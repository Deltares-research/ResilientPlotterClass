import numpy as np
import geopandas as gpd
from pyproj import CRS as pyprojCRS
import xarray as xr
import xugrid as xu
from rasterio.crs import CRS as rasterioCRS

def _get_xy_attrs_from_crs(crs=None):
    """Get the x and y attributes for a coordinate reference system.

    :param crs: Coordinate reference system.
    :type crs:  pyproj.CRS, optional
    :return:    x and y attributes.
    :rtype:     dict, dict
    """
    # Define abbreviations for x and y long names and unit
    XY_NAME_ABRIVIATIONS = {'Geodetic latitude':'Latitude', 'Geodetic longitude':'Longitude'}
    XY_UNIT_ABRIVIATIONS = {'millimeter':'mm', 'decimeter':'dm', 'centimeter':'cm', 'meter':'m',
                            'decameter':'dam', 'hectometer':'hm', 'kilometer':'km',
                            'millimetre':'mm', 'decimetre':'dm', 'centimetre':'cm', 'metre':'m',
                            'decametre':'dam', 'hectometre':'hm', 'kilometre':'km',
                            'degree':'deg', 'arcsecond':'arcsec', 'arcminute':'arcmin','radian':'rad',
                            'foot':'ft', 'inch':'in', 'yard':'yd', 'mile':'mi', 'nautical mile':'nmi'}
    
    # Convert the crs to a pyproj.CRS object
    if crs is None:
        x_attrs = {'long_name':'x', 'unit':'-'}
        y_attrs = {'long_name':'y', 'unit':'-'}
        return x_attrs, y_attrs
    
    # Get the x and y axis names
    x_axis_name = crs.axis_info[0].name
    y_axis_name = crs.axis_info[1].name

    # Abbreviate the axis names
    x_axis_name = XY_NAME_ABRIVIATIONS[x_axis_name] if x_axis_name in XY_NAME_ABRIVIATIONS.keys() else x_axis_name
    y_axis_name = XY_NAME_ABRIVIATIONS[y_axis_name] if y_axis_name in XY_NAME_ABRIVIATIONS.keys() else y_axis_name

    # Set the x and y long names
    x_long_name = '{} {}'.format(x_axis_name, crs.name)
    y_long_name = '{} {}'.format(y_axis_name, crs.name)

    # Get the x and y unit
    xy_unit = crs.axis_info[0].unit_name    

    # Abbreviate the x and y unit
    xy_unit = XY_UNIT_ABRIVIATIONS[xy_unit] if xy_unit in XY_UNIT_ABRIVIATIONS.keys() else xy_unit

    # Set the x and y attributes
    x_attrs = {'long_name':x_long_name, 'unit':xy_unit}
    y_attrs = {'long_name':y_long_name, 'unit':xy_unit}

    # Return the x and y attributes
    return x_attrs, y_attrs

def _get_scale_factor(xy_unit_in, xy_unit_out=None):
    """Get the scale factor and corresponding x and y unit.

    :param xy_unit_in:  x and y unit of the data.
    :type xy_unit_in:   str
    :param xy_unit_out: x and y unit of the output data. If ``None``, default x and y units are used.
    :type xy_unit_out:  str, optional
    :return:            x and y unit of the output data, scale factor.
    :rtype:             float
    """

    # Define the scale factors
    SCALE_METRES = {'mm':1000, 'cm':100, 'dm':10, 'm':1, 'dam':0.1, 'hm':0.01, 'km':0.001,
                    'ft':3.28084, 'in':39.3701, 'yd':1.09361, 'mi':0.000621371, 'nmi':0.000539957}
    SCALE_DEGREES = {'deg':1, 'arcsec':3600, 'arcmin':60, 'rad':np.pi/180}

    # Get the x and y unit
    if xy_unit_out is None and xy_unit_in in SCALE_METRES:
        xy_unit_out = 'km'
    elif xy_unit_out is None and xy_unit_in in SCALE_DEGREES:
        xy_unit_out = 'deg'
    elif xy_unit_out is None:
        xy_unit_out = xy_unit_in
    else:
        xy_unit_out = xy_unit_out
    
    # Get the scale factor
    if xy_unit_in in SCALE_METRES.keys() and xy_unit_out in SCALE_METRES.keys():
        scale_factor = SCALE_METRES[xy_unit_out]/SCALE_METRES[xy_unit_in]
    elif xy_unit_in in SCALE_DEGREES.keys() and xy_unit_out in SCALE_DEGREES.keys():
        scale_factor = SCALE_DEGREES[xy_unit_out]/SCALE_DEGREES[xy_unit_in]
    else:
        scale_factor = 1

    # Return the scale factor and corresponding x and y unit
    return scale_factor, xy_unit_out

