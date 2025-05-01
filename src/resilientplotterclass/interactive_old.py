from cartopy import crs as cartopyCRS
import geopandas as gpd
import holoviews as hv
import holoviews.operation.datashader as hd
import hvplot.pandas
import hvplot.xarray
import pandas as pd
import panel as pn
from pyproj import CRS as pyprojCRS
from rasterio.crs import CRS as rasterioCRS
import resilientplotterclass as rpc
from shapely.geometry import box, MultiPolygon, Polygon, MultiLineString, LineString, MultiPoint, Point
import xarray as xr
import xugrid as xu

# Set streams
def set_streams(self, streams=None):
    """Set stream geometries.

    :param streams: Dictionary with streams.
    :type streams:  dict[str, hv.streams.Stream], optional
    :return:        None.
    :rtype:         None
    """

    # Set streams
    self.streams = streams

def get_streams(self):
    """Get stream geometries.

    :return: Stream geometries.
    :rtype:  geopandas.GeoDataFrame
    """

    # Get stream geometries
    gdf_streams = rpc.interactive.get_gdf_streams(self.streams, crs=self.guidelines['general']['crs'])

    # Return stream geometries
    return gdf_streams


def add_streams(fig, stream_types=['boxes', 'polygons', 'lines', 'freehand', 'points']):
    # Define stream styles
    STREAMS_KWARGS = {'boxes':{'fill_color':None, 'line_color':'purple', 'line_width':3},
                      'polygons':{'fill_color':None, 'line_color':'blue', 'line_width':3},
                      'lines':{'line_color':'green', 'line_width':3},
                      'freehand':{'line_color':'black', 'line_width':3},
                      'points':{'color':'red', 'size':5}}
    
    # Create streams and add them to the plot
    streams = {}
    if 'boxes' in stream_types:
        boxes = hv.Rectangles([]).opts(**STREAMS_KWARGS['boxes'])
        streams['boxes'] = hv.streams.BoxEdit(source=boxes)
        fig = fig * boxes
    if 'polygons' in stream_types:
        polygons = hv.Polygons([]).opts(**STREAMS_KWARGS['polygons'])
        streams['polygons'] = hv.streams.PolyDraw(source=polygons)
        fig = fig * polygons
    if 'lines' in stream_types:
        lines = hv.Path([]).opts(**STREAMS_KWARGS['lines'])
        streams['lines'] = hv.streams.PolyDraw(source=lines, tooltip='Line Draw Tool')
        fig = fig * lines
    if 'freehand' in stream_types:
        freehand = hv.Path([]).opts(**STREAMS_KWARGS['freehand'])
        streams['freehand'] = hv.streams.FreehandDraw(source=freehand)
        fig = fig * freehand
    if 'points' in stream_types:
        points = hv.Points([]).opts(**STREAMS_KWARGS['points'])
        streams['points'] = hv.streams.PointDraw(source=points)
        fig = fig * points

    # Return the plot
    return fig, streams

