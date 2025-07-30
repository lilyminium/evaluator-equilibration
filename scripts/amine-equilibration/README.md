# Equilibrating amine properties

This directory contains code for equilibrating additional amine properties for the ash-sage-rc2 re-fit.

The scripts here:

* `subset-amine-properties.py` selects the amine properties that need equilibration and don't already exist in the data storage, saving Evaluator PhysicalPropertyDatasets to `dataset.json` and `dataset.csv`
* `set-up-equilibration.py` sets up boxes for each property in the `working_directory/boxes` directory. 