# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "optionz"
copyright = "2026, Fábio Macêdo Mendes"
author = "Fábio Macêdo Mendes"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_mdinclude",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]

autodoc_typehints = "none"
napoleon_google_docstring = True
napoleon_numpy_docstring = False
typehints_document_overloads = False

templates_path = ["_templates"]
exclude_patterns = []  # type: ignore
source_suffix = [".rst", ".md"]

intersphinx_mapping = {
    "hypothesis": ("https://hypothesis.readthedocs.io/en/latest/", None),
    "python": ("https://docs.python.org/3", None),
}

nitpick_ignore = [
    ("py:class", "typing.Any"),
    ("py:class", "errorz.GenericAlias"),
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
