# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
from importlib.metadata import version

sys.path.insert(0, os.path.abspath("../../"))
# sys.path.insert(0, os.path.abspath("./"))  # in conf.py


project = "Dev-Kit MCP Server"  # Updated project name
version = version("dev-kit-mcp-server")  # Updated package name
release = version

copyright = "2025, DanielAvdar"  # noqa  todo: change this to your name
author = "DanielAvdar"  # todo: change this to your name

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Core extension for pulling docstrings
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.githubpages",  # If deploying to GitHub Pages
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
master_doc = "index"

# PyData theme options
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/DanielAvdar/dev-kit-mcp-server",
            "icon": "fa-brands fa-github",
        }
    ],
    "use_edit_page_button": False,
    "show_toc_level": 2,
}
# html_static_path = ["_static"]
