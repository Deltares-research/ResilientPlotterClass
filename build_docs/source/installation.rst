Installation
============

Prerequisites
-------------

The following prerequisites are required to install and use the ResilientPlotterClass:

1. Install `Python <https://www.python.org/downloads>`__
2. Install a Python package manager (e.g. `uv <https://docs.astral.sh/uv/getting-started/installation/>`__, `Mamba <https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html>`__)
3. Install `Git <https://git-scm.com/downloads>`__
4. Install a code editor (e.g. `Visual Studio Code <https://code.visualstudio.com/Download>`__)

Installation for users with uv
------------------------------

To install the ResilientPlotterClass for users with `uv <https://docs.astral.sh/uv/getting-started/installation/>`__, follow these steps:

1. Install the ResilientPlotterClass::
 
    uv add "resilientplotterclass @ git+https://github.com/Deltares-research/ResilientPlotterClass.git@main"

Installation for users with Mamba
---------------------------------

To install the ResilientPlotterClass for users with `Mamba <https://github.com/conda-forge/miniforge#mambaforge>`__ follow these steps:

1. If necessary, create a new environment::

    mamba create -n rpc_env python=3.12

2. Activate the environment::

    mamba activate rpc_env

3. Install pip and gdal::

    mamba install pip
    mamba install -c conda-forge gdal

4. Install the ResilientPlotterClass::

    pip install "resilientplotterclass @ git+https://github.com/Deltares-research/ResilientPlotterClass.git@main"

Installation for developers with uv
-----------------------------------

To install the ResilientPlotterClass for developers with `uv <https://docs.astral.sh/uv/getting-started/installation/>`__, follow these steps:

1. Clone the `ResilientPlotterClass <https://github.com/Deltares-research/ResilientPlotterClass>`__ repository::

    git clone https://github.com/Deltares-research/ResilientPlotterClass.git c:\...\ResilientPlotterClass

2. Navigate to the cloned repository::

    cd c:\...\ResilientPlotterClass

3. Synchronise the virtual environment::

    uv sync

