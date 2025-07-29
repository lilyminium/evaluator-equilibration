import json
import hashlib

from openff.evaluator.utils.serialization import TypedJSONEncoder
from openff.evaluator.datasets import PhysicalProperty, PropertyPhase
from openff.evaluator.properties.properties import EstimableExcessProperty
from openff.evaluator.properties import EnthalpyOfVaporization
from openff.evaluator.substances import Substance
from openff.evaluator.utils.serialization import TypedBaseModel


from openff.interchange.components._packmol import UNIT_CUBE, pack_box
from openff.toolkit import Molecule, ForceField, Topology
from openff.units import unit


class ConsistentHashableData:
    def __init__(
        self,
        substance: Substance,
        n_molecules: int,
        max_molecules: int,
        thermodynamic_state,
        property_phase: PropertyPhase,
    ):
        self.substance = substance
        self.n_molecules = n_molecules
        self.max_molecules = max_molecules
        self.thermodynamic_state = thermodynamic_state
        self.property_phase = property_phase
    

    def __hash__(self):
        obj = {
            "substance": self.substance,
            "n_molecules": self.n_molecules,
            "max_molecules": self.max_molecules,
            "thermodynamic_state": self.thermodynamic_state,
            "property_phase": self.property_phase,
        }
        serialized = json.dumps(obj, sort_keys=True, cls=TypedJSONEncoder)

        return int(hashlib.sha256(serialized.encode("utf-8")).hexdigest(), 16)


class PropertyBox(TypedBaseModel):
    """
    A box containing a substance and its associated properties for equilibration.
    """
    def __init__(
        self,
        substance=None,
        n_molecules: int=None,
        thermodynamic_state=None,
        property_phase=None,
    ):
        self.substance = substance
        self.n_molecules = n_molecules
        self.thermodynamic_state = thermodynamic_state
        self.phase = property_phase

    def __setstate__(self, state):
        self.substance = state["substance"]
        self.n_molecules = state["n_molecules"]
        self.thermodynamic_state = state["thermodynamic_state"]
        self.phase = state["phase"]

    def __getstate__(self):
        return {
            "substance": self.substance,
            "n_molecules": self.n_molecules,
            "thermodynamic_state": self.thermodynamic_state,
            "phase": self.phase,
        }


    def __repr__(self):
        return (
            f"PropertyBox(substance={self.substance}, "
            f"n_molecules={self.n_molecules}, "
            f"thermodynamic_state={self.thermodynamic_state}, "
            f"phase={self.phase})"
        )


    def to_topology(self) -> Topology:
        """ Convert the PropertyBox to an OpenFF Topology."""
        n_molecules = self.substance.get_molecules_per_component(
            self.max_molecules
        )
        molecules = []
        counts = []
        for component in self.substance.components:
            mol = Molecule.from_smiles(component.smiles)
            mol.generate_conformers(n_conformers=1)
            molecules.append(mol)
            counts.append(n_molecules[component.identifier])

        top = pack_box(
            molecules,
            counts,
            target_density=0.95 * unit.grams / unit.milliliters,
            box_shape=UNIT_CUBE,
            retain_working_files=False,
        )
        return top
    

    @classmethod
    def from_physical_property(
        cls,
        physical_property: PhysicalProperty,
        n_molecules: int = 1000,
    ) -> list["PropertyBox"]:
        substance = physical_property.substance.to_substance_n_molecules(
            n_molecules,
        )
        substances = [substance]

        # going to hard-code this
        # because it's hard to figure out replicators
        if isinstance(physical_property, EstimableExcessProperty):
            for component in physical_property.substance.components:
                component_substance = Substance.from_components(component)
                substances.append(
                    component_substance.to_substance_n_molecules(
                        n_molecules,
                    )
                )
    
        # one is gas, one is liquid
        if isinstance(physical_property, EnthalpyOfVaporization):
            return [
                cls(
                    substance,
                    n_molecules,
                    physical_property.thermodynamic_state,
                    PropertyPhase.Liquid
                ),
                cls(
                    substance,
                    n_molecules,
                    physical_property.thermodynamic_state,
                    PropertyPhase.Gas
                )
            ]

        return [
            cls(
                sub,
                n_molecules,
                physical_property.thermodynamic_state,
                physical_property.phase,
            )
            for sub in substances
        ]

    def __hash__(self) -> int:
        return hash(
            ConsistentHashableData(
                self.substance,
                self.n_molecules,
                self.n_molecules,
                self.thermodynamic_state,
                self.phase,
            )
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PropertyBox):
            return NotImplemented
        return hash(self) == hash(other)
    
    def _get_storage_key(self) -> str:
        """Generate a storage key for the property box."""
        return "u_" + str(hash(self))
    