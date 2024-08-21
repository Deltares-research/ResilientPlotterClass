import matplotlib.pyplot as plt
from resilientplotterclass.rescale import get_rescale_parameters, rescale

def plot(ax=None, xy_unit=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None):
    """Plot a figure.
    
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
    :return:              Plot.
    :rtype:               matplotlib.collections.QuadMesh

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_.
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