# %%
# Packages
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import xarray as xr
import xugrid as xu
from resilientplotterclass import rpclass

# Repository path
repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# %%
# File paths
file_path_tif = r'p:\11203480-yunlin-morpho-update\01_Data\04_BathymetryData\02_FullAreaSurveys\2023 Bathymetry\01_ProcessedData\YUN_BAT_DWT_ALL_1m_202303-202306_TWD97_compressed.tif'
file_path_nc = r'p:\11203480-yunlin-morpho-update\03_NumericalModelling\01_TSM\98_Haixia\r2020_3D_original_wKeywords_202204container\fm\final_grid_v2_gebco13_add030m_net.nc'

file_path_aoi = r'p:\11203480-yunlin-morpho-update\01_Data\02_PolygonData\OldData\YUN_PM_EIA_Area_TWD97_20180209.geojson'
file_path_gls = os.path.join(repo_path, 'project', 'project_guidelines.json')

# Read data
da = xr.open_dataarray(file_path_tif).sel(band=1)
uda = xu.open_dataset(file_path_nc)['NetNode_z']
uda.grid.set_crs('EPSG:4326')

# Remove coordinates
remove_crs = False
if remove_crs:
    da = da.drop_vars('spatial_ref')
    uda.attrs['crs'] = None

# Read geometries
gdf_aoi = gpd.read_file(file_path_aoi)
gdf_aoi_4326 = gdf_aoi.to_crs('EPSG:4326')

# Set guidelines
gls = {'general': {'crs': 'EPSG:3826'},
       'extent_type': {'aoi': {'xlim': [146000, 156000], 'ylim': [2601000, 2618000]},
                       'aoi_wide': {'xlim': [143000, 167000], 'ylim': [2596000, 2624000]},
                       'aoi_4326': {'xlim': [117, 121], 'ylim': [22, 26]}}}
 
# %%
# Set guidelines
rpc = rpclass(cartopy=False)
rpc.set_guidelines(gls)
#rpc.set_guidelines(file_path_gls)

# %%
# Get guideline options
gls_options = rpc.get_guideline_options()
#print(json.dumps(gls_options, indent=4))

# %%
# Plot structured data using general plot methods
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
rpc.imshow(da, ax=ax, data_type='bathymetry', extent_type='aoi_wide', skip=10)
rpc.contour(da, ax=ax, data_type='bathymetry', skip=10)
rpc.geometries(gdf_aoi, ax=ax, geometry_type='aoi', edgecolor='red')
rpc.basemap(ax=ax, map_type='satellite')
ax.legend(loc='upper right')
fig.tight_layout()

# %%
# Plot unstructured data using general plot methods
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
rpc.scatter(uda.where(uda.values < 0), ax=ax, extent_type='aoi_4326', data_type='bathymetry', center=False, vmin=-100, vmax=0)
rpc.geometries(gdf_aoi_4326, ax=ax, geometry_type='aoi', edgecolor='black')
rpc.basemap(ax=ax, map_type='satellite', crs='EPSG:4326')
ax.legend(loc='upper right')
fig.tight_layout()

# %%
# Plot unstructured grid using general plot methods
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
rpc.grid(uda.where(uda.values < 0), ax=ax, geometry_type='grid', extent_type='aoi_4326', alpha=0.5)
rpc.geometries(gdf_aoi_4326, ax=ax, geometry_type='aoi', edgecolor='black')
rpc.basemap(ax=ax, map_type='satellite', crs='EPSG:4326')
ax.legend(loc='upper right')
fig.tight_layout()

# %%