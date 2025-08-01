# Installation

OpenFF recommends using Conda virtual environments for all scientific Python work. 

<!-- Evaluator Equilibration can be installed automatically from the open source [Conda Forge] channel; if you do not yet have Conda, we recommend installing the [MambaForge] distribution, which includes the faster Mamba package manager and is pre-configured to work with Conda Forge. Mamba is a drop-in replacement for the package management functions of Conda, and so if it is unavailable can be replaced with `conda` in all the following commands.

Evaluator Equilibration can be installed into a new Conda environment named `evaluator-equilibration` with the `evaluator-equilibration` package:

```shell
mamba create -n evaluator-equilibration -c conda-forge evaluator-equilibration
conda activate evaluator-equilibration
```

If you do not have Conda or Mamba installed, see the [OpenFF installation documentation](inv:openff.docs#install).

We recommend keeping environments minimal, and only installing packages you use together. Environments can be safely discarded when you no longer need them. This avoids dependency conflicts common to large Python environments. If you prefer, Evaluator Equilibration may be installed into the current environment:

```shell
mamba install -c conda-forge evaluator-equilibration
```

Conda environments that use packages from Conda Forge alongside packages from the default Conda channels run the risk of breaking when an installation or update is attempted. This most commonly happens when a user forgets the `-c conda-forge` switch when installing a package or updating an environment. When this happens, Conda attempts to install or update from the default channels, and may replace shared dependencies of already installed packages with incompatible versions from the default channels.

For this reason, we recommend installing Conda via [MambaForge], which uses Conda Forge for all transactions and excludes packages from the default channels unless they are unavailable in Forge. If you are using a standard Conda installation, we recommend you at minimum configure Forge environments similarly:

```shell
# Remove the --env switch to apply these settings globally
conda activate evaluator-equilibration
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict 
```

In environments with this configuration, the `-c conda-forge` switch is unnecessary. Other channels, like `psi4` and `bioconda`, can still be used in the usual way.

More information on installing OpenFF packages can be found in the [OpenFF installation documentation](inv:openff.docs#install). -->

## Installation from source

You may want to install Evaluator Equilibration from source, either because you are after an unreleased feature or to manage your own dependencies. To do so, first download the GitHub repository:

```shell
git clone https://github.com/lilyminium/evaluator-equilibration.git
cd evaluator-equilibration
```

Install the dependencies:

```shell
mamba env create --name evaluator-equilibration --file devtools/conda-envs/test_env.yaml
conda activate evaluator-equilibration
```

And then install the package itself:

```shell
python -m pip install . --no-deps
```




[Conda Forge]: https://conda-forge.org/
[MambaForge]: https://github.com/conda-forge/miniforge#mambaforge


