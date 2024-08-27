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
file_path_tif = r'p:\archivedprojects\11209197-virtualclimatelab\01_data\Bodem\originele_bodem.tif'
file_path_nc = r'p:\archivedprojects\11209197-virtualclimatelab\01_data\Delft3D\wadsea_0000_map.nc'
file_path_aoi = r'p:\archivedprojects\11209197-virtualclimatelab\01_data\Extent\afmetingen_krappebox.shp'
file_path_gls = os.path.join(repo_path, 'project', 'project_guidelines.json')

# Read data
da = xr.open_dataarray(file_path_tif).sel(band=1)
ds = da.to_dataset()
uds = xu.open_dataset(file_path_nc)
uds.grid.set_crs(da.rio.crs)
uda = uds['mesh2d_flowelem_bl']

# Remove coordinates
remove_crs = False
if remove_crs:
    da = da.drop_vars('spatial_ref')
    uda.attrs['crs'] = None

# Read geometries
gdf_aoi = gpd.read_file(file_path_aoi)

#
# Get bounds
bounds_da = da.rio.bounds()
bounds_uda = [float(uda.mesh2d_face_x.min()), float(uda.mesh2d_face_y.min()),
              float(uda.mesh2d_face_x.max()), float(uda.mesh2d_face_y.max())]
bounds = [min(bounds_da[0], bounds_uda[0]), min(bounds_da[1], bounds_uda[1]),
          max(bounds_da[2], bounds_uda[2]), max(bounds_da[3], bounds_uda[3])]

# Get aoi exents
aoi1 = {'xlim': [bounds_da[0], bounds_da[2]], 'ylim': [bounds_da[1], bounds_da[3]]}
aoi2 = {'xlim': [bounds_uda[0], bounds_uda[2]], 'ylim': [bounds_uda[1], bounds_uda[3]]}

# Get guidelines
gls = {'general': {'crs': da.rio.crs, 'bounds': bounds}, 'extent_type': {'aoi1': aoi1, 'aoi2': aoi2}}

# %%
# Set guidelines
rpc = rpclass(cartopy=False)
rpc.set_guidelines(gls)
#rpc.set_guidelines(file_path_gls)
rpc.set_cartopy()

# %%
# Get guideline options
gls_options = rpc.get_guideline_options()
#print(json.dumps(gls_options, indent=4))

# %%
# Plot guideline colormaps
#rpc.plot_colormaps()

# %%
# Plot structured data using general plot methods
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
#rpc.pcolormesh(da, ax=ax, data_type='bathymetry', skip=10)
#rpc.imshow(da, ax=ax, data_type='bathymetry', skip=10)
#rpc.contourf(da, ax=ax, data_type='bathymetry', skip=10)
#rpc.contour(da, ax=ax, data_type='bathymetry', skip=10)
#rpc.scatter(ds, ax=ax, data_type='bathymetry', skip=10)
#rpc.quiver(ds, ax=ax, data_type='bathymetry', skip=100)
#rpc.streamplot(ds, ax=ax, data_type='bathymetry', skip=100)
rpc.geometries(gdf_aoi, ax=ax, geometry_type='aoi')
#rpc.cartopy(ax=ax)
rpc.basemap(ax=ax, map_type='osm', extent_type='aoi')
ax.legend(loc='upper right')
fig.tight_layout()

# %%
# Plot unstructured data using general plot methods
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
#rpc.pcolormesh(uda, ax=ax, data_type='bathymetry')
#rpc.imshow(uda, ax=ax, data_type='bathymetry')
#rpc.contourf(uda, ax=ax, data_type='bathymetry')
#rpc.contour(uda, ax=ax, data_type='bathymetry')
rpc.scatter(uda, ax=ax, data_type='bathymetry')
rpc.geometries(gdf_aoi, ax=ax, geometry_type='aoi')
#rpc.cartopy(ax=ax)
rpc.basemap(ax=ax, map_type='satellite', extent_type='aoi2')
ax.legend(loc='upper right')
fig.tight_layout()

# %%
# Plot unstructured grid using general plot methods
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
rpc.grid(uda, ax=ax, geometry_type='grid')
rpc.geometries(gdf_aoi, ax=ax, geometry_type='aoi')
rpc.cartopy(ax=ax, extent_type='aoi2')
#rpc.basemap(ax=ax, map_type='satellite', extent_type='aoi2')
ax.legend(loc='upper right')
fig.tight_layout()

# %%
# Plot structured data using bathymetry method
fig, ax = rpc.bathymetry(da=da, gdf=gdf_aoi, extent_type='aoi1')
rpc.savefig(fig=fig, file_path=os.path.join(repo_path, 'project', 'bathymetry1.png'))

# %%
# Plot unstructured data using bathymetry method
fig, ax = rpc.bathymetry(da=uda, gdf=gdf_aoi, extent_type='aoi1')
rpc.savefig(fig=fig, file_path=os.path.join(repo_path, 'project', 'bathymetry2.png'))

# %%
# Plot structured data using pretty_grid method
fig, ax = rpc.pretty_grid(da=uda, gdf=gdf_aoi, extent_type='aoi1')
rpc.savefig(fig=fig, file_path=os.path.join(repo_path, 'project', 'grid.png'))

# %%
# Rescale the x and y dimensions
scale_factor = 0.00001
grids = uds.grids
grids2 = []
for grid in grids:
    print(type(grid))
    if isinstance(grid, xu.Ugrid1d):
        grid = xu.Ugrid1d(node_x=grid.node_x*scale_factor,
                          node_y=grid.node_y*scale_factor,
                          fill_value=grid.fill_value,
                          edge_node_connectivity=grid.edge_node_connectivity)    
    elif isinstance(grid, xu.Ugrid2d):
        grid = xu.Ugrid2d(node_x=grid.node_x*scale_factor,
                          node_y=grid.node_y*scale_factor,
                          fill_value=grid.fill_value,
                          face_node_connectivity=grid.face_node_connectivity,
                          edge_node_connectivity=grid.edge_node_connectivity)
    grids2.append(grid)

uds2 = xr.Dataset(uds.copy(deep=True))
uds2 = uds2.rename({'nmesh2d_node': 'mesh2d_nNodes',
                    'nmesh2d_edge': 'mesh2d_nEdges',
                    'nmesh2d_face': 'mesh2d_nFaces'})

uds2 = xu.UgridDataset(obj=uds2, grids=grids2)

uds2['mesh2d_flowelem_bl'].ugrid.plot.imshow()


# %%
uds['mesh2d_flowelem_bl'].ugrid.plot.imshow()

# %%
uds['mesh2d_flowelem_bl']

# %%
