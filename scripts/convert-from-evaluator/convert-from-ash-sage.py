import click
from eveq.storage.storage import LocalStoredEquilibrationData


@click.command()
@click.option(
    "--lfs-root-directory",
    "-lfs",
    "lfs_root_directory",
    type=click.Path(exists=True, dir_okay=True, readable=True),
    default="/Volumes/Nobbsy/combined_equilibration_data/stored_data",
    help=(
        "Path to the root directory of an existing LocalFileStorage. "
        "The default path here is from the equilibration of ash-sage-rc1."
    )
)
@click.option(
    "--new-root-directory",
    "-nrd",
    "new_root_directory",
    type=click.Path(file_okay=False, writable=True),
    default="../../data/stored_data",
    help=(
        "Path to the new root directory for the LocalStoredEquilibrationData. "
        "This will be created if it does not exist. "
        "The default path here is to the repo data storage"
    )
)
def main(
    lfs_root_directory: str = "/Volumes/Nobbsy/combined_equilibration_data/stored_data",
    new_root_directory: str = "../data/stored_data",
):
    storage = LocalStoredEquilibrationData.from_localfilestorage(
        lfs_root_directory=lfs_root_directory,
        new_root_directory=new_root_directory
    )
    print(len(storage._cached_retrieved_objects))


if __name__ == "__main__":
    main()
