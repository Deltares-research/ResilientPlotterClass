# Build the documentation for the Resilient Plotter Class
The following sections describe how to build the documentation for the ResilientPlotterClass package. The documentation is built using [Sphinx](https://www.sphinx-doc.org/en/master/index.html) and the documentation is written in reStructuredText. The documentation is built in the html format and can be viewed in a web browser.

## Prerequisites
The following steps are required to install and use ResilientPlotterClass:

1. Install [Python](https://www.python.org/downloads)

2. Install a python package manager (e.g., [Mamba](https://github.com/conda-forge/miniforge#mambaforge))

3. Install [Git](https://git-scm.com/downloads)

4. Install a code editor (e.g. [Virtual Studio Code](https://code.visualstudio.com/Download))

## Documentation Installation
The following steps describe how to install the ResilientPlotterClass package to be able to build the documentation:

1. Clone the [ResilientPlotterClass Repository](https://github.com/Deltares-research/ResilientPlotterClass)

2. Create a dedicated environment or use an existing one:
    ```
    mamba create --name rpc_docs_env pip ipykernel
    ```

3. Activate the environment you just created:
    ```	
    mamba activate rpc_docs_env
    ```

4. Install ResilientPlotterClass:
    ```
    pip install -e c:\...\ResilientPlotterClass[docs]
    ```

5. Install [Pandoc](https://pandoc.org)
    ```
    mamba install conda-forge::pandoc
    ```

## Build the Documentation
The following steps describe how to build the documentation for the ResilientPlotterClass package:
1. Activate the ResilientPlotterClass environment
    ```
    mamba activate rpc_docs_env
    ```

2. Navigate to the `docs_builder` directory of the ResilientPlotterClass repository
    ```
    cd /d c:\...\ResilientPlotterClass\docs_builder
    ```

3. Build the html documentation
    ```
    make.bat html
    ```
   
4. Copy the html documentation from the `docs_builder\_build\html` directory to the `docs` directory of the ResilientPlotterClass repository