def get_gdf_streams(streams, crs):
    # Define stream styles
    STREAMS_KWARGS = {'boxes':{'facecolor':'none', 'edgecolor':'purple', 'linewidth':3, 'label':'Boxes'},
                      'polygons':{'facecolor':'none', 'edgecolor':'blue', 'linewidth':3, 'label':'Polygons'},
                      'lines':{'color':'green', 'linewidth':3, 'label':'Lines'},
                      'freehand':{'color':'black', 'linewidth':3, 'label':'Freehand'},
                      'points':{'color':'red', 'markersize':5, 'label':'Points'}}
    
    # Convert the crs to a pyproj.CRS
    if isinstance(crs, pyprojCRS):
        crs = crs
    elif isinstance(crs, rasterioCRS):
        crs = pyprojCRS.from_string(crs.to_string())
    elif isinstance(crs, str):
        crs = pyprojCRS.from_string(crs)
    elif crs is None:
        crs = 'EPSG:4326'
    else:
        raise ValueError('CRS type not supported. Please provide a pyproj.CRS, rasterio.CRS or str object.')
    
    # Get stream geometries
    gdf_streams_ls = []
    if streams is not None and 'boxes' in streams.keys() and streams['boxes'].data is not None and len(streams['boxes'].data['x0']) > 0:
        data = streams['boxes'].data
        boxes = MultiPolygon([box(x0, y0, x1, y1) for x0, y0, x1, y1 in zip(data['x0'], data['y0'], data['x1'], data['y1'])])
    else:
        boxes = MultiPolygon([])
    if streams is not None and 'polygons' in streams.keys() and streams['polygons'].data is not None and len(streams['polygons'].data['xs']) > 0:
        data = streams['polygons'].data
        polygons = MultiPolygon([Polygon([(lon,lat) for lon, lat in zip(lons, lats)]) for lons, lats in zip(data['xs'], data['ys'])])
    else:
        polygons = MultiPolygon([])
    if streams is not None and 'lines' in streams.keys() and streams['lines'].data is not None and len(streams['lines'].data['xs']) > 0:
        data = streams['lines'].data
        lines = MultiLineString([LineString([(lon,lat) for lon, lat in zip(lons, lats)]) for lons, lats in zip(data['xs'], data['ys'])])
    else:
        lines = MultiLineString([])
    if streams is not None and 'freehand' in streams.keys() and streams['freehand'].data is not None and len(streams['freehand'].data['xs']) > 0:
        data = streams['freehand'].data
        freehand = MultiLineString([LineString([(lon,lat) for lon, lat in zip(lons, lats)]) for lons, lats in zip(data['xs'], data['ys'])])
    else:
        freehand = MultiLineString([])
        gdf_streams_ls.append(gpd.GeoDataFrame({'geometry':freehand, 'kwargs':[STREAMS_KWARGS['freehand']]}, crs=cartopyCRS.GOOGLE_MERCATOR))    
    if streams is not None and 'points' in streams.keys() and streams['points'].data is not None and len(streams['points'].data['x']) > 0:
        data = streams['points'].data
        points = MultiPoint([Point(lon, lat) for lon, lat in zip(data['x'], data['y'])])
    else:
        points = MultiPoint([])

    # Create geodataframes
    gdf_boxes = gpd.GeoDataFrame({'geometry':boxes, 'kwargs':[STREAMS_KWARGS['boxes']]}, index=['boxes'], crs=cartopyCRS.GOOGLE_MERCATOR)
    gdf_polygons = gpd.GeoDataFrame({'geometry':polygons, 'kwargs':[STREAMS_KWARGS['polygons']]}, index=['polygons'], crs=cartopyCRS.GOOGLE_MERCATOR)
    gdf_lines = gpd.GeoDataFrame({'geometry':lines, 'kwargs':[STREAMS_KWARGS['lines']]}, index=['lines'], crs=cartopyCRS.GOOGLE_MERCATOR)
    gdf_freehand = gpd.GeoDataFrame({'geometry':freehand, 'kwargs':[STREAMS_KWARGS['freehand']]}, index=['freehand'], crs=cartopyCRS.GOOGLE_MERCATOR)
    gdf_points = gpd.GeoDataFrame({'geometry':points, 'kwargs':[STREAMS_KWARGS['points']]}, index=['points'], crs=cartopyCRS.GOOGLE_MERCATOR)

    # Combine geodataframes
    gdf_streams = gpd.GeoDataFrame(pd.concat([gdf_boxes, gdf_polygons, gdf_lines, gdf_freehand, gdf_points]), crs=cartopyCRS.GOOGLE_MERCATOR)

    # Drop empty geometries
    gdf_streams = gdf_streams[gdf_streams['geometry'].is_empty == False]

    # Reproject stream geometries
    gdf_streams = gdf_streams.to_crs(crs)

    # Return geodataframes
    return gdf_streams

def show_fig(fig, stream_types=[], **kwargs):
    # Add streams
    fig, streams = add_streams(fig, stream_types=stream_types)

    # Default keyword arguments
    kwargs.setdefault('width', 1920)
    kwargs.setdefault('height', 550)

    # Format the plot
    fig = fig.opts(**kwargs).opts(legend_position='top_right', click_policy='hide', active_tools=['pan', 'wheel_zoom'])

    # Create panel
    panel = pn.pane.HoloViews(fig, sizing_mode='stretch_width')

    # Return panel
    return panel, streams

def save_fig(fig, filename, stream_types=[], **kwargs):
    # Add streams
    fig, _ = add_streams(fig, stream_types=stream_types)

    # Default keyword arguments
    kwargs.setdefault('width', None)
    kwargs.setdefault('height', None)

    # Format the plot
    fig = fig.opts(**kwargs).opts(legend_position='top_right', click_policy='hide', active_tools=['pan', 'wheel_zoom'])
    
    # Create panel
    panel = pn.pane.HoloViews(fig, sizing_mode='stretch_both')

    # Save the plot
    panel.save(filename)

def pcolormesh(da, **kwargs):
    pass

def imshow(da, **kwargs):
    """Plot data using interactive plot.

    :param da:      DataArray to plot.
    :type da:       xarray.DataArray
    :param kwargs:  Keyword arguments for :func:`holoviews.opts`.
    :type kwargs:   dict, optional
    :return:        Interactive plot.
    :rtype:         holoviews.core.spaces.DynamicMap

    See also: `holoviews.element.raster.Raster <https://holoviews.org/reference/elements/bokeh/Raster.html>`_,
              `holoviews.opts <https://holoviews.org/user_guide/Customizing_Plots.html>`_.
    """

    # Default keyword arguments
    kwargs.setdefault('x', da.dims[1])
    kwargs.setdefault('y', da.dims[0])
    kwargs.setdefault('xaxis', None)
    kwargs.setdefault('yaxis', None)
    kwargs.setdefault('xlabel', None)
    kwargs.setdefault('ylabel', None)
    kwargs.setdefault('title', None)
    kwargs.setdefault('grid', True)
    kwargs.setdefault('geo', True)
    
    # Get the colorbar label
    if 'long_name' in da.attrs and 'units' in da.attrs:
        kwargs.setdefault('clabel', '{} [{}]'.format(da.attrs['long_name'], da.attrs['units']))
        
    # Plot the DataArray
    p = da.hvplot(**kwargs)

    # Return the plot
    return p

