# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# %%
import glob
import os
import shutil
import tomllib

DIR_PATH_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


# %%
def load_project_metadata(file_path_toml):
    with open(file_path_toml, "rb") as f:
        toml_data = tomllib.load(f)

    project_data = toml_data.get("project", {})

    project = project_data.get("name", "Unknown Project")
    authors = project_data.get("authors", [])
    author = authors[0]["name"] if authors else "Unknown Author"
    release = project_data.get("version", "0.0.1")

    return {
        "project": project,
        "author": author,
        "release": release,
    }


metadata = load_project_metadata(os.path.join(DIR_PATH_REPO, "pyproject.toml"))
project = metadata["project"]
author = metadata["author"]
release = metadata["release"]

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
    "nbsphinx",
]

intersphinx_mapping = {
    "rioxarray": ("https://corteva.github.io/rioxarray/stable/", None),
    "xarray": ("http://xarray.pydata.org/en/stable/", None),
    "geopandas": ("https://geopandas.org/en/stable/", None),
}

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_logo = "../logo/rpc_logo_white.png"
html_theme_options = {
    "logo_only": True,
}

# -- nbsphinx configuration -----------------------------------------------
nbsphinx_execute = "never"


# -- Custom pre-build tasks --------------------------------------------------
def copy_notebooks(dir_path_notebooks, dir_path_notebooks_copy):
    """
    Copy Jupyter notebooks from the source directory to the docs directory.
    """
    if os.path.exists(dir_path_notebooks_copy):
        shutil.rmtree(dir_path_notebooks_copy)
    os.makedirs(dir_path_notebooks_copy, exist_ok=True)

    file_path_notebooks = glob.glob(os.path.join(dir_path_notebooks, "*.ipynb"))

    # Exclude notebooks
    file_path_notebooks = [file_path for file_path in file_path_notebooks if os.path.basename(file_path) not in ["00_batch.ipynb"]]

    for file_path_notebook in file_path_notebooks:
        file_path_notebook_copy = os.path.join(dir_path_notebooks_copy, os.path.basename(file_path_notebook))
        shutil.copy(file_path_notebook, file_path_notebook_copy)

    file_path_rst = os.path.join(DIR_PATH_REPO, "docs", "source", os.path.basename(dir_path_notebooks_copy) + ".rst")
    with open(file_path_rst, "w", encoding="utf-8") as f:
        title = os.path.basename(dir_path_notebooks_copy).replace("_", " ").title()
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")
        f.write(".. toctree::\n   :maxdepth: 1\n\n")
        for file_path_notebook in file_path_notebooks:
            rel_path = os.path.join(
                os.path.basename(os.path.dirname(file_path_notebook)),
                os.path.basename(file_path_notebook),
            ).replace("\\", "/")  # Windows path fix
            f.write(f"   {rel_path}\n")


def on_builder_inited(app):
    # Copy notebooks
    copy_notebooks(
        os.path.join(DIR_PATH_REPO, "notebooks", "usage_examples"),
        os.path.join(DIR_PATH_REPO, "docs", "source", "usage_examples"),
    )


def setup(app):
    print("Setting up Sphinx app...")
    app.connect("builder-inited", on_builder_inited)
