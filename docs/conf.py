# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'zafiaonline.py'
copyright = '2025, unelected'
author = 'unelected'
release = '2.2.4'

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_baseurl = "https://unelected.github.io/zafiaonline.py"
