# %%
# Packages
import matplotlib.pyplot as plt
import os
import xarray as xr
import xugrid as xu
import sys

# Repository path
repo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))

# Resilient plotter class
sys.path.append(os.path.join(repo_path, 'src'))
from resilientplotterclass import resilientplotterclass

# %%
# File paths
file_path_nc = r'p:\archivedprojects\11209197-virtualclimatelab\01_data\Delft3D\wadsea_0000_map.nc'
file_path_tif = r'c:\Users\white_rn\Documents\GitHub\MorphoPy\data\dataArrays\Grid_in.tif'
file_path_gls = os.path.join(repo_path, 'project', 'project_guidelines.json')

# Read data
da = xr.open_dataarray(file_path_tif)
ds = xu.open_dataset(file_path_nc)

# %%
# Set guidelines
rpc = resilientplotterclass(file_path_gls)

# %%
# General plot for structured data
fig, axs = plt.subplots(2, 2, figsize=(10, 10))
axs = axs.flatten()
rpc.pcolormesh(da.sel(band=1), ax=axs[0], data_type='bathymetry', extent_type='aoi', vmin=-40, vmax=0)
rpc.imshow(da.sel(band=1), ax=axs[1], data_type='bathymetry', extent_type='aoi', vmin=-40, vmax=0)
rpc.contour(da.sel(band=1), ax=axs[2], data_type='bathymetry', extent_type='aoi', vmin=-40, vmax=0)
rpc.contourf(da.sel(band=1), ax=axs[3], data_type='bathymetry', extent_type='aoi', vmin=-40, vmax=0)

# %%
# General plot for unstructured data
fig, axs = plt.subplots(2, 2, figsize=(10, 10))
axs = axs.flatten()
rpc.pcolormesh(ds['mesh2d_flowelem_bl'], ax=axs[0], data_type='bathymetry', extent_type='aoi', vmin=-40, vmax=0)
rpc.imshow(ds['mesh2d_flowelem_bl'], ax=axs[1], data_type='bathymetry', extent_type='aoi', vmin=-40, vmax=0)
rpc.contour(ds['mesh2d_flowelem_bl'], ax=axs[2], data_type='bathymetry', extent_type='aoi', vmin=-40, vmax=0)
rpc.contourf(ds['mesh2d_flowelem_bl'], ax=axs[3], data_type='bathymetry', extent_type='aoi', vmin=-40, vmax=0)

# %%
# Specific plot for structured data
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
rpc.bathymetry(da.sel(band=1), ax=ax, extent_type='aoi', vmin=-40, vmax=0)

# %%
# Specific plot for unstructured data
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
rpc.bathymetry(ds['mesh2d_flowelem_bl'], ax=ax, extent_type='aoi', vmin=-40, vmax=0)

# %%
