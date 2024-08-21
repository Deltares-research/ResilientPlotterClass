import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))
from rescale import get_rescale_parameters, rescale

def plot_gdf(gdf, ax, **kwargs):
    """Plot a GeoDataFrame using plot.

    :param gdf:    GeoDataFrame to plot.
    :type gdf:     geopandas.GeoDataFrame
    :param ax:     Axis.
    :type ax:      matplotlib.axes.Axes
    :param kwargs: Keyword arguments for :func:`geopandas.GeoDataFrame.plot`.
    :type kwargs:  dict, optional
    :return:       Axis.
    :rtype:        matplotlib.axes.Axes

    :See also: `geopandas.GeoDataFrame.plot <https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.plot.html>`_.
    """

    # Combine keyword arguments on GeoDataFrame with user keyword arguments, prioritising user keyword arguments
    if 'kwargs' in gdf.columns: 
        gdf['kwargs'] = gdf['kwargs'].apply(lambda x: {**x, **kwargs})
    else:
        gdf['kwargs'] = [kwargs]*len(gdf)

    # Function to add label to legend
    def add_label_to_legend(geometry, plot_label, kwargs):
        # Plot a point with label
        if geometry.geom_type in ['Point', 'MultiPoint']:
            if 'markersize' in kwargs:
                kwargs['s'] = kwargs.pop('markersize')
            ax.scatter(np.nan, np.nan, label=plot_label, **kwargs)
        
        # Plot a line with label
        elif geometry.geom_type in ['LineString', 'MultiLineString']:
            ax.plot(np.nan, np.nan, label=plot_label, **kwargs)

        # Plot a polygon with label
        elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
            ax.add_patch(plt.Polygon(np.array([[np.nan, np.nan]]), label=plot_label, **kwargs))

    # Add string representation of keyword arguments to GeoDataFrame
    gdf['kwargs_str'] = gdf['kwargs'].apply(lambda x: str(x))

    # Plot groups of GeoDataFrames with same string representation of keyword arguments
    for kwargs, gdf_group in gdf.groupby('kwargs_str'):
        # Evaluate string representation of keyword arguments
        kwargs = eval(kwargs)
        
        # Seperate label from keyword arguments
        label = kwargs.pop('label', None)

        # Plot geodataframe
        ax = gdf_group.plot(ax=ax, **kwargs)

        # Add label to legend
        if label is not None:
            add_label_to_legend(gdf_group['geometry'].iloc[0], label, kwargs)
    
    # Return axis
    return ax

def plot_geometries(gdf, ax=None, xy_unit=None,
                        xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, **kwargs):
    """Plot a GeoDataFrame using plot.
    
    :param gdf:           GeoDataFrame to plot.
    :type gdf:            geopandas.GeoDataFrame
    :param ax:            Axis.
    :type ax:             matplotlib.axes.Axes, optional
    :param xy_unit:       Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:        str, optional
    :param xlabel_kwargs: Keyword arguments for :func:`matplotlib.axis.set_xlabel`.
    :type xlabel_kwargs:  dict, optional
    :param ylabel_kwargs: Keyword arguments for :func:`matplotlib.axis.set_ylabel`.
    :type ylabel_kwargs:  dict, optional
    :param title_kwargs:  Keyword arguments for :func:`matplotlib.axis.set_title`.
    :type title_kwargs:   dict, optional
    :param aspect_kwargs: Keyword arguments for :func:`matplotlib.axis.set_aspect`.
    :type aspect_kwargs:  dict, optional
    :param grid_kwargs:   Keyword arguments for :func:`matplotlib.axis.grid`.
    :type grid_kwargs:    dict, optional
    :param kwargs:        Keyword arguments for :func:`geopandas.GeoDataFrame.plot`.
    :type kwargs:         dict, optional
    :return:              Axis.
    :rtype:               matplotlib.axes.Axes

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `geopandas.GeoDataFrame.plot <https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.plot.html>`_
    """

    # Create axis if not provided
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Create keyword arguments if not provided
    if xlabel_kwargs is None: xlabel_kwargs = {}
    if ylabel_kwargs is None: ylabel_kwargs = {}
    if title_kwargs is None: title_kwargs = {}
    if aspect_kwargs is None: aspect_kwargs = {}
    if grid_kwargs is None: grid_kwargs = {}

    # Get the rescale parameters
    scale_factor, xlabel, ylabel = get_rescale_parameters(data=gdf, xy_unit=xy_unit)
    
    # Rescale the GeoDataFrame
    gdf = rescale(data=gdf, scale_factor=scale_factor)

    # Rescale xlim and ylim
    if 'xlim' in kwargs and kwargs['xlim'] is not None:
        xlim = [x*scale_factor for x in kwargs.pop('xlim')]
    elif 'xlim' in kwargs:
        xlim = kwargs.pop('xlim')
    else:
        xlim = None
    if 'ylim' in kwargs and kwargs['ylim'] is not None:
        ylim= [y*scale_factor for y in kwargs.pop('ylim')]
    elif 'ylim' in kwargs:
        ylim = kwargs.pop('ylim')
    else:
        ylim = None
    
    # Set default keyword arguments
    xlabel_kwargs.setdefault('xlabel', xlabel)
    ylabel_kwargs.setdefault('ylabel', ylabel)
    title_kwargs.setdefault('label', '')
    aspect_kwargs.setdefault('aspect', 'equal')
    grid_kwargs.setdefault('visible', True)

    # Plot the GeoDataFrame
    ax = plot_gdf(gdf, ax=ax, **kwargs)

    # Set limits
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    # Set labels
    ax.set_xlabel(**xlabel_kwargs)
    ax.set_ylabel(**ylabel_kwargs)
    ax.set_title(**title_kwargs)

    # Set aspect
    ax.set_aspect(**aspect_kwargs)

    # Set grid
    ax.grid(**grid_kwargs)
    
    # Return axis
    return ax
