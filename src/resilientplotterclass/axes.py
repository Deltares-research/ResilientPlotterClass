import matplotlib.pyplot as plt
import resilientplotterclass as rpc
from mpl_toolkits.axes_grid1 import make_axes_locatable

def append_cbar_axis(ax, append_axes_kwargs=None):
    """Append a colorbar axis.

    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes
    :param append_axes_kwargs: Keyword arguments for :func:`mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes`.
    :type append_axes_kwargs:  dict, optional
    :return:                   Colorbar axis.
    :rtype:                    matplotlib.axes.Axes

    :See also: `matplotlib.figure.Figure.colorbar <https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.colorbar.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_.
    """

    # Create keyword arguments if not provided
    if append_axes_kwargs is None: append_axes_kwargs = {}

    # Divide axis
    divider = make_axes_locatable(ax)

    # Create colorbar axis
    cax = divider.append_axes(**append_axes_kwargs)
    
    # Return colorbar axis
    return cax


def format(ax, data=None, crs=None, xy_unit=None, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None):
    """Format axis for a DataArray, UgridDataArray or GeoDataFrame.
    
    :param ax:            Axis.
    :type ax:             matplotlib.axes.Axes
    :param data:          DataArray, UgridDataArray or GeoDataFrame to rescale. If ``None``, the coordinate reference system is used to create the axis.
    :type data:           xr.DataArray or xugrid.UgridDataArray or gpd.GeoDataFrame, optional
    :param crs:           Coordinate reference system of the data. If ``None``, the data is used to create the axis.
    :type crs:            pyproj.CRS or rasterio.CRS or str, optional
    :param xy_unit:       Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:        str, optional
    :param xlim:          x limits.
    :type xlim:           list[float], optional
    :param ylim:          y limits.
    :type ylim:           list[float], optional
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
    :return:              Axis.
    :rtype:               matplotlib.axes.Axes

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_.
    """

    # Create keyword arguments if not provided
    if xlabel_kwargs is None: xlabel_kwargs = {}
    if ylabel_kwargs is None: ylabel_kwargs = {}
    if title_kwargs is None: title_kwargs = {}
    if aspect_kwargs is None: aspect_kwargs = {}
    if grid_kwargs is None: grid_kwargs = {}

    # Get the rescale parameters
    scale_factor, xlabel, ylabel = rpc.rescale.get_rescale_parameters(data=data, crs=crs, xy_unit=xy_unit)
    
    # Rescale x and y limits
    if xlim is not None:
        xlim = [x*scale_factor for x in xlim]
    if ylim is not None:
        ylim = [y*scale_factor for y in ylim]
    
    # Set default keyword arguments
    xlabel_kwargs.setdefault('xlabel', xlabel)
    ylabel_kwargs.setdefault('ylabel', ylabel)
    title_kwargs.setdefault('label', '')
    aspect_kwargs.setdefault('aspect', 'equal')
    grid_kwargs.setdefault('visible', True)

    # Set limits
    ax.set_xlim(xlim)
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