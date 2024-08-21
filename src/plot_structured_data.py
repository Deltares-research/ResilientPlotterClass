import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))
from rescale import get_rescale_parameters, rescale

def pcolormesh_DataArray(da, ax=None, xy_unit=None, skip=1, smooth=1, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, **kwargs):
    """Plot a DataArray using pcolormesh.
    
    :param da:            DataArray to plot.
    :type da:             xarray.DataArray
    :param ax:            Axis.
    :type ax:             matplotlib.axes.Axes, optional
    :param xy_unit:       Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:        str, optional
    :param skip:          Plot every nth value in x and y direction.
    :type skip:           int, optional
    :param smooth:        Smooth data array with rolling mean in x and y direction.
    :type smooth:         int, optional
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
    :param kwargs:        Keyword arguments for :func:`xarray.plot.pcolormesh`.
    :type kwargs:         dict, optional
    :return:              Plot.
    :rtype:               matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `xarray.plot.pcolormesh <http://xarray.pydata.org/en/stable/generated/xarray.plot.pcolormesh.html>`_.
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
    scale_factor, xlabel, ylabel = get_rescale_parameters(data=da, xy_unit=xy_unit)
    
    # Rescale the DataArray
    da = rescale(data=da, scale_factor=scale_factor)

    # Rescale xlim and ylim
    if 'xlim' in kwargs and kwargs['xlim'] is not None:
        kwargs['xlim'] = [x*scale_factor for x in kwargs['xlim']]
    if 'ylim' in kwargs and kwargs['ylim'] is not None:
        kwargs['ylim'] = [y*scale_factor for y in kwargs['ylim']]

    # Set default keyword arguments
    xlabel_kwargs.setdefault('xlabel', xlabel)
    ylabel_kwargs.setdefault('ylabel', ylabel)
    title_kwargs.setdefault('label', '')
    aspect_kwargs.setdefault('aspect', 'equal')
    grid_kwargs.setdefault('visible', True)

    # Skip every nth value
    if skip > 1:
        da = da.isel(x=slice(None, None, skip), y=slice(None, None, skip))

    # Smooth data array
    if smooth > 1:
        da = da.rolling(x=smooth, center=True).mean().rolling(y=smooth, center=True).mean()
    
    # Plot data array
    p = da.plot.pcolormesh(ax=ax, **kwargs)

    # Set labels
    ax.set_xlabel(**xlabel_kwargs)
    ax.set_ylabel(**ylabel_kwargs)
    ax.set_title(**title_kwargs)

    # Set aspect
    ax.set_aspect(**aspect_kwargs)

    # Set grid
    ax.grid(**grid_kwargs)
    
    # Return plot
    return p
