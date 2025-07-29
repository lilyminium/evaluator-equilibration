# Dev Installation

To build Evaluator Equilibration from source, we highly recommend using virtual environments. If possible, we strongly recommend that you use [Anaconda](https://docs.conda.io/en/latest/) as your package manager.

Ensure that you have [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed.

First, download the repository from GitHub:

```shell
git clone https://github.com/lilyminium/evaluator-equilibration.git
cd evaluator-equilibration
```

Create a virtual environment named `evaluator-equilibration-dev`, install the development and documentation dependencies, and activate the environment:

```shell
conda env create --name evaluator-equilibration-dev --file devtools/conda-envs/test_env.yaml
conda env update --name evaluator-equilibration-dev --file devtools/conda-envs/docs_env.yaml
conda activate evaluator-equilibration-dev
```

The environment will be deactivated when the shell session is closed, but it can always be reactivated with `conda activate evaluator-equilibration-dev`. Next, install the package in development mode into the activated environment:

```shell
pip install -e .
```

To keep the environment safe, consistent, and able to be updated, it is helpful to constrain the environment to prefer packages in Conda Forge to those from the default channels: 

```shell
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict 
```

If you want to update your dependencies (which can be risky if you have a mixed-channel environment), delete and rebuild the environment or run:

```shell
conda update -c conda-forge --name evaluator-equilibration-dev --all
```
