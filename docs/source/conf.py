# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "colosseum"
copyright = "2024, robot-colosseum"
author = "robot-colosseum"
release = "0.6.5"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinxcontrib.bibtex",
    "sphinxcontrib.katex",
    "sphinxcontrib.youtube",
    "sphinx_copybutton",
    "sphinx_favicon",
    "sphinx_reredirects",
    "sphinx_toolbox.collapse",
    "sphinx_toolbox.github",
    "sphinx_toolbox.sidebar_links",
]

# GitHub-related options
github_username = "robot-colosseum"
github_repository = "robot-colosseum"

templates_path = ["_templates"]
exclude_patterns = []

bibtex_bibfiles = ["references.bib"]

redirects = {"index": "overview.html"}

# Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
