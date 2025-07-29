import pathlib
import json
import logging
import shutil

from openff.evaluator.storage.storage import StorageBackend
from openff.evaluator.storage import LocalFileStorage
from openff.evaluator.datasets.datasets import PhysicalProperty, PhysicalPropertyDataSet
from openff.evaluator.storage.data import (
    BaseStoredData,
    ForceFieldData,
    HashableStoredData,
    ReplaceableData,
    StoredEquilibrationData
)


from openff.evaluator.utils.serialization import TypedJSONEncoder
from eveq.box.box import ConsistentHashableData, PropertyBox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




class LocalStoredEquilibrationData(LocalFileStorage):
    """
    A local storage backend for storing equilibration data.
    """

    def _hash_equilibration_data(self, equilibration_data: StoredEquilibrationData) -> int:
        """Hash the equilibration data to create a unique key."""
        assert isinstance(equilibration_data, StoredEquilibrationData), (
            "The provided equilibration data must be an instance of StoredEquilibrationData."
        )
        return hash(
            ConsistentHashableData(
                equilibration_data.substance,
                equilibration_data.number_of_molecules,
                equilibration_data.max_number_of_molecules,
                equilibration_data.thermodynamic_state,
                equilibration_data.property_phase,
            )
        )

    def _get_storage_key(self, equilibration_data: StoredEquilibrationData) -> str:
        """Generate a storage key for the equilibration data."""
        return "u_" + str(self._hash_equilibration_data(equilibration_data))

    @classmethod
    def from_localfilestorage(
        cls,
        lfs_root_directory: str | pathlib.Path = "old_stored_data",
        new_root_directory: str | pathlib.Path = "stored_data",
    ):
        lfs = LocalFileStorage(lfs_root_directory, cache_objects_in_memory=True)

        lsed = cls(new_root_directory)
        storage_objects: dict[str, tuple[StoredEquilibrationData, str]] = {}

        for old_storage_key, (stored_object, data_path) in lfs._cached_retrieved_objects.items():
            if isinstance(stored_object, StorageBackend._ObjectKeyData):
                # Skip object key data, as it is not relevant for equilibration data.
                continue
            if not isinstance(stored_object, StoredEquilibrationData):
                lsed.store_object(
                    stored_object,
                    ancillary_data_path=data_path,
                )
                continue
            new_storage_key = lsed._get_storage_key(stored_object)
            # if object already exists, compare statistical inefficiencies
            if new_storage_key in storage_objects:
                existing_object = storage_objects[new_storage_key]
                if existing_object.statistical_inefficiency < stored_object.statistical_inefficiency:
                    continue  # skip the new object if the old one is better
            storage_objects[new_storage_key] = (stored_object, data_path)

        # copy over all objects to the new storage
        for storage_key, (stored_object, data_path) in storage_objects.items():
            lsed._store_object(
                stored_object,
                storage_key=storage_key,
                ancillary_data_path=data_path,
            )
            object_class = stored_object.__class__
            lsed._stored_object_keys[object_class.__name__].append(storage_key)
            lsed._save_stored_object_keys()
        return lsed

    def __init__(
        self,
        root_directory: str | pathlib.Path ="stored_data",
    ):
        root_directory = str(root_directory)
        super().__init__(
            root_directory=root_directory,
            cache_objects_in_memory=True,
        )

    def update(self, other):
        """Update the storage with new equilibration data."""
        assert isinstance(other, LocalStoredEquilibrationData), (
            "The provided object must be an instance of LocalStoredEquilibrationData."
        )

        n_existing_objects = len(self._cached_retrieved_objects)
        logger.info(
            f"Updating storage with {len(other._cached_retrieved_objects)} new objects. "
            f"Currently, there are {n_existing_objects} objects in the storage."
        )
        
        for storage_key, (object_to_store, ancillary_data_path) in other._cached_retrieved_objects.items():
            if storage_key in self._cached_retrieved_objects:
                existing_object, _ = self._cached_retrieved_objects[storage_key]
                if existing_object.statistical_inefficiency < object_to_store.statistical_inefficiency:
                    logger.info(
                        f"Skipping {storage_key} as it already exists with a lower statistical inefficiency."
                    )
                    continue
            self.store_object(
                object_to_store,
                storage_key=storage_key,
                ancillary_data_path=ancillary_data_path,
            )
            # object_class = object_to_store.__class__
            # self._stored_object_keys[object_class.__name__].append(storage_key)
            # self._save_stored_object_keys()

        n_final_objects = len(self._cached_retrieved_objects)
        logger.info(
            f"Storage updated. Now contains {n_final_objects} objects."
        )

    def _store_object(
        self, object_to_store, storage_key=None, ancillary_data_path=None
    ):
        root = pathlib.Path(self._root_directory)
        file_path = root / f"{storage_key}.json"
        directory_path = root / f"{storage_key}"

        with open(file_path, "w") as file:
            json.dump(object_to_store, file, cls=TypedJSONEncoder)

        if object_to_store.has_ancillary_data():
            shutil.copytree(ancillary_data_path, directory_path, dirs_exist_ok=True)

        self._cached_retrieved_objects[storage_key] = (
            object_to_store,
            directory_path,
        )

    def store_object(self, object_to_store, ancillary_data_path=None):
        """Store an object in the storage system, returning the key
        of the stored object. This may be different to `storage_key`
        depending on whether the same or a similar object was already
        present in the system.

        Parameters
        ----------
        object_to_store: BaseStoredData
            The object to store.
        ancillary_data_path: str, optional
            The data path to the ancillary directory-like
            data to store alongside the object if the data
            type requires one.

        Returns
        -------
        str
            The unique key assigned to the stored object.
        """

        # Make sure the object is valid.
        if object_to_store is None:
            raise ValueError("The object to store cannot be None.")

        object_to_store.validate()

        # Make sure the object is a supported type.
        if not isinstance(object_to_store, BaseStoredData):
            raise ValueError(
                "Only objects inheriting from `BaseStoredData` can "
                "be stored in the storage system."
            )

        # Make sure we have ancillary data if required.
        object_class = object_to_store.__class__

        if object_class.has_ancillary_data() and ancillary_data_path is None:
            raise ValueError("This object requires ancillary data.")

        # Check whether the exact same object already exists within
        # the storage system based on its hash.
        storage_key = self.has_object(object_to_store)

        if storage_key is not None:
            if not isinstance(object_to_store, ReplaceableData):
                # Handle the case where the existing data
                # should be returned, rather than storing
                # the passed object.
                return storage_key

            existing_object, _ = self.retrieve_object(storage_key, ReplaceableData)

            # noinspection PyTypeChecker
            object_to_store = object_to_store.most_information(
                existing_object, object_to_store
            )

            if object_to_store is None:
                raise ValueError(
                    "Something went wrong when trying to "
                    "determine whether the object trying to "
                    "be stored is redundant."
                )

            elif object_to_store == existing_object:
                # Don't try to re-store the existing object.
                return storage_key

        else:
            # Generate a unique id for this object.
            while storage_key is None or not self._is_key_unique(storage_key):
                if isinstance(object_to_store, HashableStoredData):
                    # Use the hash of the object to generate a unique key.
                    _hash = str(hash(object_to_store))
                    clsname = object_class.__name__
                    storage_key = f"{clsname}_{_hash}"
                else:
                    storage_key = self._get_storage_key(object_to_store)

        # Hash this object if appropriate
        if isinstance(object_to_store, HashableStoredData):
            self._object_hashes[hash(object_to_store)] = storage_key

        # Save the object into the storage system with the given key.
        with self._lock:
            self._store_object(object_to_store, storage_key, ancillary_data_path)

        # Register the key in the storage system.
        if (
            not isinstance(object_to_store, StorageBackend._ObjectKeyData)
            and storage_key not in self._stored_object_keys[object_class.__name__]
        ):
            self._stored_object_keys[object_class.__name__].append(storage_key)
            self._save_stored_object_keys()

        return storage_key

    def contains_all_property_boxes(
        self,
        physical_property: PhysicalProperty,
        n_molecules: int = 1000,
    ) -> bool:
        """Check if all property boxes for a given physical property are stored.
        
        Parameters
        ----------
        physical_property : PhysicalProperty
            The physical property for which to check the stored property boxes.
            
        n_molecules : int, optional
            The number of molecules to consider for the property boxes, by default 1000.

        Returns
        -------
        bool
            True if all property boxes for the given physical property are stored, False otherwise.
            If False, you will need to equilibrate and store the property boxes before retrieving them.
        """
        boxes = PropertyBox.from_physical_property(
            physical_property,
            n_molecules=n_molecules,
        )
        for box in boxes:
            key = box._get_storage_key()
            if key not in self._cached_retrieved_objects:
                return False
        return True
