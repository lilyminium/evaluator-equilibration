import pathlib

import click
import tqdm


from openff.evaluator.utils.serialization import TypedBaseModel
from eveq.box.box import PropertyBox
from eveq.protocols.equilibration import EquilibrationSystem

@click.command()
@click.option(
    "--index",
    "-i",
    "index",
    type=int,
    default=0,
    help="Index of the box to equilibrate.",
)
@click.option(
    "--box-directory",
    "-bd",
    "box_directory",
    type=click.Path(exists=True, dir_okay=True, readable=True),
    default="working_directory/boxes",
    help="Path to the directory containing box files.",
)
@click.option(
    "--working-directory",
    "-wd",
    "working_directory",
    type=click.Path(file_okay=False, writable=True),
    default="working_directory/equilibration",
    help="Path to the working directory for equilibration.",
)
@click.option(
    "--forcefield",
    "-ff",
    "forcefield",
    type=str,
    default="openff-2.1.0.offxml",
    help="Path to the force field file.",
)
@click.option(
    "--max-iterations",
    "-maxiter",
    "max_iterations",
    type=int,
    default=2000,
    help="Maximum number of iterations for equilibration.",
)
def main(
    index: int = 0,
    box_directory: str = "working_directory/boxes",
    working_directory: str = "working_directory/equilibration",
    forcefield: str = "openff-2.1.0.offxml",
    max_iterations: int = 2000,
):
    
    box_directory = pathlib.Path(box_directory)
    working_directory = pathlib.Path(working_directory)
    
    working_directory.mkdir(parents=True, exist_ok=True)

    boxes = sorted(box_directory.glob("u*.json"))
    box_file = boxes[index]

    print(f"Working with box: {box_file.name}")

    box = PropertyBox.from_json(box_file)
    print(box)

    system = EquilibrationSystem(
        box=box,
        forcefield=forcefield,
        working_directory=working_directory,
        max_iterations=max_iterations,
    )

    system.run_all()


if __name__ == "__main__":
    main()
