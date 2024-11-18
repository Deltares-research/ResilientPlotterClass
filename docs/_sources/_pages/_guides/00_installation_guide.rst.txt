Installation Guide
==================

Prerequisites
-------------
The following steps are required to install and use the ResilientPlotterClass:

1. Install `Python`_

2. Install a python package manager (e.g. `Mamba`_)

3. Install `Git`_

5. Install a code editor (e.g. `Virtual Studio Code`_)

Standalone Installation
-----------------------
The following steps describe how to install the ResilientPlotterClass as a standalone package:

1. Clone the `ResilientPlotterClass Repository`_

2. Create a dedicated environment or use an existing one:

.. code-block:: text

    mamba create --name the ResilientPlotterClass_env pip ipykernel

3. Activate the environment:

.. code-block:: text

    mamba activate the ResilientPlotterClass_env

4. Install the ResilientPlotterClass:

.. code-block:: text

    pip install -e c:\...\the ResilientPlotterClass

Installation with Environment
-----------------------------
The following steps describe how to install the ResilientPlotterClass using the provided environment file:

1. Clone the `ResilientPlotterClass Repository`_

2. Create a dedicated environment using the provided environment file:

.. code-block:: text

    mamba env create --name the ResilientPlotterClass_env --file c:\...\the ResilientPlotterClass\the ResilientPlotterClass_env.yml

3. Activate the environment you just created:

.. code-block:: text

    mamba activate the ResilientPlotterClass_env

4. Install the ResilientPlotterClass:

z.. code-block:: text

    pip install -e c:\...\the ResilientPlotterClass

.. _Python: https://www.python.org/downloads
.. _Mamba: https://github.com/conda-forge/miniforge#mambaforge
.. _Git: https://git-scm.com/downloads
.. _Virtual Studio Code: https://code.visualstudio.com/Download
.. _ResilientPlotterClass Repository: https://github.com/Deltares-research/ResilientPlotterClass
.. _GDAL: https://gdal.org
.. _Pandoc: https://pandoc.org