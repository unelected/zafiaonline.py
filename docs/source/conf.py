# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import datetime

sys.path.insert(0, os.path.abspath("../../src"))
from zafiaonline.version import __version__

project = 'zafiaonline'
copyright = f'2024-{datetime.date.today().year}, unelected'
author = 'unelected'
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
    "sphinxcontrib_trio"
]

# autodoc настройки
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_inherit_docstrings = False
python_use_unqualified_type_names = True
autodoc_mock_imports = []

# autosummary (генерация таблиц классов и функций)
autosummary_generate = True

# -- Paths -------------------------------------------------------------------
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_static_path = ["_static"]

# -- Theme -------------------------------------------------------------------
html_theme = "furo"

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#0099cc",
        "color-brand-content": "#0077aa",
    },
    "dark_css_variables": {
        "color-brand-primary": "#66ccff",
        "color-brand-content": "#33aaff",
    },
}

html_show_sphinx = False

