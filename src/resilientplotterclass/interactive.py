import geopandas as gpd
import holoviews as hv
import holoviews.operation.datashader as hd
import hvplot.pandas
import hvplot.xarray
from pyproj import CRS as pyprojCRS
from rasterio.crs import CRS as rasterioCRS
import resilientplotterclass as rpc
import xarray as xr
import xugrid as xu

def _get_georeference_bool(data=None, crs=None):
    """Check if the data is georeferenced in WGS 84 (EPSG:4326).

    :param data:    Data or geometries to rescale. If ``None``, the crs is used to determine the rescale parameters.
    :type data:     xarray.DataArray, xarray.Dataset, xugrid.UgridDataArray, xugrid.UgridDataset, geopandas.GeoDataFrame, optional
    :param crs:     Coordinate reference system of the data. If ``None``, the crs is determined automatically based on the data.
    :type crs:      pyproj.CRS or rasterio.CRS or str, optional
    :return:        Boolean indicating if the data is georeferenced in WGS 84 (EPSG:4326).
    :rtype:         bool
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
    
    # Check if the data is georeferenced
    if crs == pyprojCRS.from_epsg(4326):
        return True
    else:
        return False

def interactive_da(da, xy_unit=None, **kwargs):
    """Plot data as an interactive plot.

    :param da:      DataArray to plot.
    :type da:       xarray.DataArray
    :param xy_unit: Unit of the x and y coordinates. If ``None``, the unit is determined automatically based on the data.
    :type xy_unit:  str, optional
    :param kwargs:  Keyword arguments for :func:`holoviews.opts`.
    :type kwargs:   dict, optional
    :return:        Interactive plot.
    :rtype:         holoviews.core.spaces.DynamicMap

    See also: `holoviews.element.raster.Raster <https://holoviews.org/reference/elements/bokeh/Raster.html>`_,
              `holoviews.opts <https://holoviews.org/user_guide/Customizing_Plots.html>`_.
    """

    # Get the rescale parameters
    scale_factor, xlabel, ylabel = rpc.rescale.get_rescale_parameters(data=da, xy_unit=xy_unit)
    
    # Rescale the DataArray
    da = rpc.rescale.rescale(data=da, scale_factor=scale_factor)

    # Get x and y dimensions
    x = kwargs.pop('x', da.dims[1])
    y = kwargs.pop('y', da.dims[0])

    # Check if the DataArray is georeferenced
    geo = _get_georeference_bool(data=da)

    # Get the label
    label = kwargs.pop('label', '')

    # Get the colorbar label
    if 'long_name' in da.attrs and 'units' in da.attrs:
        kwargs.setdefault('clabel', '{} [{}]'.format(da.attrs['long_name'], da.attrs['units']))
        
    # Plot the DataArray
    da_plot = hd.rasterize(da.hvplot(x=x, y=y, geo=geo, label=label)).opts(**kwargs)

    # Format the plot
    da_plot = da_plot.opts(width=550, height=550, xlabel=xlabel, ylabel=ylabel, title='', aspect='equal', show_grid=True, active_tools=['pan', 'wheel_zoom'])
    
    # Return the plot
    return da_plot

def interactive_uda(uda, xy_unit=None, **kwargs):
    pass

def interactive_gdf(gdf, xy_unit=None, **kwargs):
    """Plot GeoDataFrame as an interactive plot.

    :param gdf:     GeoDataFrame to plot.
    :type gdf:      geopandas.GeoDataFrame
    :param xy_unit: Unit of the x and y coordinates. If ``None``, the unit is determined automatically based on the data.
    :type xy_unit:  str, optional
    :param kwargs:  Keyword arguments for :func:`holoviews.opts`.
    :type kwargs:   dict, optional
    :return:        Interactive plot.
    :rtype:         holoviews.element.path.Polygons

    See also: `holoviews.element.path.Polygons <https://holoviews.org/reference/elements/bokeh/Polygons.html>`_,
              `holoviews.opts <https://holoviews.org/user_guide/Customizing_Plots.html>`_.
    """

    # Get the rescale parameters
    scale_factor, xlabel, ylabel = rpc.rescale.get_rescale_parameters(data=gdf, xy_unit=xy_unit)
    
    # Rescale the GeoDataFrame
    gdf = rpc.rescale.rescale(data=gdf, scale_factor=scale_factor)

    # Check if the GeoDataFrame is georeferenced
    geo = _get_georeference_bool(data=gdf)

    # Get the column
    c = kwargs.pop('c', None)
        
    # Get the label
    label = kwargs.pop('label', '')

 
    # Plot the GeoDataFrame
    gdf_plot = gdf.hvplot(geo=geo, c=c, label=label).opts(**kwargs)
    
    # Format the plot
    gdf_plot = gdf_plot.opts(width=550, height=550, xlabel=xlabel, ylabel=ylabel, title='', aspect='equal', show_grid=True, active_tools=['pan', 'wheel_zoom'])
    
    # Return the plot
    return gdf_plot

def interactive_gdf_cartopy(gdf, xy_unit=None, **kwargs):
    """Plot GeoDataFrame with cartopy geometries as an interactive plot.

    :param gdf:     GeoDataFrame with cartopy geometries to plot.
    :type gdf:      geopandas.GeoDataFrame
    :param xy_unit: Unit of the x and y coordinates. If ``None``, the unit is determined automatically based on the data.
    :type xy_unit:  str, optional
    :param kwargs:  Keyword arguments for :func:`holoviews.opts`.
    :type kwargs:   dict, optional
    :return:        Interactive plot.
    :rtype:         holoviews.core.overlay.Overlay

    See also: `holoviews.core.overlay.Overlay <https://holoviews.org/reference/containers/bokeh/Overlay.html>`_,
              `holoviews.opts <https://holoviews.org/user_guide/Customizing_Plots.html>`_.
    """

    # Get the rescale parameters
    scale_factor, xlabel, ylabel = rpc.rescale.get_rescale_parameters(data=gdf, xy_unit=xy_unit)
    
    # Rescale the GeoDataFrame
    gdf = rpc.rescale.rescale(data=gdf, scale_factor=scale_factor)

    # Seperate and explode cartopy geometries
    gdf_land = gpd.GeoDataFrame(geometry=[geom for geom in gdf.loc['land', 'geometry'].geoms]) if 'land' in gdf.index else None
    gdf_ocean = gpd.GeoDataFrame(geometry=[geom for geom in gdf.loc['ocean', 'geometry'].geoms]) if 'ocean' in gdf.index else None
    gdf_lakes = gpd.GeoDataFrame(geometry=[geom for geom in gdf.loc['lakes', 'geometry'].geoms]) if 'lakes' in gdf.index else None
    gdf_coastline = gpd.GeoDataFrame(geometry=[geom for geom in gdf.loc['coastline', 'geometry'].geoms]) if 'coastline' in gdf.index else None
    gdf_states = gpd.GeoDataFrame(geometry=[geom for geom in gdf.loc['states', 'geometry'].geoms]) if 'states' in gdf.index else None

    # Check if the GeoDataFrame is georeferenced
    geo = _get_georeference_bool(gdf)
    
    # Plot the cartopy geometries
    cartopy_plots = []
    if gdf_ocean is not None:
        kwargs_ = {**{'color': 'lightblue', 'line_color': 'none'}, **kwargs}
        cartopy_plots.append(gdf_ocean.hvplot(geo=geo).opts(**kwargs_))
    if gdf_land is not None:
        kwargs_ = {**{'color': 'antiquewhite', 'line_color': 'none'}, **kwargs}
        cartopy_plots.append(gdf_land.hvplot(geo=geo).opts(**kwargs_))
    if gdf_lakes is not None:
        kwargs_ = {**{'color': 'lightblue', 'line_color': 'none'}, **kwargs}
        cartopy_plots.append(gdf_lakes.hvplot(geo=geo).opts(**kwargs_))
    if gdf_coastline is not None:
        kwargs_ = {**{'color': 'black', 'line_width': 1, 'line_dash': 'solid'}, **kwargs}
        cartopy_plots.append(gdf_coastline.hvplot(geo=geo).opts(**kwargs_))
    if gdf_states is not None:
        kwargs_ = {**{'color': 'none', 'line_width': 1, 'line_dash': 'dotted'}, **kwargs}
        cartopy_plots.append(gdf_states.hvplot(geo=geo).opts(**kwargs_))
    
    # Combine the plots
    for cartopy_plot in cartopy_plots:
        cartopy_plot = cartopy_plot.opts(width=550, height=550, xlabel=xlabel, ylabel=ylabel, title='', aspect='equal', show_grid=True, active_tools=['pan', 'wheel_zoom'])
    cartopy_plot = hv.Overlay(cartopy_plots)

    # Format the plot
    cartopy_plot = cartopy_plot.opts(width=550, height=550, xlabel=xlabel, ylabel=ylabel, title='', aspect='equal', show_grid=True, active_tools=['pan', 'wheel_zoom'])
    
    # Return the plot
    return cartopy_plot

def interactive_basemap(map_type, **kwargs):
    """Plot an interactive basemap.

    :param map_type: Type of the basemap to plot.
    :type map_type:  str, optional
    :param kwargs:   Keyword arguments for :func:`holoviews.opts`.
    :type kwargs:    dict, optional
    :return:         Interactive basemap.
    :rtype:          holoviews.element.tiles.WMTS

    See also: `holoviews.element.tiles.tile_sources <https://holoviews.org/reference/elements/bokeh/Tiles.html>`_,
              `holoviews.opts <https://holoviews.org/user_guide/Customizing_Plots.html>`_.
    """

    # Plot the basemap
    basemap_plot = hv.element.tiles.tile_sources[map_type]().opts(**kwargs)

    # Format the plot
    basemap_plot = basemap_plot.opts(width=550, height=550, title='', aspect='equal', show_grid=True, active_tools=['pan', 'wheel_zoom'])
    
    # Return the plot
    return basemap_plot
