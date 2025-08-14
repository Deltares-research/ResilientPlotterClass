# Building the documentation
## Prerequisites
The following prerequisites are required to install and use the ResilientPlotterClass:
1. Install [Python](https://www.python.org/downloads)

2. Install a python package manager (e.g. [uv](https://docs.astral.sh/uv/getting-started/installation/),  [Mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html))

3. Install [Git](https://git-scm.com/downloads)

4. Install a code editor (e.g. [Virtual Studio Code](https://code.visualstudio.com/Download))

5. Install [Pandoc](https://github.com/jgm/pandoc/releases/tag/3.7.0.2) (for windows use .msi installer)

## Installation for developers
To install the ResilientPlotterClass for development purposes, follow these steps:

1. Clone the [ResilientPlotterClass](https://github.com/Deltares-research/ResilientPlotterClass) repository:
    ```bash
    git clone https://github.com/Deltares-research/ResilientPlotterClass.git c:\...\ResilientPlotterClass
    ```

2. Navigate to the cloned repository:
    ```bash
    cd c:\...\ResilientPlotterClass
    ```

3. Synchronise the virtual environment
    ``` bash
    uv sync
    ```

## Building the documentation
To build the documentation, follow these steps:

1. Navigate to the `docs` directory of the cloned repository:
    ```bash
    cd c:\...\ResilientPlotterClass\docs
    ```
    
2. Build the documentation using [sphinx](https://www.sphinx-doc.org/en/master/):
    ```bash
    sphinx-build -b html source build
    ```