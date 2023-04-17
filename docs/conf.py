"""Configuration file for the Sphinx documentation builder."""
import os
import sys

sys.path.insert(0, os.path.abspath(".."))
import orion

# -- Project information -----------------------------------------------------

project = "orion-nais"
copyright = "MIT"
author = "Lasse Lambrechts"

# The full version, including alpha/beta/rc tags
release = version = "0.1.1"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "m2r"
]


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

autodoc_typehints = "description"

html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/hack-font/3.3.0/web/hack.min.css"
]
