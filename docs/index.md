# Evaluator Equilibration

A playground for applying graph convolutional networks to molecules, with a focus on learning continuous "atom-type" embeddings and from these classical molecule force field parameters.

## Getting started

OpenFF recommends using Conda virtual environments for all scientific Python work. Evaluator Equilibration can be installed into a new Conda environment named `evaluator-equilibration` with the [`evaluator-equilibration`] package:

```shell
mamba create -n evaluator-equilibration -c conda-forge evaluator-equilibration
conda activate evaluator-equilibration
```

For more information on installing Evaluator Equilibration, see [](installation.md).

Evaluator Equilibration can then be imported from the [`evaluator_equilibration`] module:

```python
import evaluator_equilibration
```

Or executed from the command line:

```shell
evaluator-equilibration --help
```

[`evaluator-equilibration`]: https://anaconda.org/conda-forge/evaluator-equilibration
[`evaluator_equilibration`]: evaluator_equilibration

(inference)=
## Inference with Evaluator Equilibration

Evaluator Equilibration GNN models are used via the [`evaluator_equilibration.GNNModel`] class. A checkpoint file produced by Evaluator Equilibration can be loaded with the [`GNNModel.load()`] method:

```python
from evaluator_equilibration import GNNModel

model = GNNModel.load("trained_model.pt")
```

Then, the properties the model is trained to predict can be computed with the [`GNNModel.compute_properties()`] method, which takes an OpenFF [`Molecule`] object:

```python
from openff.toolkit import Molecule

ethanol = Molecule.from_smiles("CCO")

model.compute_property(ethanol)
```

[`evaluator_equilibration.GNNModel`]: evaluator_equilibration.GNNModel
[`GNNModel.load()`]: evaluator_equilibration.GNNModel.load
[`GNNModel.compute_properties()`]: evaluator_equilibration.GNNModel.compute_properties
[`Molecule`]: openff.toolkit.topology.Molecule

:::{toctree}
---
hidden: true
---

Overview <self>
installation.md
theory.md
designing.md
training.md
examples.md
:::

:::{toctree}
---
hidden: true
caption: Developer's Guide
---

CHANGELOG.md
dev.md
toolkit_wrappers.md
:::

:::{toctree}
---
hidden: true
caption: CLI Reference
---

cli.md
:::


<!--
The autosummary directive renders to rST,
so we must use eval-rst here
-->
```{eval-rst}
.. raw:: html

    <div style="display: None">

.. autosummary::
   :recursive:
   :caption: API Reference
   :toctree: api/generated
   :nosignatures:

   evaluator_equilibration

.. raw:: html

    </div>
```
