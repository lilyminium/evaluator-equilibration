"""
This script sets up the equilibration of amine properties by creating boxes
from a dataset of physical properties. It checks for existing boxes in the
storage and only creates boxes for properties that are not already present.
"""

import pathlib

import click
import tqdm

from openff.evaluator.datasets.datasets import PhysicalPropertyDataSet

from eveq.storage.storage import LocalStoredEquilibrationData
from eveq.box.box import PropertyBox


@click.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default="dataset.json",
    help="Path to the input dataset JSON file.",
)
@click.option(
    "--storage",
    "-s",
    "existing_storage_path",
    type=click.Path(exists=True, dir_okay=True, readable=True),
    default="../../data/stored_data",
    help="Path to the existing storage directory.",
)
@click.option(
    "--working-directory",
    "-w",
    "working_directory",
    type=click.Path(file_okay=False, writable=True),
    default="working_directory",
    help="Path to the working directory where boxes will be created.",
)
def main(
    input_path: str = "dataset.json",
    existing_storage_path: str = "../../data/stored_data",
    working_directory: str = "working_directory",
):
    
    working_directory = pathlib.Path(working_directory)
    working_directory.mkdir(parents=True, exist_ok=True)


    dataset = PhysicalPropertyDataSet.from_json(input_path)

    storage = LocalStoredEquilibrationData(existing_storage_path)

    all_boxes = [
        box
        for physical_property in dataset.properties
        for box in PropertyBox.from_physical_property(physical_property, n_molecules=1000)
    ]
    print(f"Found {len(all_boxes)} boxes in dataset.")
    boxes = set(all_boxes)
    print(f"Found {len(boxes)} unique boxes in dataset.")

    boxes = [
        box
        for box in boxes
        if not box._get_storage_key() in storage._cached_retrieved_objects
    ]
    print(f"Found {len(boxes)} boxes not in storage, setting up.")

    box_directory = working_directory / "boxes"
    box_directory.mkdir(parents=True, exist_ok=True)
    unique_boxes = []
    for box in tqdm.tqdm(boxes):
        box_file = box_directory / f"{box._get_storage_key()}.json"
        box.json(box_file, format=True)
        unique_boxes.append(str(box_file))

if __name__ == "__main__":
    main()
