import matplotlib.pyplot as plt
import resilientplotterclass as rpc

def pcolormesh(uda, ax=None, xy_unit=None, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using pcolormesh.
    
    :param uda:                Data to plot.
    :type uda:                 xugrid.UgridDataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
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
    :param kwargs:             Keyword arguments for :func:`xugrid.plot.pcolormesh`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xugrid.plot.pcolormesh <https://deltares.github.io/xugrid/api/xugrid.plot.pcolormesh.html#xugrid.plot.pcolormesh>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=uda, xy_unit=xy_unit)
    
    # Rescale UgridudataArray
    uda = rpc.rescale.rescale(data=uda, scale_factor=scale_factor)
    
    # Append colorbar axis
    if append_axes_kwargs is not None and ('add_colorbar' not in kwargs or kwargs['add_colorbar']):
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)
    
    # Plot UgridDataArray
    p = uda.ugrid.plot.pcolormesh(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=uda, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def imshow(uda, ax=None, xy_unit=None, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using imshow.
    
    :param uda:                Data to plot.
    :type uda:                 xugrid.UgridDataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
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
    :param kwargs:             Keyword arguments for :func:`xugrid.plot.imshow`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xugrid.plot.imshow <https://deltares.github.io/xugrid/api/xugrid.plot.imshow.html#xugrid.plot.imshow>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=uda, xy_unit=xy_unit)
    
    # Rescale UgridudataArray
    uda = rpc.rescale.rescale(data=uda, scale_factor=scale_factor)
    
    # Append colorbar axis
    if append_axes_kwargs is not None and ('add_colorbar' not in kwargs or kwargs['add_colorbar']):
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)
    
    # Plot UgridDataArray
    p = uda.ugrid.plot.imshow(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=uda, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def scatter(uda, ax=None, xy_unit=None, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using scatter.
    
    :param uda:                Data to plot.
    :type uda:                 xugrid.UgridDataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
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
    :param kwargs:             Keyword arguments for :func:`xugrid.plot.scatter`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xugrid.plot.scatter <https://deltares.github.io/xugrid/api/xugrid.plot.scatter.html#xugrid.plot.scatter>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=uda, xy_unit=xy_unit)

    # Rescale UgridudataArray
    uda = rpc.rescale.rescale(data=uda, scale_factor=scale_factor)

    # Append colorbar axis
    if append_axes_kwargs is not None and (('add_colorbar' in kwargs and kwargs['add_colorbar']) or ('hue' in kwargs and kwargs['hue'] is not None)):
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)
    
    # Plot UgridDataArray
    p = uda.ugrid.plot.scatter(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=uda, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def contourf(uda, ax=None, xy_unit=None, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using contourf.
    
    :param uda:                Data to plot.
    :type uda:                 xugrid.UgridDataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
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
    :param kwargs:             Keyword arguments for :func:`xugrid.plot.contourf`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xugrid.plot.contourf <https://deltares.github.io/xugrid/api/xugrid.plot.contourf.html#xugrid.plot.contourf>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=uda, xy_unit=xy_unit)
    
    # Rescale UgridudataArray
    uda = rpc.rescale.rescale(data=uda, scale_factor=scale_factor)
    
    # Append colorbar axis
    if append_axes_kwargs is not None and ('add_colorbar' not in kwargs or kwargs['add_colorbar']):
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)
    
    # Plot UgridDataArray
    p = uda.ugrid.plot.contourf(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=uda, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def contour(uda, ax=None, xy_unit=None, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using contour.
    
    :param uda:                Data to plot.
    :type uda:                 xugrid.UgridDataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
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
    :param kwargs:             Keyword arguments for :func:`xugrid.plot.contour`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xugrid.plot.contour <https://deltares.github.io/xugrid/api/xugrid.plot.contour.html#xugrid.plot.contour>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=uda, xy_unit=xy_unit)
    
    # Rescale UgridudataArray
    uda = rpc.rescale.rescale(data=uda, scale_factor=scale_factor)

    # Append colorbar axis
    if append_axes_kwargs is not None and ('add_colorbar' in kwargs and kwargs['add_colorbar']):
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)
    
    # Plot UgridDataArray
    p = uda.ugrid.plot.contour(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=uda, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return p

def quiver(uds, ax=None, xy_unit=None, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using quiver.

    :param uda:                Data to plot.
    :type uda:                 xugrid.UgridDataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
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
    :param kwargs:             Keyword arguments for :func:`xugrid.plot.quiver`.
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
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=uds, xy_unit=xy_unit)

    # Rescale UgridDataSet
    uds = rpc.rescale.rescale(data=uds, scale_factor=scale_factor)

    # Append colorbar axis
    if append_axes_kwargs is not None and (('add_colorbar' in kwargs and kwargs['add_colorbar']) or ('hue' in kwargs and kwargs['hue'] is not None)):
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)

    # Plot UgridDataSet
    p = uds.plot.quiver(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=uds, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)

    # Return plot
    return p

def grid(uda, ax=None, xy_unit=None, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, append_axes_kwargs=None, **kwargs):
    """Plot data using grid.

    :param uda:                Data to plot.
    :type uda:                 xugrid.UgridDataArray
    :param ax:                 Axis.
    :type ax:                  matplotlib.axes.Axes, optional
    :param xy_unit:            Unit to rescale the x and y dimensions to. If ``None``, the unit is determined automatically based on the input data.
    :type xy_unit:             str, optional
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
    :param kwargs:             Keyword arguments for :func:`xugrid.Ugrid2d.plot`.
    :type kwargs:              dict, optional
    :return:                   Plot.
    :rtype:                    matplotlib.collections.QuadMesh
    
    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `xugrid.Ugrid2d.plot <https://deltares.github.io/xugrid/api/xugrid.Ugrid2d.html#xugrid.Ugrid2d.plot>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=uda, xy_unit=xy_unit)
    
    # Rescale UgridudataArray
    uda = rpc.rescale.rescale(data=uda, scale_factor=scale_factor)

    # Append colorbar axis
    if append_axes_kwargs is not None and 'add_colorbar' in kwargs and kwargs['add_colorbar']:
        kwargs['cbar_kwargs'] = {} if 'cbar_kwargs' not in kwargs or kwargs['cbar_kwargs'] is None else kwargs['cbar_kwargs']
        kwargs['cbar_kwargs']['cax'] = rpc.axes.append_cbar_axis(ax=ax, append_axes_kwargs=append_axes_kwargs)
    
    # Plot UgridDataArray
    p = uda.grid.plot(ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(ax=ax, data=uda, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Return plot
    return ax
