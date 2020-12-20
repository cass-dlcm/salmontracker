# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../../salmontracker"))


# -- Project information -----------------------------------------------------

project = "Salmon Tracker"
copyright = "2020, Cassandra de la Cruz-Munoz"
author = "Cassandra de la Cruz-Munoz"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.linkcode", "sphinx.ext.intersphinx"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["data"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


master_doc = "index"


intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "jsonlines": ("https://jsonlines.readthedocs.io/en/latest/", None),
    "requests": ("https://requests.readthedocs.io/en/master/", None),
}


def linkcode_resolve(domain, info):
    if domain != "py":
        return None
    if not info["module"]:
        return None
    filename = info["module"].replace(".", "/")
    return (
        "https://github.com/cassdelacruzmunoz/salmontracker/blob/dev/%s.py" % filename
    )


import guzzle_sphinx_theme

html_theme_path = guzzle_sphinx_theme.html_theme_path()
html_theme = "guzzle_sphinx_theme"

# Register the theme as an extension to generate a sitemap.xml
extensions.append("guzzle_sphinx_theme")

# Guzzle theme options (see theme.conf for more information)
html_theme_options = {
    # Set the name of the project to appear in the sidebar
    "project_nav_name": "Salmon Tracker",
}
