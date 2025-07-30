"""
This script selects amine properties from an existing dataset and checks which ones
are not yet equilibrated. It saves the non-equilibrated properties to a new dataset file
for further processing.
"""

import click

import pandas as pd

from eveq.storage.storage import LocalStoredEquilibrationData

from openff.evaluator.datasets.datasets import PhysicalPropertyDataSet
from openff.evaluator.datasets.curation.components import filtering, selection, thermoml
from openff.evaluator.datasets.curation.components.selection import State, TargetState
from openff.evaluator.datasets.curation.workflow import (
    CurationWorkflow,
    CurationWorkflowSchema,
)

from openff.evaluator.utils.checkmol import ChemicalEnvironment, analyse_functional_groups
from eveq.storage.storage import PropertyBox


@click.command()
@click.option(
    "--existing-storage-path",
    "-esp",
    "existing_storage_path",
    type=click.Path(exists=True, dir_okay=True, readable=True),
    default="../../data/stored_data",
    help="Path to the existing storage directory.",
)
@click.option(
    "--intermediate-csv-path",
    "-icp",
    "intermediate_csv_path",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default="/Users/lily/pydev/old-ash-sage/01_download-data/physprop/intermediate/output/initial-filtered.csv",
    help=(
        "Path to the intermediate CSV file containing filtered properties. "
        "This file is from the ash-sage-rc1 dataset."
    )
)
def main(
    existing_storage_path: str = "../../data/stored_data",
    intermediate_csv_path: str = "/Users/lily/pydev/old-ash-sage/01_download-data/physprop/intermediate/output/initial-filtered.csv",
):
    storage = LocalStoredEquilibrationData(existing_storage_path)
    print(f"Number of objects in storage: {len(storage._cached_retrieved_objects)}")

    # load existing intermediate filtered set
    df = pd.read_csv(
        intermediate_csv_path,
        index_col=0
    )
    df["Id"] = df["Id"].astype(str)


    # the FilterByEnvironments filter is too strict -- all components have to match amines.
    cols = [x for x in df.columns if x.startswith("Component")]
    amine_property_rows = []
    for _, row in df.iterrows():
        components = []
        for col in cols:
            if not pd.isna(row[col]):
                components.append(row[col])

        for comp in components:
            groups = [gp.value for gp in analyse_functional_groups(comp)]
            if any("Amine" in x for x in groups):
                amine_property_rows.append(dict(row))
                break

    amine_properties = pd.DataFrame(amine_property_rows)

    print(
        f"{len(amine_properties)} amine properties found"
    )

    amine_dataset = PhysicalPropertyDataSet.from_pandas(amine_properties)

    not_equilibrated = []
    for physical_property in amine_dataset.properties:
        if not storage.contains_all_property_boxes(physical_property):
            not_equilibrated.append(physical_property)

    print(
        f"{len(not_equilibrated)} properties not equilibrated"
    )

    non_equilibrated_amines = PhysicalPropertyDataSet()
    non_equilibrated_amines.add_properties(*not_equilibrated)
    with open("dataset.json", "w") as f:
        f.write(non_equilibrated_amines.json())

    non_equilibrated_amines_df = non_equilibrated_amines.to_pandas()
    non_equilibrated_amines_df.to_csv("dataset.csv")


if __name__ == "__main__":
    main()
