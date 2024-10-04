import geopandas as gpd
from shapely.geometry import Point
import xarray as xr
import xugrid as xu
import numpy as np

def reproject_xugrid(uda, crs, **kwargs):
    """Reproject data.

    :param uda:    Data to reproject.
    :type uda:     xugrid.UgridDataArray or xugrid.UgridDataSet
    :param crs:    Coordinate reference system.
    :type crs:     str
    :param kwargs: Keyword arguments for :func:`geopandas.GeoDataFrame.to_crs`.
    :type kwargs:  dict
    :return:       Reprojected data.
    :rtype:        xugrid.UgridDataArray or xugrid.UgridDataSet

    See also: `geopandas.GeoDataFrame.to_crs <https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html>`_.
    """

    def _reproject_grid(grid, crs, **kwargs):
        # Convert the grid to a GeoDataFrame
        gdf_grid = gpd.GeoDataFrame(geometry=[Point(x, y) for x, y in zip(grid.node_x, grid.node_y)], crs=grid.crs)

        # Reproject the grid
        gdf_grid = gdf_grid.to_crs(crs, **kwargs)

         # Set the x and y coordinates of 1D grid
        if isinstance(grid, xu.Ugrid1d):
            grid = xu.Ugrid1d(node_x=gdf_grid.geometry.x,
                              node_y=gdf_grid.geometry.y,
                              fill_value=grid.fill_value,
                              edge_node_connectivity=grid.edge_node_connectivity)

        # Set x and y coordinates of 2D grid  
        elif isinstance(grid, xu.Ugrid2d):
            grid = xu.Ugrid2d(node_x=gdf_grid.geometry.x,
                              node_y=gdf_grid.geometry.y,
                              fill_value=grid.fill_value,
                              face_node_connectivity=grid.face_node_connectivity,
                              edge_node_connectivity=grid.edge_node_connectivity)

        # Return the reprojected grid
        return grid
    
    def _rename_dims(da):
        # Define the new dimension names
        NEW_DIMS_1D = {'node':'network1d_nNodes', 'edge':'network1d_nEdges', 'face':'network1d_nFaces',
                       'Node':'network1d_nNodes', 'Edge':'network1d_nEdges', 'Face':'network1d_nFaces'}
        NEW_DIMS_2D = {'node':'mesh2d_nNodes', 'edge':'mesh2d_nEdges', 'face':'mesh2d_nFaces',
                       'Node':'mesh2d_nNodes', 'Edge':'mesh2d_nEdges', 'Face':'mesh2d_nFaces'}
        
        # Get the new dimension names
        if isinstance(da.grid, xu.Ugrid1d):
            NEW_DIMS = NEW_DIMS_1D
        elif isinstance(da.grid, xu.Ugrid2d):
            NEW_DIMS = NEW_DIMS_2D

        # Rename the dimensions of the data
        for dim in list(da.dims):
            for new_dim in NEW_DIMS.keys():
                if new_dim in dim:
                    da = da.rename({dim: NEW_DIMS[new_dim]})
        
        # Return the renamed data
        return da

    # Assign the coordinate arrays to the data
    if isinstance(uda, xu.UgridDataArray):
        grid = _reproject_grid(uda.grid, crs, **kwargs)
        uda_rescaled = xu.UgridDataArray(obj=xr.DataArray(uda), grid=grid)
    elif isinstance(uda, xu.UgridDataset):
        grids = [_reproject_grid(grid, crs, **kwargs) for grid in uda.grids]
        uda_rescaled = xu.UgridDataset(obj=xr.Dataset(uda), grids=grids)

    # Rename the dimensions of the data
    uda_rescaled = _rename_dims(uda_rescaled)
    
    # Set the coordinate reference system
    uda_rescaled.grid.set_crs(crs)

    # Return the reprojected data
    return uda_rescaled

def rasterise_xugrid(uda, da=None, **kwargs):
    """Rasterise data.

    :param uda:    Data to rasterise.
    :type uda:     xugrid.UgridDataSet
    :param da:     Data array to rasterise data on.
    :type da:      xarray.DataArray, optional
    :param kwargs: Keyword arguments for :func:`xugrid.Ugrid.grid.rasterize`.
    :type kwargs:  dict, optional
    :return:       Rasterised data.
    :rtype:        xarray.DataArray

    See also: `xugrid.Ugrid.grid.rasterize <https://xugrid.readthedocs.io/en/stable/api/xugrid.Ugrid.html#xugrid.Ugrid.grid.rasterize>`_.
    """

    # Create data array with grid indices
    if da is not None:
        x, y, zG = uda.grid.rasterize_like(da.x, da.y)
    else:
        x, y, zG = uda.grid.rasterize(**kwargs)
    da_grid = xr.DataArray(zG, dims=['y', 'x'], coords={'y': y, 'x': x})
    da_grid = da_grid.where(da_grid != -1)

    # Initialise data array with data
    da_data = da_grid.copy(deep=True)
    da_data.values = da_data.values * np.nan

    # Get dimension to rasterise
    dim = uda.dims[0]

    # Get indices of dimension
    idxs = list(set(da_grid.values.flatten()))
    
    # Rasterise data
    for idx in idxs:
        # Get x and y coordinates of index
        idx_xy = np.where(da_grid.values == idx)

        # Skip if no data
        if len(idx_xy[0]) == 0:
            continue
        
        # Set value
        da_data[idx_xy] = uda.sel({dim: idx})

    # Set coordinate reference system
    da_data = da_data.rio.write_crs(uda.grid.crs)

    # Return the rasterised data
    return da_data