def scatter(da, **kwargs):
    pass

def contourf(da, **kwargs):
    pass

def contour(da, **kwargs):
    pass

def quiver(da, **kwargs):
    pass

def plot_geometries(gdf, **kwargs):
    """Plot GeoDataFrame using interactive plot.

    :param gdf:     GeoDataFrame to plot.
    :type gdf:      geopandas.GeoDataFrame
    :param kwargs:  Keyword arguments for :func:`holoviews.opts`.
    :type kwargs:   dict, optional
    :return:        Interactive plot.
    :rtype:         holoviews.element.path.Polygons

    See also: `holoviews.element.path.Polygons <https://holoviews.org/reference/elements/bokeh/Polygons.html>`_,
              `holoviews.opts <https://holoviews.org/user_guide/Customizing_Plots.html>`_.
    """

    # Default keyword arguments
    kwargs.setdefault('xlabel', '')
    kwargs.setdefault('ylabel', '')
    kwargs.setdefault('title', '')
    kwargs.setdefault('grid', True)
    kwargs.setdefault('geo', True)

    # Plot the GeoDataFrame
    p = gdf.hvplot(**kwargs)

    # Return the plot
    return p

def plot_cartopy(gdf, **kwargs):
    """Plot GeoDataFrame with cartopy geometries using interactive plot.

    :param gdf:     GeoDataFrame with cartopy geometries to plot.
    :type gdf:      geopandas.GeoDataFrame
    :param kwargs:  Keyword arguments for :func:`holoviews.opts`.
    :type kwargs:   dict, optional
    :return:        Interactive plot.
    :rtype:         holoviews.core.overlay.Overlay

    See also: `holoviews.core.overlay.Overlay <https://holoviews.org/reference/containers/bokeh/Overlay.html>`_,
              `holoviews.opts <https://holoviews.org/user_guide/Customizing_Plots.html>`_.
    """

    # Default keyword arguments
    kwargs.setdefault('xlabel', '')
    kwargs.setdefault('ylabel', '')
    kwargs.setdefault('title', '')
    kwargs.setdefault('grid', True)
    kwargs.setdefault('geo', True)

    # Seperate and explode cartopy geometries
    gdf_land = gpd.GeoDataFrame(geometry=[geom for geom in gdf.loc['land', 'geometry'].geoms]) if 'land' in gdf.index else None
    gdf_ocean = gpd.GeoDataFrame(geometry=[geom for geom in gdf.loc['ocean', 'geometry'].geoms]) if 'ocean' in gdf.index else None
    gdf_lakes = gpd.GeoDataFrame(geometry=[geom for geom in gdf.loc['lakes', 'geometry'].geoms]) if 'lakes' in gdf.index else None
    gdf_coastline = gpd.GeoDataFrame(geometry=[geom for geom in gdf.loc['coastline', 'geometry'].geoms]) if 'coastline' in gdf.index else None
    gdf_states = gpd.GeoDataFrame(geometry=[geom for geom in gdf.loc['states', 'geometry'].geoms]) if 'states' in gdf.index else None

    # Plot the cartopy geometries
    ps = []
    if gdf_ocean is not None:
        kwargs_ = {**{'color':'lightblue', 'line_color':'none'}, **kwargs}
        ps.append(gdf_ocean.hvplot(**kwargs_))
    if gdf_land is not None:
        kwargs_ = {**{'color':'antiquewhite', 'line_color':'none'}, **kwargs}
        ps.append(gdf_land.hvplot(**kwargs_))
    if gdf_lakes is not None:
        kwargs_ = {**{'color':'lightblue', 'line_color':'none'}, **kwargs}
        ps.append(gdf_lakes.hvplot(**kwargs_))
    if gdf_coastline is not None:
        kwargs_ = {**{'color':'black', 'line_width':1, 'line_dash':'solid'}, **kwargs}
        ps.append(gdf_coastline.hvplot(**kwargs_))
    if gdf_states is not None:
        kwargs_ = {**{'color':'none', 'line_width':1, 'line_dash': 'dotted'}, **kwargs}
        ps.append(gdf_states.hvplot(**kwargs_))
    
    # Combine the plots
    p = hv.Overlay(ps)

    # Return the plot
    return p

def plot_basemap(**kwargs):
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

    # Default keyword arguments
    source = kwargs.pop('source', 'OSM')
    kwargs.setdefault('xlabel', '')
    kwargs.setdefault('ylabel', '')
    kwargs.setdefault('title', '')
    kwargs.setdefault('show_grid', True)

    # Plot the basemap
    p = hv.element.tiles.tile_sources[source]().opts(**kwargs)
    
    # Return the plot
    return p
