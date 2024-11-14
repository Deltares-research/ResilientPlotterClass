import matplotlib.pyplot as plt
import numpy as np
import resilientplotterclass as rpc
import xarray as xr

def pcolormesh(da, ax=None, xy_unit=None, skip=1, smooth=1, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using pcolormesh.
    
    :param da:                 Data to plot.
    :type da:                  xarray.DataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
    :param skip:               Plot every nth value in x and y direction.
    :type skip:                int, optional
    :param smooth:             Smooth data array with rolling mean in x and y direction.
    :type smooth:              int, optional
    :param xlim:               x limits.
    :type xlim:                list[float], optional
    :param ylim:               y limits.
    :type ylim:                list[float], optional
    :param xlabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_xlabel`.
    :type xlabel_kwargs:       dict, optional
    :param ylabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_ylabel`.
    :type ylabel_kwargs:       dict, optional
    :param title_kwargs:       Keyword arguments for :func:`matplotlib.axis.set_title`.
    :type title_kwargs:        dict, optional
    :param aspect_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_aspect`.
    :type aspect_kwargs:       dict, optional
    :param grid_kwargs:        Keyword arguments for :func:`matplotlib.axis.grid`.
    :type grid_kwargs:         dict, optional
    :param append_axes_kwargs: Keyword arguments for :func:`mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes`.
    :type append_axes_kwargs:  dict, optional
    :param kwargs:             Keyword arguments for :func:`xarray.plot.pcolormesh`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xarray.plot.pcolormesh <http://xarray.pydata.org/en/stable/generated/xarray.plot.pcolormesh.html>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=da, xy_unit=xy_unit)
    
    # Rescale the DataArray
    da = rpc.rescale.rescale(data=da, scale_factor=scale_factor)

    # Skip DataArray values
    if skip > 1:
        da = da.isel(x=slice(None, None, skip), y=slice(None, None, skip))

    # Smooth DataArray
    if smooth > 1:
        da = da.rolling(x=smooth, center=True).mean().rolling(y=smooth, center=True).mean()
    
    # Append colorbar axis
    if append_axes_kwargs is not None and ('add_colorbar' not in kwargs or not kwargs['add_colorbar']):
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)
    
    # Plot DataArray
    p = da.plot.pcolormesh(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=da, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def imshow(da, ax=None, xy_unit=None, skip=1, smooth=1, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using imshow.
    
    :param da:                 Data to plot.
    :type da:                  xarray.DataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
    :param skip:               Plot every nth value in x and y direction.
    :type skip:                int, optional
    :param smooth:             Smooth data array with rolling mean in x and y direction.
    :type smooth:              int, optional
    :param xlim:               x limits.
    :type xlim:                list[float], optional
    :param ylim:               y limits.
    :type ylim:                list[float], optional
    :param xlabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_xlabel`.
    :type xlabel_kwargs:       dict, optional
    :param ylabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_ylabel`.
    :type ylabel_kwargs:       dict, optional
    :param title_kwargs:       Keyword arguments for :func:`matplotlib.axis.set_title`.
    :type title_kwargs:        dict, optional
    :param aspect_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_aspect`.
    :type aspect_kwargs:       dict, optional
    :param grid_kwargs:        Keyword arguments for :func:`matplotlib.axis.grid`.
    :type grid_kwargs:         dict, optional
    :param append_axes_kwargs: Keyword arguments for :func:`mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes`.
    :type append_axes_kwargs:  dict, optional
    :param kwargs:             Keyword arguments for :func:`xarray.plot.imshow`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xarray.plot.imshow <http://xarray.pydata.org/en/stable/generated/xarray.plot.imshow.html>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=da, xy_unit=xy_unit)
    
    # Rescale the DataArray
    da = rpc.rescale.rescale(data=da, scale_factor=scale_factor)

    # Skip DataArray values
    if skip > 1:
        da = da.isel(x=slice(None, None, skip), y=slice(None, None, skip))

    # Smooth DataArray
    if smooth > 1:
        da = da.rolling(x=smooth, center=True).mean().rolling(y=smooth, center=True).mean()

    # Append colorbar axis
    if append_axes_kwargs is not None and ('add_colorbar' not in kwargs or not kwargs['add_colorbar']):
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)
    
    # Plot DataArray
    p = da.plot.imshow(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=da, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def scatter(ds, ax=None, xy_unit=None, skip=1, smooth=1, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using scatter.
    
    :param da:                 Data to plot.
    :type da:                  xarray.DataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
    :param skip:               Plot every nth value in x and y direction.
    :type skip:                int, optional
    :param smooth:             Smooth data array with rolling mean in x and y direction.
    :type smooth:              int, optional
    :param xlim:               x limits.
    :type xlim:                list[float], optional
    :param ylim:               y limits.
    :type ylim:                list[float], optional
    :param xlabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_xlabel`.
    :type xlabel_kwargs:       dict, optional
    :param ylabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_ylabel`.
    :type ylabel_kwargs:       dict, optional
    :param title_kwargs:       Keyword arguments for :func:`matplotlib.axis.set_title`.
    :type title_kwargs:        dict, optional
    :param aspect_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_aspect`.
    :type aspect_kwargs:       dict, optional
    :param grid_kwargs:        Keyword arguments for :func:`matplotlib.axis.grid`.
    :type grid_kwargs:         dict, optional
    :param append_axes_kwargs: Keyword arguments for :func:`mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes`.
    :type append_axes_kwargs:  dict, optional
    :param kwargs:             Keyword arguments for :func:`xarray.plot.scatter`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xarray.plot.scatter <http://xarray.pydata.org/en/stable/generated/xarray.plot.scatter.html>`_.
    """
    
    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=ds, xy_unit=xy_unit)
    
    # Rescale the Dataset
    ds = rpc.rescale.rescale(data=ds, scale_factor=scale_factor)

    # Skip Dataset values
    if skip > 1:
        ds = ds.isel(x=slice(None, None, skip), y=slice(None, None, skip))

    # Smooth Dataset
    if smooth > 1:
        ds = ds.rolling(x=smooth, center=True).mean().rolling(y=smooth, center=True).mean()
    
    # Append colorbar axis
    if append_axes_kwargs is not None and 'add_colorbar' in kwargs or kwargs['add_colorbar']:
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)

    # Plot Dataset
    p = ds.plot.scatter(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=ds, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def contourf(da, ax=None, xy_unit=None, skip=1, smooth=1, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using contourf.
    
    :param da:                 Data to plot.
    :type da:                  xarray.DataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
    :param skip:               Plot every nth value in x and y direction.
    :type skip:                int, optional
    :param smooth:             Smooth data array with rolling mean in x and y direction.
    :type smooth:              int, optional
    :param xlim:               x limits.
    :type xlim:                list[float], optional
    :param ylim:               y limits.
    :type ylim:                list[float], optional
    :param xlabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_xlabel`.
    :type xlabel_kwargs:       dict, optional
    :param ylabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_ylabel`.
    :type ylabel_kwargs:       dict, optional
    :param title_kwargs:       Keyword arguments for :func:`matplotlib.axis.set_title`.
    :type title_kwargs:        dict, optional
    :param aspect_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_aspect`.
    :type aspect_kwargs:       dict, optional
    :param grid_kwargs:        Keyword arguments for :func:`matplotlib.axis.grid`.
    :type grid_kwargs:         dict, optional
    :param append_axes_kwargs: Keyword arguments for :func:`mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes`.
    :type append_axes_kwargs:  dict, optional
    :param kwargs:             Keyword arguments for :func:`xarray.plot.contourf`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xarray.plot.contourf <http://xarray.pydata.org/en/stable/generated/xarray.plot.contourf.html>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=da, xy_unit=xy_unit)
    
    # Rescale the DataArray
    da = rpc.rescale.rescale(data=da, scale_factor=scale_factor)

    # Skip DataArray values
    if skip > 1:
        da = da.isel(x=slice(None, None, skip), y=slice(None, None, skip))

    # Smooth DataArray
    if smooth > 1:
        da = da.rolling(x=smooth, center=True).mean().rolling(y=smooth, center=True).mean()
    
    # Append colorbar axis
    if append_axes_kwargs is not None and ('add_colorbar' not in kwargs or not kwargs['add_colorbar']):
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)
    
    # Plot DataArray
    p = da.plot.contourf(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=da, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def contour(da, ax=None, xy_unit=None, skip=1, smooth=1, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using contour.
    
    :param da:                 Data to plot.
    :type da:                  xarray.DataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
    :param skip:               Plot every nth value in x and y direction.
    :type skip:                int, optional
    :param smooth:             Smooth data array with rolling mean in x and y direction.
    :type smooth:              int, optional
    :param xlim:               x limits.
    :type xlim:                list[float], optional
    :param ylim:               y limits.
    :type ylim:                list[float], optional
    :param xlabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_xlabel`.
    :type xlabel_kwargs:       dict, optional
    :param ylabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_ylabel`.
    :type ylabel_kwargs:       dict, optional
    :param title_kwargs:       Keyword arguments for :func:`matplotlib.axis.set_title`.
    :type title_kwargs:        dict, optional
    :param aspect_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_aspect`.
    :type aspect_kwargs:       dict, optional
    :param grid_kwargs:        Keyword arguments for :func:`matplotlib.axis.grid`.
    :type grid_kwargs:         dict, optional
    :param append_axes_kwargs: Keyword arguments for :func:`mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes`.
    :type append_axes_kwargs:  dict, optional
    :param kwargs:             Keyword arguments for :func:`xarray.plot.contour`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xarray.plot.contour <http://xarray.pydata.org/en/stable/generated/xarray.plot.contour.html>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=da, xy_unit=xy_unit)
    
    # Rescale the DataArray
    da = rpc.rescale.rescale(data=da, scale_factor=scale_factor)

    # Skip DataArray values
    if skip > 1:
        da = da.isel(x=slice(None, None, skip), y=slice(None, None, skip))

    # Smooth DataArray
    if smooth > 1:
        da = da.rolling(x=smooth, center=True).mean().rolling(y=smooth, center=True).mean()
    
    # Append colorbar axis
    if append_axes_kwargs is not None and 'add_colorbar' in kwargs or kwargs['add_colorbar']:
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)
    
    # Plot DataArray
    p = da.plot.contour(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=da, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def quiver(ds, ax=None, xy_unit=None, skip=1, smooth=1, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using quiver.

    :param da:                 Data to plot.
    :type da:                  xarray.DataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
    :param skip:               Plot every nth value in x and y direction.
    :type skip:                int, optional
    :param smooth:             Smooth data array with rolling mean in x and y direction.
    :type smooth:              int, optional
    :param xlim:               x limits.
    :type xlim:                list[float], optional
    :param ylim:               y limits.
    :type ylim:                list[float], optional
    :param xlabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_xlabel`.
    :type xlabel_kwargs:       dict, optional
    :param ylabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_ylabel`.
    :type ylabel_kwargs:       dict, optional
    :param title_kwargs:       Keyword arguments for :func:`matplotlib.axis.set_title`.
    :type title_kwargs:        dict, optional
    :param aspect_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_aspect`.
    :type aspect_kwargs:       dict, optional
    :param grid_kwargs:        Keyword arguments for :func:`matplotlib.axis.grid`.
    :type grid_kwargs:         dict, optional
    :param append_axes_kwargs: Keyword arguments for :func:`mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes`.
    :type append_axes_kwargs:  dict, optional
    :param kwargs:             Keyword arguments for :func:`xarray.plot.quiver`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh
    
    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xarray.plot.quiver <http://xarray.pydata.org/en/stable/generated/xarray.plot.quiver.html>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=ds, xy_unit=xy_unit)
    
    # Rescale the Dataset
    ds = rpc.rescale.rescale(data=ds, scale_factor=scale_factor)

    # Skip Dataset values
    if skip > 1:
        ds = ds.isel(x=slice(None, None, skip), y=slice(None, None, skip))
    
    # Append colorbar axis
    if append_axes_kwargs is not None and 'add_colorbar' in kwargs or kwargs['add_colorbar']:
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)

    # Smooth Dataset
    if smooth > 1:
        ds = ds.rolling(x=smooth, center=True).mean().rolling(y=smooth, center=True).mean()
    
    # Plot Dataset
    p = ds.plot.quiver(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=ds, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def streamplot(ds, ax=None, xy_unit=None, skip=1, smooth=1, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using streamplot.
    
    :param da:                 Data to plot.
    :type da:                  xarray.DataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
    :param skip:               Plot every nth value in x and y direction.
    :type skip:                int, optional
    :param smooth:             Smooth data array with rolling mean in x and y direction.
    :type smooth:              int, optional
    :param xlim:               x limits.
    :type xlim:                list[float], optional
    :param ylim:               y limits.
    :type ylim:                list[float], optional
    :param xlabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_xlabel`.
    :type xlabel_kwargs:       dict, optional
    :param ylabel_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_ylabel`.
    :type ylabel_kwargs:       dict, optional
    :param title_kwargs:       Keyword arguments for :func:`matplotlib.axis.set_title`.
    :type title_kwargs:        dict, optional
    :param aspect_kwargs:      Keyword arguments for :func:`matplotlib.axis.set_aspect`.
    :type aspect_kwargs:       dict, optional
    :param grid_kwargs:        Keyword arguments for :func:`matplotlib.axis.grid`.
    :type grid_kwargs:         dict, optional
    :param append_axes_kwargs: Keyword arguments for :func:`mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes`.
    :type append_axes_kwargs:  dict, optional
    :param kwargs:             Keyword arguments for :func:`xarray.plot.streamplot`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xarray.plot.streamplot <http://xarray.pydata.org/en/stable/generated/xarray.plot.streamplot.html>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=ds, xy_unit=xy_unit)
    
    # Rescale the DataArray
    ds = rpc.rescale.rescale(data=ds, scale_factor=scale_factor)

    # Skip DataArray values
    if skip > 1:
        ds = ds.isel(x=slice(None, None, skip), y=slice(None, None, skip))

    # Smooth DataArray
    if smooth > 1:
        ds = ds.rolling(x=smooth, center=True).mean().rolling(y=smooth, center=True).mean()

    # Sort such that y is srictly increasing
    ds = ds.sortby('y')

    # Append colorbar axis
    if append_axes_kwargs is not None and 'add_colorbar' in kwargs or kwargs['add_colorbar']:
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)

    # Plot Dataset
    p = ds.plot.streamplot(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=ds, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p


