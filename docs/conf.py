# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/stable/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# In case the project was not installed
import os
import sys

sys.path.insert(0, os.path.abspath(".."))
import evaluator_equilibration


# -- Project information -----------------------------------------------------

project = "Evaluator Equilibration"
copyright = "2021+ Open Force Field Initiative"
author = "Open Force Field Initiative"

# The short X.Y version
version = evaluator_equilibration.__version__
# The full version, including alpha/beta/rc tags
release = evaluator_equilibration.__version__


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.autodoc_pydantic",
    "openff_sphinx_theme",
    "myst_nb",
    "sphinx_click",
]

# API docs settings
autosummary_generate = True
# Document imported items iff they're in __all__
autosummary_imported_members = False
autosummary_ignore_module_all = False
# Autosummary template configuration
autosummary_context = {
    # Modules to exclude from API docs
    "exclude_modules": [
        "evaluator_equilibration.tests",
        "evaluator_equilibration.data",
    ],
    "show_inheritance": True,
    "show_inherited_members": False,
    "show_undoc_members": True,
}

autodoc_preserve_defaults = True
autodoc_inherit_docstrings = True
autodoc_typehints_format = "short"
# Fold the __init__ or __new__ methods' signature into class documentation
autoclass_content = "class"
autodoc_class_signature = "mixed"
# Workaround for autodoc_typehints_format not working for attributes
# see https://github.com/sphinx-doc/sphinx/issues/10290#issuecomment-1079740009
python_use_unqualified_type_names = True

napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_attr_annotations = True
napoleon_custom_sections = [("attributes", "params_style")]
napoleon_use_rtype = False
napoleon_use_param = True
napoleon_use_ivar = True
napoleon_preprocess_types = True

autodoc_pydantic_model_member_order = "groupwise"
autodoc_pydantic_model_signature_prefix = "model"
autodoc_pydantic_model_show_validator_members = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_config_member = False
autodoc_pydantic_model_show_json = False
autodoc_pydantic_settings_signature_prefix = "settings"
autodoc_pydantic_settings_show_validator_members = False
autodoc_pydantic_settings_show_validator_summary = False
autodoc_pydantic_settings_show_config_summary = False
autodoc_pydantic_settings_show_config_member = False
autodoc_pydantic_field_doc_policy = "both"
autodoc_pydantic_field_list_validators = False

_python_doc_base = "https://docs.python.org/3.7"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.7", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "scikit.learn": ("https://scikit-learn.org/stable", None),
    "openmm": ("http://docs.openmm.org/latest/api-python/", None),
    "rdkit": ("https://www.rdkit.org/docs", None),
    "openeye": ("https://docs.eyesopen.com/toolkits/python/", None),
    "mdtraj": ("https://www.mdtraj.org/1.9.5/", None),
    "openff.toolkit": (
        "https://docs.openforcefield.org/projects/toolkit/en/stable/",
        None,
    ),
    "openff.interchange": (
        "https://docs.openforcefield.org/projects/interchange/en/stable/",
        None,
    ),
    "openff.units": (
        "https://docs.openforcefield.org/projects/units/en/stable/",
        None,
    ),
    "openff.bespokefit": (
        "https://docs.openforcefield.org/projects/bespokefit/en/stable/",
        None,
    ),
    "openff.qcsubmit": (
        "https://docs.openforcefield.org/projects/qcsubmit/en/stable/",
        None,
    ),
    "openff.fragmenter": (
        "https://docs.openforcefield.org/projects/fragmenter/en/stable/",
        None,
    ),
    "openff.evaluator": (
        "https://docs.openforcefield.org/projects/evaluator/en/stable/",
        None,
    ),
    "openff.recharge": (
        "https://docs.openforcefield.org/projects/recharge/en/stable/",
        None,
    ),
    "openff.docs": (
        "https://docs.openforcefield.org/en/latest/",
        None,
    ),
    "torch": ("https://pytorch.org/docs/stable/", None),
    "pytorch_lightning": (
        "https://pytorch-lightning.readthedocs.io/en/stable/",
        None,
    ),
    "dgl": ("https://docs.dgl.ai/en/latest/", None),
}
myst_url_schemes = [
    "http",
    "https",
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Extensions for the myst parser
myst_enable_extensions = [
    "dollarmath",
    "colon_fence",
    "smartquotes",
    "replacements",
    "deflist",
]
myst_heading_anchors = 3

# sphinx-notfound-page
# https://github.com/readthedocs/sphinx-notfound-page
# Renders a 404 page with absolute links
from importlib.util import find_spec as find_import_spec

if find_import_spec("notfound"):
    extensions.append("notfound.extension")

    notfound_urls_prefix = "/projects/evaluator_equilibration/en/stable/"
    notfound_context = {
        "title": "404: File Not Found",
        "body": f"""
    <h1>404: File Not Found</h1>
    <p>
        Sorry, we couldn't find that page. This often happens as a result of
        following an outdated link. Please check the
        <a href="{notfound_urls_prefix}">latest stable version</a>
        of the docs, unless you're sure you want an earlier version, and
        try using the search box or the navigation menu on the left.
    </p>
    <p>
    </p>
    """,
    }

# Myst NB settings
# Execute all notebooks on build
nb_execution_mode = "force"
# List of notebooks NOT to execute (use output stored in notebook instead)
nb_execution_excludepatterns = []

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = [".rst", ".md", ".ipynb"]

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "EN"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "default"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "openff_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_theme_options = {
    # Repository integration
    # Set the repo url for the link to appear
    "repo_url": "https://github.com/lilyminium/evaluator-equilibration",
    # The name of the repo. If must be set if repo_url is set
    "repo_name": "evaluator-equilibration",
    # Must be one of github, gitlab or bitbucket
    "repo_type": "github",
    # Colour for sidebar captions and other accents. One of
    # openff-toolkit-blue, openff-dataset-yellow, openff-evaluator-orange,
    # red, pink, purple, deep-purple, indigo, blue, light-blue, cyan,
    # teal, green, light-green, lime, yellow, amber, orange, deep-orange
    "color_accent": "openff-toolkit-blue",
    # Content Minification for deployment, prettification for debugging
    "html_minify": False,
    "html_prettify": False,
    "css_minify": True,
    "master_doc": False,
    "globaltoc_include_local": True,
    "globaltoc_depth": 3,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["flowchart.css"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default:
html_sidebars = {
    "**": ["globaltoc.html", "searchbox.html", "localtoc.html"],
}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "evaluator-equilibrationdoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "evaluator-equilibration.tex",
        "Evaluator Equilibration Documentation",
        "evaluator-equilibration",
        "manual",
    ),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "evaluator-equilibration", "Evaluator Equilibration Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "evaluator-equilibration",
        "Evaluator Equilibration Documentation",
        author,
        "evaluator-equilibration",
        "A short description of the project.",
        "Miscellaneous",
    ),
]
