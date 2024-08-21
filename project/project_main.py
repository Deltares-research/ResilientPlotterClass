# %%
# Packages
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import xarray as xr
import xugrid as xu
from resilientplotterclass.rpc import rpc_class

# Repository path
repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# %%
# File paths
file_path_nc = r'p:\archivedprojects\11209197-virtualclimatelab\01_data\Delft3D\wadsea_0000_map.nc'
file_path_tif = r'p:\archivedprojects\11209197-virtualclimatelab\01_data\Bodem\originele_bodem.tif'
file_path_aoi = r'p:\archivedprojects\11209197-virtualclimatelab\01_data\Extent\afmetingen_krappebox.shp'
file_path_gls = os.path.join(repo_path, 'project', 'project_guidelines.json')

# Read data
da = xr.open_dataarray(file_path_tif).sel(band=1)
uda = xu.open_dataset(file_path_nc)['mesh2d_flowelem_bl']
uda.attrs['crs'] = da.rio.crs

# Remove coordinates
remove_crs = False
if remove_crs:
    da = da.drop_vars('spatial_ref')
    uda.attrs['crs'] = None

# Read geometries
gdf_aoi = gpd.read_file(file_path_aoi)

# Get bounds
bounds_da = da.rio.bounds()
bounds_uda = [float(uda.mesh2d_face_x.min()), float(uda.mesh2d_face_y.min()),
              float(uda.mesh2d_face_x.max()), float(uda.mesh2d_face_y.max())]
bounds = [min(bounds_da[0], bounds_uda[0]), min(bounds_da[1], bounds_uda[1]),
          max(bounds_da[2], bounds_uda[2]), max(bounds_da[3], bounds_uda[3])]

# Get x and y limits
xlim = [bounds[0], bounds[2]]
ylim = [bounds[1], bounds[3]]

# Get guidelines
gls = {'general': {'crs': da.rio.crs, 'bounds': bounds}, 'extent_type': {'aoi': {'xlim': xlim, 'ylim': ylim}}}

# %%
# Set guidelines
rpc = rpc_class(cartopy=False)
rpc.set_guidelines(gls)
#rpc.set_guidelines(file_path_gls)
rpc.set_cartopy()

# %%
# Get guideline options
gls_options = rpc.get_guideline_options()
#print(json.dumps(gls_options, indent=4))

# %%
# Plot guideline colormaps
# rpc.plot_colormaps()

# %%
# General plot for structured data, geometry and basemap
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
rpc.pcolormesh(da, ax=ax, data_type='bathymetry', extent_type='aoi', skip=10)
rpc.geometries(gdf_aoi, ax=ax, geometry_type='aoi', extent_type='aoi')
rpc.basemap(ax=ax, map_type='osm', extent_type='aoi')
ax.legend(loc='upper right')
fig.tight_layout()

# %%
# General plot for unstructured data, geometry and basemap
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
rpc.pcolormesh(uda, ax=ax, data_type='bathymetry', extent_type='aoi')
rpc.geometries(gdf_aoi, ax=ax, geometry_type='aoi', extent_type='aoi')
rpc.basemap(ax=ax, map_type='satellite', extent_type='aoi')
ax.legend(loc='upper right')
fig.tight_layout()

# %%
# General plot for structured data, geometry and cartopy
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
rpc.pcolormesh(da, ax=ax, data_type='bathymetry', extent_type='aoi', skip=10)
rpc.geometries(gdf_aoi, ax=ax, geometry_type='aoi', extent_type='aoi')
rpc.cartopy(ax=ax, extent_type='aoi')
ax.legend(loc='upper right')
fig.tight_layout()

# %%
# General plot for unstructured data, geometry and cartopy
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
rpc.pcolormesh(uda, ax=ax, data_type='bathymetry', extent_type='aoi')
rpc.geometries(gdf_aoi, ax=ax, geometry_type='aoi', extent_type='aoi')
rpc.cartopy(ax=ax, extent_type='aoi')
ax.legend(loc='upper right')
fig.tight_layout()

# %%
# General plot for structured data, geometry and basemap with quiver
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
rpc.grid(uda, ax=ax, geometry_type='grid', extent_type='aoi', zorder=1)
rpc.geometries(gdf_aoi, ax=ax, geometry_type='aoi', extent_type='aoi')
rpc.basemap(ax=ax, map_type='osm', extent_type='aoi')
ax.legend(loc='upper right')
fig.tight_layout()

# %%
# Specific plot for structured bathymetry
rpc.bathymetry(da)

# %%
# Specific plot for unstructured bathymetry
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
rpc.bathymetry(uda, gdf=gdf_aoi, ax=ax)
rpc.grid(uda, ax=ax)
ax.legend()

# %%
























# %%
# Plot using Gouraud shading
fig, ax = plt.subplots(1, 1, figsize=(5, 5))

xs = uda.mesh2d_face_x.values
ys = uda.mesh2d_face_y.values
zs = uda.values

import matplotlib.tri as tri
triangles = tri.Triangulation(xs, ys)
ax.tripcolor(triangles, zs, shading='gouraud', cmap='Spectral_r')

(xs, ys, triangles), tf_con = uda.grid.triangulation # https://deltares.github.io/xugrid/api/xugrid.Ugrid2d.html

import numpy as np
zs = np.random.rand(xs.shape[0])

fig, ax = plt.subplots(1, 2, figsize=(10, 5))
axs = ax.flatten()
axs[0].tripcolor(xs, ys, triangles, zs, shading='flat', cmap='Spectral_r')
axs[1].tripcolor(xs, ys, triangles, zs, shading='gouraud', cmap='Spectral_r')

# %%
fig, ax = plt.subplots(1, 1, figsize=(5, 5))
uda.grid.plot(ax=ax, linewidth=0.5, color='red', alpha=0.5)
rpc.basemap(ax=ax, map_type='osm', extent_type='aoi', crs=uda.crs, xy_unit='m')

# %%
fig, ax = plt.subplots(1, 1, figsize=(5, 5))
skip = 50
da = da.isel(x=slice(None, None, skip), y=slice(None, None, skip))
ds = da.to_dataset()
ds.band_data.values = ds.band_data.values - np.nanmax(ds.band_data.values)
ds.plot.quiver(ax=ax, x='x', y='y', u='band_data', v='band_data')
rpc.basemap(ax=ax, map_type='osm', extent_type='aoi', crs=da.rio.crs, xy_unit='m')

# %%
fig, ax = plt.subplots(1, 1, figsize=(5, 5))
ds = uda.to_dataset()
ds.plot.quiver(ax=ax, x='mesh2d_face_x', y='mesh2d_face_y', u='mesh2d_flowelem_bl', v='mesh2d_flowelem_bl')
ax.set_xlim(100000, 120000)
ax.set_ylim(550000, 570000)
rpc.basemap(ax=ax, map_type='osm', crs=uda.crs, xy_unit='m')

# %%
