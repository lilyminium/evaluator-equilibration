import logging
import pathlib
import shutil
import json

from eveq.box.box import PropertyBox
import pandas as pd

import openmm
import red

from openff.evaluator.utils.serialization import TypedJSONEncoder
from openff.evaluator.forcefield.forcefield import SmirnoffForceFieldSource
from openff.evaluator.storage.data import StoredEquilibrationData, ForceFieldData
from openff.toolkit import Molecule, ForceField, Topology
from openff.interchange import Interchange
from openff.units import unit
from openff.units.openmm import from_openmm

logger = logging.getLogger(__name__)

class EquilibrationSystem:

    def __init__(
        self,
        box: PropertyBox,
        forcefield: ForceField,
        working_directory: str,
        max_iterations: int=2000
    ):
        self.box = box
        if isinstance(forcefield, str):
            forcefield = ForceField(forcefield)

        self.forcefield = forcefield
        # 2000 * 200 ps = 400 ns
        self.max_iterations = max_iterations
        
        working_directory = pathlib.Path(working_directory) / box._get_storage_key()
        working_directory.mkdir(parents=True, exist_ok=True)
        self.working_directory = working_directory

        self.interchange_file = self.working_directory / "interchange.json"
        self.input_file = self.working_directory / "input_packed_box.pdb"
        self.minimized_file = self.working_directory / "minimized_box.pdb"
        self.statistics_file = self.working_directory / "openmm_statistics.csv"
        self.tmp_statistics_file = self.working_directory / "tmp_openmm_statistics.csv"
        self.checkpoint_file = self.working_directory / "checkpoint.xml"
        self.equilibrated_file = self.working_directory / "equilibrated_box.pdb"
        self.output_file = self.working_directory / "stored_equilibration_data.json"

        self._load_current_state()

        # easy defaults
        self.pressure = box.thermodynamic_state.pressure.to_openmm()
        self.temperature = box.thermodynamic_state.temperature.to_openmm()
        self.timestep = 2.0 * unit.femtosecond
        self.csv_columns = [
            "Step",
            "Potential Energy (kJ/mole)", "Kinetic Energy (kJ/mole)", "Total Energy (kJ/mole)",
            "Temperature (K)", "Box Volume (nm^3)", "Density (g/mL)", "Speed (ns/day)"
        ]

    def _load_current_state(self):
        if self.interchange_file.exists():
            self.interchange = Interchange.parse_file(self.interchange_file)
        else:
            self.interchange = None

    def pack_initial_box(self):
        topology = self.box.to_topology()
        interchange = self.forcefield.create_interchange(topology)
        interchange.to_pdb(self.input_file)
        self.interchange = interchange
        self.save_interchange()

    def run_all(self):
        """
        Run the entire equilibration protocol.
        """
        self.pack_initial_box()
        logger.info(f"Packed box saved to: {self.input_file}")
        self.minimize()
        logger.info(f"Minimized box saved to: {self.minimized_file}")
        self.equilibrate()
        logger.info(f"Equilibrated box saved to: {self.equilibrated_file}")


    def save_interchange(self):
        if self.interchange is None:
            raise ValueError("Interchange not initialized. Call pack_initial_box first.")
        with open(self.interchange_file, "w") as f:
            f.write(self.interchange.json())


    def minimize(self):
        if self.interchange is None:
            raise ValueError("Interchange not initialized. Call pack_initial_box first.")

        # Evaluator defaults
        self.interchange.minimize(
            force_tolerance=10 * unit.kilojoules_per_mole / unit.nanometer,
            max_iterations=0
        )
        self.interchange.to_pdb(self.minimized_file)
        self.save_interchange()


    def _create_integrator(self):
        integrator = openmm.LangevinMiddleIntegrator(
            self.temperature,
            (1.0 / unit.picoseconds).to_openmm(),
            self.timestep.to_openmm()
        )
        return integrator
    

    def equilibrate_step(self, filename):
        from openmmtools.utils import get_fastest_platform
        
        platform = get_fastest_platform()
        logger.info(f"Using platform: {platform.getName()}")

        barostat = openmm.MonteCarloBarostat(
            self.pressure,
            self.temperature,
            25,
        )

        simulation = self.interchange.to_openmm_simulation(
            integrator=self._create_integrator(),
            platform=platform,
            combine_nonbonded_forces=True,
            additional_forces=[barostat],
        )

        # load any existing checkpoint
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, "r") as file:
                current_state = openmm.XmlSerializer.deserialize(file.read())
            simulation.context.setState(current_state)

        # copy over statistics file to avoid accidental overwrites
        if self.statistics_file.exists():
            shutil.copy(self.statistics_file, self.tmp_statistics_file)

        statistics_reporter = openmm.app.StateDataReporter(
            str(self.tmp_statistics_file.resolve()),
            1000, # every 2 ps
            step=True,
            potentialEnergy=True,
            kineticEnergy=True,
            totalEnergy=True,
            temperature=True,
            volume=True,
            density=True,
            speed=True,
            append=True,
        )
        simulation.context.setVelocitiesToTemperature(self.temperature)
        simulation.reporters.append(statistics_reporter)

        # simulate for 200 ps
        steps_per_iteration = 100000
        simulation.step(steps_per_iteration)

        state = simulation.context.getState(getPositions=True, getEnergy=True)
        self.interchange.positions = from_openmm(state.getPositions(asNumpy=True))

        self.save_interchange()
        self.interchange.to_pdb(filename)

        shutil.copy(self.tmp_statistics_file, self.statistics_file)
        
        # save checkpoint
        state = simulation.context.getState(
            getPositions=True,
            getEnergy=True,
            getVelocities=True,
            getForces=True,
            getParameters=True,
            enforcePeriodicBox=True,
        )

        with open(self.checkpoint_file, "w") as file:
            file.write(openmm.XmlSerializer.serialize(state))


    def equilibrate(self):
        if self.interchange is None:
            raise ValueError("Interchange not initialized. Call pack_initial_box first.")

        existing_equilibration_files = sorted(self.working_directory.glob("equilibrated_box*.pdb"))
        n_eq_files = len(existing_equilibration_files)
        
        equilibrated = False
        while not equilibrated and n_eq_files < self.max_iterations:
            next_file = self.working_directory / f"equilibrated_box_{n_eq_files + 1}.pdb"

            logger.info(f"Starting equilibration step {n_eq_files + 1}")

            self.equilibrate_step(next_file)
            equilibrated = self.evaluate_equilibration()

            existing_equilibration_files = sorted(self.working_directory.glob("equilibrated_box*.pdb"))
            n_eq_files = len(existing_equilibration_files)

        if not equilibrated:
            logger.warning(f"Equilibration did not converge after {self.max_iterations} iterations.")

        existing_equilibration_files = sorted(self.working_directory.glob("equilibrated_box*.pdb"))
        shutil.copy(existing_equilibration_files[-1], self.equilibrated_file)

        obj = self.to_stored_equilibration_data()
        with open(self.output_file, "w") as f:
            json.dump(obj, f, cls=TypedJSONEncoder)

        

    def evaluate_equilibration(self) -> bool:
        df = pd.read_csv(self.statistics_file, names=self.csv_columns)

        # detect equilibration based on Potential Energy and Density

        potential_energy = df['Potential Energy (kJ/mole)'].values
        density = df['Density (g/mL)'].values

        return (
            self._evaluate_timeseries_equilibration(potential_energy) and
            self._evaluate_timeseries_equilibration(density)
        )
    
    def _get_equilibration_attributes(self, data):
        # employ all methods available in RED... 
        # Chodera's is likely the most influential as it selects the latest points
        # but this is more automated

        print(data)

        equilibration_indices = []
        statistical_inefficiencies = []
        effective_sample_sizes = []

        # window
        idx, g, ess = red.detect_equilibration_window(
            data, method="min_sse", plot=True,
            plot_name = self.working_directory / "equilibration_window.png"
        )
        equilibration_indices.append(idx)
        statistical_inefficiencies.append(g)
        effective_sample_sizes.append(ess)

        # geyer
        idx, g, ess = red.detect_equilibration_init_seq(
            data, method="min_sse", plot=True,
            plot_name = self.working_directory / "equilibration_geyer.png",
        )
        equilibration_indices.append(idx)
        statistical_inefficiencies.append(g)
        effective_sample_sizes.append(ess)

        # choderas
        idx, g, ess = red.detect_equilibration_init_seq(
              data, method="max_ess", sequence_estimator="positive",
              plot=True,
              plot_name = self.working_directory / "equilibration_chodera.png",
        )
        equilibration_indices.append(idx)
        statistical_inefficiencies.append(g)
        effective_sample_sizes.append(ess)

        min_ess = min(effective_sample_sizes)
        max_idx = max(equilibration_indices)
        max_inefficiency = max(statistical_inefficiencies)

        return max_idx, max_inefficiency, min_ess



    def _evaluate_timeseries_equilibration(self, data, n_required_samples: int = 50) -> bool:
        """
        Evaluate the equilibration of a timeseries data

        Parameters
        ----------
        data : np.ndarray
            The timeseries data to evaluate.
        n_required_samples : int, optional
            The number of required samples to consider the system equilibrated, by default 50.
            50 samples is at minimum 100 ps data

        Returns
        -------
        bool
            True if the system is equilibrated, False otherwise.
        """

        max_idx, max_inefficiency, min_ess = self._get_equilibration_attributes(data)
        logger.info(f"Minimum ESS: {min_ess}; Maximum Index: {max_idx}; Maximum Statistical Inefficiency: {max_inefficiency}")

        if min_ess < n_required_samples:
            return False
        return True
    
    def get_force_field_id(self):
        source = SmirnoffForceFieldSource.from_object(self.forcefield)
        data = ForceFieldData(force_field_source=source)
        return "ff_" + str(hash(data))


    def to_stored_equilibration_data(self):
        df = pd.read_csv(self.statistics_file, names=self.csv_columns)
        equilibration_attrs = [
            self._get_equilibration_attributes(df['Potential Energy (kJ/mole)'].values),
            self._get_equilibration_attributes(df['Density (g/mL)'].values)
        ]
        statistical_inefficiency = max([attr[1] for attr in equilibration_attrs])

        obj = StoredEquilibrationData(
            substance=self.box.substance,
            thermodynamic_state=self.box.thermodynamic_state,
            property_phase=self.box.phase,
            source_calculation_id="eveq",
            force_field_id=self.get_force_field_id(),
            coordinate_file_name=str(self.equilibrated_file.resolve()),
            statistical_inefficiency=statistical_inefficiency,
            number_of_molecules=self.interchange.topology.n_molecules,
            max_number_of_molecules=self.box.n_molecules,
            calculation_layer="EquilibrationLayer"
        )
        return obj