def _rescale_xarray(da, scale_factor):
    """Rescale the x and y dimensions of a DataArray or Dataset.

    :param da:           Data to rescale.
    :type da:            xarray.DataArray or xarray.Dataset
    :param scale_factor: Scale factor to rescale the x and y dimensions to.
    :type scale_factor:  float
    :return:             Rescaled data
    :rtype:              xarray.DataArray or xarray.Dataset
    """
    
    # If scale factor is 1, return the original data
    if scale_factor == 1:
        return da
    
    # Rescale the x and y dimensions
    x_coord = xr.DataArray(da['x'].values*scale_factor, dims=['x'], attrs=da['x'].attrs)
    y_coord = xr.DataArray(da['y'].values*scale_factor, dims=['y'], attrs=da['y'].attrs)

    # Assign the coordinate arrays to the data
    da = da.assign_coords(x=x_coord, y=y_coord)

    # Return the rescaled data
    return da

def _rescale_xugrid(uda, scale_factor):
    """Rescale the x and y dimensions of a UgridDataArray or UgridDataset.

    :param uda:          Data to rescale.
    :type uda:           xugrid.UgridDataArray or xugrid.UgridDataset
    :param scale_factor: Scale factor to rescale the x and y dimensions to.
    :type scale_factor:  float
    :return:             Rescaled data
    :rtype:              xugrid.UgridDataArray
    """
    
    # If scale factor is 1, return the original UgridDataArray
    if scale_factor == 1:
        return uda

    # Function to rescale the grid
    def _rescale_grid(grid, scale_factor):
        # Rescale the x and y dimensions of 1D grid
        if isinstance(grid, xu.Ugrid1d):
            grid = xu.Ugrid1d(node_x=grid.node_x*scale_factor,
                              node_y=grid.node_y*scale_factor,
                              fill_value=grid.fill_value,
                              edge_node_connectivity=grid.edge_node_connectivity)

        # Rescale x and y dimensions of 2D grid  
        elif isinstance(grid, xu.Ugrid2d):
            grid = xu.Ugrid2d(node_x=grid.node_x*scale_factor,
                              node_y=grid.node_y*scale_factor,
                              fill_value=grid.fill_value,
                              face_node_connectivity=grid.face_node_connectivity,
                              edge_node_connectivity=grid.edge_node_connectivity)
        
        # Return rescaled grid
        return grid
    
    # Function to rename the dimensions of the data
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
        for dim in list(da.indexes):
            for new_dim in NEW_DIMS.keys():
                if new_dim in dim:
                    da = da.rename({dim: NEW_DIMS[new_dim]})
        
        # Return the renamed data
        return da
    
    # Rename the dimensions of the data
    da = _rename_dims(uda)
    
    # Assign the coordinate arrays to the data
    if isinstance(uda, xu.UgridDataArray):
        grid = _rescale_grid(uda.grid, scale_factor)
        uda = xu.UgridDataArray(obj=xr.DataArray(da), grid=grid)
    elif isinstance(uda, xu.UgridDataset):
        grids = [_rescale_grid(grid, scale_factor) for grid in uda.grids]
        uda = xu.UgridDataset(obj=xr.Dataset(da), grids=grids)
    
    # Return the rescaled data
    return uda

