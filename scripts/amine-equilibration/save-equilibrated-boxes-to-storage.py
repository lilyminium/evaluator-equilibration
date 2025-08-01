import pathlib

import click
import tqdm

from eveq.storage.storage import LocalStoredEquilibrationData
from openff.evaluator.utils.serialization import TypedBaseModel


@click.command()
@click.option(
    "--input-path",
    "-i",
    "input_path",
    type=click.Path(exists=True, dir_okay=True, readable=True),
    default="working_directory/equilibration/",
    help="Path to the input directory containing equilibration data files.",
)
@click.option(
    "--storage-path",
    "-s",
    "storage_path",
    type=click.Path(exists=True, dir_okay=True, writable=True),
    default="../../data/stored_data",
    help="Path to the existing storage directory where data will be saved.",
)
@click.option(
    "--force-field-id-placeholder",
    "-ffid",
    "force_field_id_placeholder",
    type=str,
    default="ForceFieldData_2803685782293237796",
    help=(
        "Placeholder for the force field ID to be used in the stored data. "
        "This is manually replaced with the ID of an existing version of openff-2.1.0 right now."
    ),
)
def main(
    input_path: str = "working_directory/equilibration/",
    storage_path: str = "../../data/stored_data",
    force_field_id_placeholder: str = "ForceFieldData_2803685782293237796"
):
    input_directory = pathlib.Path(input_path)
    data_files = sorted(input_directory.glob("*/stored_equilibration_data.json"))
    print(f"Found {len(data_files)} equilibration data files in {input_directory}")

    storage = LocalStoredEquilibrationData(storage_path)
    print(f"Original number of objects in storage: {len(storage._cached_retrieved_objects)}")

    for data_file in tqdm.tqdm(data_files):
        object_to_store = TypedBaseModel.from_json(data_file)
        object_to_store.force_field_id = force_field_id_placeholder
        object_to_store.coordinate_file_name = "output.pdb"
        ancillary_data_path = data_file.parent / "output"
        storage.store_object(object_to_store, str(ancillary_data_path))

    print(f"Final number of objects in storage: {len(storage._cached_retrieved_objects)}")



if __name__ == "__main__":
    main()
