# %%
# Configuration file for the Sphinx documentation builder.

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# %%
# -- Path setup --------------------------------------------------------------
# Packages
import os
import sys

# Paths
sys.path.insert(0, os.path.abspath('../src/resilientplotterclass'))

# %%
# -- Create pages ------------------------------------------------------------
# Packages
import os
import sys
import shutil
import inspect
from collections import ChainMap
import resilientplotterclass
from resilientplotterclass.axes import *
from resilientplotterclass.basemaps import *
from resilientplotterclass.colormaps import *
from resilientplotterclass.data_xarray import *
from resilientplotterclass.data_xugrid import *
from resilientplotterclass.geometries import *
from resilientplotterclass.rescale import *
from resilientplotterclass.utils import *

# Get guide notebook paths
dir_path_guide_in = os.path.abspath('../guides')
dir_path_guide_out = os.path.abspath('_pages')
file_path_guide_old = glob.glob(os.path.join(dir_path_guide_out, '_guides', '*'))
file_path_guide_in = glob.glob(os.path.join(dir_path_guide_in, '*'))
file_path_guide_out = [os.path.join(dir_path_guide_out, '_guides', os.path.basename(file_path)) for file_path in file_path_guide_in]

# Create the guide directory
os.makedirs(os.path.join(dir_path_guide_out, '_guides'), exist_ok=True)

# Clear all the old guide notebooks
for file_path in file_path_guide_old:
    os.remove(file_path)

# Copy the new guide notebooks
for file_path_in, file_path_out in zip(file_path_guide_in, file_path_guide_out):
    shutil.copy(file_path_in, file_path_out)

# Remove the guides page
file_path_guide_page = os.path.join(dir_path_guide_out, 'guides.rst')

# Create the guides page
file_guides = ['.'.join(os.path.basename(file_path).split('.')[:-1]) for file_path in file_path_guide_out]
file_guides = sorted(file_guides)

# Create the guides page
page = 'Guides\n======\n\n'
page += 'The guides provide detailed instructions on how to install and use the ResilientPlotterClass. The following guides are available:\n\n'

for file_guide in file_guides:
    page += f'* :doc:`_guides/{file_guide}`\n'

page += '\n.. toctree::\n'
page += '    :maxdepth: 2\n'
page += '    :caption: Guides\n'
page += '    :hidden:\n\n'
page += '     Overview <self>\n'
for file_guide in file_guides:
    guide_name = ' '.join(file_guide.split('_')[1:]).title()
    page += f'     {guide_name} <_guides/{file_guide}>\n'

with open(os.path.join(dir_path_guide_out, 'guides.rst'), 'w+') as f:
    f.write(page)

# %%
# Get modules
modules = {resilientplotterclass.__name__: resilientplotterclass}
modules = dict(ChainMap(modules,*[dict(inspect.getmembers(module, inspect.ismodule)) for module in modules.values()]))
modules = dict(ChainMap(modules,*[dict(inspect.getmembers(module, inspect.ismodule)) for module in modules.values()]))
modules = {module: modules[module] for module in modules if modules[module].__name__.startswith('resilientplotterclass') and module.startswith('_') is False}

top_modules = dict(inspect.getmembers(resilientplotterclass, inspect.ismodule))
top_modules = {module: top_modules[module] for module in top_modules if top_modules[module].__name__.startswith('resilientplotterclass') and module.startswith('_') is False}
top_modules = [f'{module.__name__}' for module in top_modules.values()]

# Get classes
classes = dict(ChainMap(*[dict(inspect.getmembers(module, inspect.isclass)) for module in modules.values()]))
classes = {class_: classes[class_] for class_ in classes if classes[class_].__module__.startswith('resilientplotterclass') and class_.startswith('_') is False}
classes = dict(sorted(classes.items()))
classes = [f'{class_.__module__}.{class_.__name__}' for class_ in classes.values()]

# Get functions
functions = {}
for module in modules.values():
    for member in inspect.getmembers(module, inspect.isfunction):
        if member[0].startswith('_') is False and member[1].__module__.startswith('resilientplotterclass'):
            functions['{}.{}'.format(member[1].__module__.split('.')[1], member[0])] = member[1]
functions = dict(sorted(functions.items()))
functions = [f'{function.__module__}.{function.__name__}' for function in functions.values()]

# %%
# Function to generate the pages
def genenerate_pages(dir_path_page, structs, struct_type, title=None):
    """ Generate the pages for classes, methods, attributes and functions."""
    # Clear the directory
    shutil.rmtree(dir_path_page, ignore_errors=True)
    os.makedirs(dir_path_page, exist_ok=True)

    # Get the title
    if title is None:
        title = struct_type

    # Function to generate the page
    def generate_page(dir_path_page, struct, struct_type, title=None):
        """ Generate the page for class, method, attribute or function."""

        # Get the title
        if title is None:
            title = '.'.join(struct.split('.')[1:])

        # Create the page
        page = f'{title}\n{"="*len(title)}\n'
        page += f'.. autoclass:: {struct}\n    :members:\n' if struct_type == 'Classes' else ''
        page += f'.. automethod:: {struct}\n' if struct_type == 'Methods' else ''
        page += f'.. autoattribute:: {struct}\n' if struct_type == 'Attributes' else ''
        page += f'.. autofunction:: {struct}\n' if struct_type == 'Functions' else ''

        # Export the page to a file
        with open(os.path.join(dir_path_page, f'{struct}.rst'), 'w+') as f:
            f.write(page)

    # Create pages for each struct, function and method
    if struct_type != 'Modules':
        for struct in structs:
            generate_page(dir_path_page=dir_path_page, struct=struct, struct_type=struct_type)

    # Create the main page
    page = f'{struct_type}\n{"="*len(struct_type)}\n'
    if struct_type == 'Modules':
        page += f'.. autosummary::\n    :toctree:\n    :recursive:\n\n'
        for struct in structs:
            page += f'    {struct}\n'
    else:
        page += f'.. toctree::\n    :caption: {struct_type}\n\n'
        for struct in structs:
            page += f'    {struct}\n'
    
    # Export the page to a file
    with open(os.path.join(dir_path_page, f'{struct_type.lower()}.rst'), 'w+') as f:
        f.write(page)

# Create the pages
genenerate_pages(dir_path_page='_pages/_modules', structs=top_modules, struct_type='Modules')
genenerate_pages(dir_path_page='_pages/_classes', structs=classes, struct_type='Classes')
genenerate_pages(dir_path_page='_pages/_functions', structs=functions, struct_type='Functions')

# %%
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Packages
import time
import toml

# Read the pyproject.toml file
file_path_pyproject = os.path.abspath('../pyproject.toml')
pyproject = toml.load(file_path_pyproject)

# Get the project information
project = pyproject['project']['name']
copyright = '{}, {} & {}'.format(time.strftime('%Y'), pyproject['project']['authors'][0]['name'], pyproject['project']['authors'][1]['name'])
author = '{} & {}'.format(pyproject['project']['authors'][0]['name'] , pyproject['project']['authors'][1]['name'])
release = pyproject['project']['version']

# %%
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.autosummary',
              'sphinx.ext.doctest',
              'sphinx.ext.intersphinx',
              'sphinx_design',
              'sphinx_copybutton',
              'nbsphinx']
exclude_patterns = ['_build', 'conf.py', 'make.bat', 'Makefile']

# %%
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_logo = '_logo/Resilient_Plotter_Class_Logo.png'
html_sidebars = {
  "index": [],
}
html_theme_options = {
    "secondary_sidebar_items": {
        "index": [],
    },
}

# %%
