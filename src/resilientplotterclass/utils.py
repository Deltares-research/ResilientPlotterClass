import geopandas as gpd
from shapely.geometry import Point
import xarray as xr
import xugrid as xu
import numpy as np
from resilientplotterclass.rescale import _rescale_xugrid

# Function to rename the dimensions of the data
def _rename_xugrid(uda):
    """Rename dimensions of data.

    :param uda: Data to rename dimensions.
    :type uda:  xugrid.UgridDataArray or xugrid.UgridDataset
    :return:    Standardised data.
    :rtype:     xugrid.UgridDataArray or xugrid.UgridDataset
    """

    # Use rescale xugrid function with scale factor 1
    uda_renamed = _rescale_xugrid(uda, 1)

    # Return the standardised data
    return uda_renamed

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

    # Assign the coordinate arrays to the data
    if isinstance(uda, xu.UgridDataArray):
        grid = _reproject_grid(uda.grid, crs, **kwargs)
        uda_rescaled = xu.UgridDataArray(obj=xr.DataArray(uda), grid=grid)
    elif isinstance(uda, xu.UgridDataset):
        grids = [_reproject_grid(grid, crs, **kwargs) for grid in uda.grids]
        uda_rescaled = xu.UgridDataset(obj=xr.Dataset(uda), grids=grids)

    # Rename the dimensions of the data
    uda_rescaled = _rename_xugrid(uda_rescaled)
    
    # Set the coordinate reference system
    uda_rescaled.grid.set_crs(crs)

    # Return the reprojected data
    return uda_rescaled

def rasterise_uds(uds, ds=None, bounds=None, resolution=None):
    """Rasterise data.

    :param uds:        Data to rasterise.
    :type uds:         xugrid.UgridDataSet or xugrid.UgridDataArray
    :param ds:         Data to rasterise data on.
    :type ds:          xarray.DataSet or xarray.DataArray, optional
    :param bounds:     Bounds of the rasterised data.
    :type bounds:      tuple, optional
    :param resolution: Resolution of the rasterised data.
    :type resolution:  float, optional
    :return:           Rasterised data.
    :rtype:            xarray.DataArray
    """
       
    # Get x and y coordinates
    if ds is not None:
        xs = ds['x']
        ys = ds['y']
    elif bounds is not None and resolution is not None:
        xmin, ymin, xmax, ymax = bounds
        xs = np.linspace(xmin, xmax, int((xmax - xmin) / resolution) + 1)
        ys = np.linspace(ymin, ymax, int((ymax - ymin) / resolution) + 1)
    else:
        raise ValueError('Either ds or bounds and resolution should be provided.')
    
    # Create x and y grids
    xG, yG = np.meshgrid(xs, ys)

    # Rename the dimensions of the data
    uds = _rename_xugrid(uds)
    
    # Remove data variables that do not have nmesh2d_face dimension
    if isinstance(uds, xu.UgridDataset):
        for var in uds.data_vars:
            if 'mesh2d_nFaces' not in uds[var].dims:
                uds = uds.drop_vars(var)

    # Remove coordinates that contain _index, _x, or _y
    for coord in uds.coords:
        if '_index' in coord or '_x' in coord or '_y' in coord:
            uds = uds.drop_vars(coord)

    # Remove dimensions that contain nodes or edges
    for dim in uds.dims:
        if 'node' in dim or 'edge' in dim or 'Node' in dim or 'Edge' in dim:
            uds = uds.drop_dims(dim)
    
    # Get dataset
    ds = uds.ugrid.sel_points(x=xG.flatten(), y=yG.flatten(), out_of_bounds='ignore')
    
    # Remove mesh2d_ from data variables
    if isinstance(ds, xu.UgridDataset):
        for var in ds.data_vars:
            if 'mesh2d_' in var:
                ds = ds.rename({var: var.replace('mesh2d_', '')})
    
    # Remove coordinates that contain _index, _x, or _y
    for coord in ds.coords:
        if '_index' in coord or '_x' in coord or '_y' in coord:
            ds = ds.drop_vars(coord)

    # Replace mesh2d_nFaces dimension with idx dimension
    ds = ds.rename({'mesh2d_nFaces': 'idx'})
    ds['idx'] = range(len(ds['idx']))

    # Add x, and y coordinates
    ds = ds.assign_coords(x=('idx', xG.flatten()), y=('idx', yG.flatten()))

    # Set index
    ds = ds.set_index(idx=('x', 'y'))

    # Unstack index
    ds = ds.unstack('idx')

    # Transpose dimensions
    ds = ds.transpose('y', 'x', ...)
    
    # Set coordinate reference system
    ds = ds.rio.write_crs(uds.grid.crs)

    # Return the rasterised data
    return ds