def _rescale_GeoDataFrame(gdf, scale_factor):
    """Rescale the x and y dimensions of a GeoDataFrame.

    :param gdf:          Geometries to rescale.
    :type gdf:           geopandas.GeoDataFrame
    :param scale_factor: Scale factor to rescale the x and y dimensions to.
    :type scale_factor:  float
    :return:             Rescaled geometries
    :rtype:              geopandas.GeoDataFrame
    """

    # If scale factor is 1, return the original geometries
    if scale_factor == 1:
        return gdf
    
    # Rescale the x and y dimensions 
    gdf_rescaled = gdf.copy()
    gdf_rescaled['geometry'] = gdf_rescaled['geometry'].scale(xfact=scale_factor, yfact=scale_factor, zfact=1, origin=(0, 0))

    # Return the rescaled geometries
    return gdf_rescaled

def get_rescale_parameters(data=None, crs=None, xy_unit=None):
    """Get the scale factor, xlabel and ylabel for data, geometries or a coordinate reference system and unit.

    :param data:    Data or geometries to rescale. If ``None``, the crs is used to determine the rescale parameters.
    :type data:     xarray.DataArray, xarray.Dataset, xugrid.UgridDataArray, xugrid.UgridDataset, geopandas.GeoDataFrame, optional
    :param crs:     Coordinate reference system of the data. If ``None``, the crs is determined automatically based on the data.
    :type crs:      pyproj.CRS or rasterio.CRS or str, optional
    :param xy_unit: Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the data.
    :type xy_unit:  str, optional
    :return:        Scale factor, xlabel, ylabel.
    :rtype:         tuple[float, str, str]
    """
    
    # Get the coordiante reference system of the data
    if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset):
        crs = data.rio.crs
    elif isinstance(data, xu.UgridDataArray) or isinstance(data, xu.UgridDataset):
        crs = data.grid.crs
    elif isinstance(data, gpd.GeoDataFrame):
        crs = data.crs
    elif data is None:
        crs = crs
    else:
        raise TypeError('data type not supported. Please provide a xarray.DataArray, xarray.Dataset, xugrid.UgridDataArray, xugrid.UgridDataset or geopandas.GeoDataFrame.')
        
    # Convert the crs to a pyproj.CRS
    if isinstance(crs, pyprojCRS):
        crs = crs
    elif isinstance(crs, rasterioCRS):
        crs = pyprojCRS.from_string(crs.to_string())
    elif isinstance(crs, str):
        crs = pyprojCRS.from_string(crs)
    elif crs is None:
        crs = crs
    else:
        raise TypeError('crs type not supported. Please provide a pyproj.CRS, rasterio.CRS or str object.')

    # Get x and y attributes and unit
    x_attrs, y_attrs = _get_xy_attrs_from_crs(crs)

    # Get the scale factor and corresponding x and y unit
    scale_factor, xy_unit_out = _get_scale_factor(xy_unit_in=x_attrs['unit'], xy_unit_out=xy_unit)

    # Get labels for the x and y dimensions
    xlabel = '{} [{}]'.format(x_attrs['long_name'], xy_unit_out)
    ylabel = '{} [{}]'.format(y_attrs['long_name'], xy_unit_out)

    # Return the scale factor, xlabel, ylabel
    return scale_factor, xlabel, ylabel

def rescale(data, scale_factor=1):
    """Rescale the x and y dimensions of data or geometries.

    :param data:         Data or geometries to rescale.
    :type data:          xr.DataArray or xugrid.UgridDataArray or gpd.GeoDataFrame
    :param scale_factor: Scale factor to rescale the x and y dimensions to.
    :type scale_factor:  float, optional
    :return:             Rescaled data or geometries
    :rtype:              xarray.DataArray, xarray.Dataset, xugrid.UgridDataArray, xugrid.UgridDataset, geopandas.GeoDataFrame
    """

    # Rescale the datas
    if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset):
        data = _rescale_xarray(data, scale_factor)
    elif isinstance(data, xu.UgridDataArray) or isinstance(data, xu.UgridDataset):
        data = _rescale_xugrid(data, scale_factor)
    elif isinstance(data, gpd.GeoDataFrame):
        data = _rescale_GeoDataFrame(data, scale_factor)
    else:
        raise TypeError('data type not supported. Please provide a xarray.DataArray, xarray.Dataset, xugrid.UgridDataArray, xugrid.UgridDataset or geopandas.GeoDataFrame.')
    
    # Return the rescaled data
    return data