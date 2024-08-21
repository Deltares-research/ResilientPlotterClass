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

    :param xy_unit_in:  x and y unit of the input data.
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
    else:
        xy_unit_out = xy_unit_in
    
    # Get the scale factor
    if xy_unit_in in SCALE_METRES.keys() and xy_unit_out in SCALE_METRES.keys():
        scale_factor = SCALE_METRES[xy_unit_out]/SCALE_METRES[xy_unit_in]
    elif xy_unit_in in SCALE_DEGREES.keys() and xy_unit_out in SCALE_DEGREES.keys():
        scale_factor = SCALE_DEGREES[xy_unit_out]/SCALE_DEGREES[xy_unit_in]
    else:
        scale_factor = 1

    # Return the scale factor and corresponding x and y unit
    return scale_factor, xy_unit_out

def _rescale_DataArray(da, scale_factor):
    """Rescale the x and y dimensions of a DataArray.

    :param da:           DataArray to rescale.
    :type da:            xr.DataArray
    :param scale_factor: Scale factor to rescale the x and y dimensions to.
    :type scale_factor:  float
    :return:             Rescaled DataArray
    :rtype:              xr.DataArray
    """
    
    # If scale factor is 1, return the original DataArray
    if scale_factor == 1:
        return da
    
    # Rescale the x and y dimensions
    x_coord = xr.DataArray(da['x'].values*scale_factor, dims=['x'], attrs=da['x'].attrs)
    y_coord = xr.DataArray(da['y'].values*scale_factor, dims=['y'], attrs=da['y'].attrs)

    # Assign the coordinate arrays to the DataArray
    da = da.assign_coords(x=x_coord, y=y_coord)

    # Return the rescaled DataArray
    return da

def _rescale_UgridDataArray(uda, scale_factor):
    """Rescale the x and y dimensions of a UgridDataArray.

    :param uda:          UgridDataArray to rescale.
    :type uda:           xugrid.UgridDataArray
    :param scale_factor: Scale factor to rescale the x and y dimensions to.
    :type scale_factor:  float
    :return:             Rescaled UgridDataArray
    :rtype:              xugrid.UgridDataArray
    """
    
    # If scale factor is 1, return the original UgridDataArray
    if scale_factor == 1:
        return uda

    # Rescale the x and y dimensions of the grid
    grid = xu.Ugrid2d(node_x=uda.grid.node_x*scale_factor,
                      node_y=uda.grid.node_y*scale_factor,
                      fill_value=uda.grid.fill_value,
                      face_node_connectivity=uda.grid.face_node_connectivity)

    # Rename the dimensions of the UgridDataArray if necessary (TODO: Make this more robust)
    if uda.dims[0] != 'mesh2d_nFaces':
        uda = uda.rename({uda.dims[0]: 'mesh2d_nFaces'})
    
    # Assign the coordinate arrays to the UgridDataArray
    uda = xu.UgridDataArray(obj=xr.DataArray(uda), grid=grid)
    
    # Return the rescaled UgridDataArray
    return uda

def _rescale_GeoDataFrame(gdf, scale_factor):
    """Rescale the x and y dimensions of a GeoDataFrame.

    :param gdf:          GeoDataFrame to rescale.
    :type gdf:           gpd.GeoDataFrame
    :param scale_factor: Scale factor to rescale the x and y dimensions to.
    :type scale_factor:  float
    :return:             Rescaled GeoDataFrame
    :rtype:              gpd.GeoDataFrame
    """

    # If scale factor is 1, return the original GeoDataFrame
    if scale_factor == 1:
        return gdf
    
    # Rescale the x and y dimensions
    gdf_rescaled = gdf.copy()
    gdf_rescaled['geometry'] = gdf_rescaled['geometry'].scale(xfact=scale_factor, yfact=scale_factor, zfact=1, origin=(0, 0))

    # Return the rescaled geodataframe
    return gdf_rescaled

def get_rescale_parameters(data=None, crs=None, xy_unit=None):
    """Get the scale factor, xlabel and ylabel for a DataArray, UgridDataArray or GeoDataFrame or a given coordinate reference system and unit.

    :param data:    DataArray, UgridDataArray or GeoDataFrame to rescale.
    :type data:     xr.DataArray or xugrid.UgridDataArray or gpd.GeoDataFrame
    :param crs:     Coordinate reference system of the data. If ``None``, the crs is determined automatically based on the input data.
    :type crs:      pyproj.CRS or rasterio.CRS or str, optional
    :param xy_unit: Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:  str, optional
    :return:        scale factor, xlabel, ylabel.
    :rtype:         float, str, str
    """

    # Get the coordiante reference system of the data
    if isinstance(data, xr.DataArray):
        crs = data.rio.crs
    elif isinstance(data, xu.UgridDataArray):
        crs = data.crs if 'crs' in data.attrs.keys() else crs
    elif isinstance(data, gpd.GeoDataFrame):
        crs = data.crs
    elif data is None:
        crs = crs
    else:
        raise ValueError('Data type not supported. Please provide a DataArray, UgridDataArray or GeoDataFrame.')
        
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
        raise ValueError('CRS type not supported. Please provide a pyproj.CRS, rasterio.CRS or str object.')

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
    """Rescale the x and y dimensions of a DataArray, UgridDataArray or GeoDataFrame.

    :param data:         DataArray, UgridDataArray or GeoDataFrame to rescale.
    :type data:          xr.DataArray or xugrid.UgridDataArray or gpd.GeoDataFrame
    :param scale_factor: Scale factor to rescale the x and y dimensions to.
    :type scale_factor:  float, optional
    :return:             Rescaled DataArray, UgridDataArray or GeoDataFrame, xlabel, ylabel.
    :rtype:              xr.DataArray or xugrid.UgridDataArray or gpd.GeoDataFrame
    """

    # Rescale the datas
    if isinstance(data, xr.DataArray):
        data = _rescale_DataArray(data, scale_factor)
    elif isinstance(data, xu.UgridDataArray):
        data = _rescale_UgridDataArray(data, scale_factor)
    elif isinstance(data, gpd.GeoDataFrame):
        data = _rescale_GeoDataFrame(data, scale_factor)
    else:
        raise ValueError('Data type not supported. Please provide a DataArray, UgridDataArray or GeoDataFrame.')
    
    # Return the rescaled data
    return data