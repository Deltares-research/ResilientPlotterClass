import matplotlib.pyplot as plt
import resilientplotterclass as rpc

# Wrapper for contextily.add_basemap() to allow for scaling
def plot_basemap(crs=None, ax=None, xy_unit=None, xlim=None, ylim=None, xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, aspect_kwargs=None, grid_kwargs=None, **kwargs):
    """Plot a basemap using contextily.
    
    :param crs:           Coordinate reference system of the basemap.
    :type crs:            pyproj.CRS or rasterio.crs.CRS or str, optional
    :param ax:            Axis.
    :type ax:             matplotlib.axes.Axes, optional
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
    :param kwargs:        Keyword arguments for :func:`contextily.add_basemap`.
    :type kwargs:         dict, optional
    :return:              Axis.
    :rtype:               matplotlib.axes.Axes

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `contextily.add_basemap <https://contextily.readthedocs.io/en/latest/reference.html#contextily.add_basemap>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots()
    
    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(crs=crs, xy_unit=xy_unit)
    
    # Format axis
    ax = rpc.axes.format(ax, crs=crs, xy_unit=xy_unit, xlim=xlim, ylim=ylim, xlabel_kwargs=xlabel_kwargs, ylabel_kwargs=ylabel_kwargs,
                         title_kwargs=title_kwargs, aspect_kwargs=aspect_kwargs, grid_kwargs=grid_kwargs)
    
    # Add basemap
    _add_basemap(ax=ax, scale=scale_factor, crs=crs, **kwargs)
    
    # Return axis
    return ax

# Code below was adapted from the contextily package to allow for scaling using the scale parameter
"""Tools to plot basemaps"""

import warnings
import numpy as np
from contextily import providers
from xyzservices import TileProvider
from contextily.tile import bounds2img, warp_tiles, _warper
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from matplotlib import patheffects
from matplotlib.pyplot import draw
from contextily.plotting import _reproj_bb, _is_overlay
from contextily.plotting import add_attribution as add_attribution_

INTERPOLATION = "bilinear"
ZOOM = "auto"
ATTRIBUTION_SIZE = 8

def _add_basemap(
    ax,
    scale,
    crs,
    add_attribution=True,
    zoom=ZOOM,
    source=None,
    interpolation=INTERPOLATION,
    attribution=None,
    attribution_size=ATTRIBUTION_SIZE,
    reset_extent=True,
    
    resampling=Resampling.bilinear,
    zoom_adjust=None,
    **extra_imshow_args
):
    """
    Add a (web/local) basemap to `ax`.

    Parameters
    ----------
    ax : AxesSubplot
        Matplotlib axes object on which to add the basemap. The extent of the
        axes is assumed to be in Spherical Mercator (EPSG:3857), unless the `crs`
        keyword is specified.
    zoom : int or 'auto'
        [Optional. Default='auto'] Level of detail for the basemap. If 'auto',
        it is calculated automatically. Ignored if `source` is a local file.
    source : xyzservices.TileProvider object or str
        [Optional. Default: OpenStreetMap Humanitarian web tiles]
        The tile source: web tile provider, a valid input for a query of a
        :class:`xyzservices.TileProvider` by a name from ``xyzservices.providers`` or
        path to local file. The web tile provider can be in the form of a
        :class:`xyzservices.TileProvider` object or a URL. The placeholders for the XYZ
        in the URL need to be `{x}`, `{y}`, `{z}`, respectively. For local file paths,
        the file is read with `rasterio` and all bands are loaded into the basemap.
        IMPORTANT: tiles are assumed to be in the Spherical Mercator projection
        (EPSG:3857), unless the `crs` keyword is specified.
    interpolation : str
        [Optional. Default='bilinear'] Interpolation algorithm to be passed
        to `imshow`. See `matplotlib.pyplot.imshow` for further details.
    attribution : str
        [Optional. Defaults to attribution specified by the source]
        Text to be added at the bottom of the axis. This
        defaults to the attribution of the provider specified
        in `source` if available. Specify False to not
        automatically add an attribution, or a string to pass
        a custom attribution.
    attribution_size : int
        [Optional. Defaults to `ATTRIBUTION_SIZE`].
        Font size to render attribution text with.
    reset_extent : bool
        [Optional. Default=True] If True, the extent of the
        basemap added is reset to the original extent (xlim,
        ylim) of `ax`
    crs : None or str or CRS
        [Optional. Default=None] coordinate reference system (CRS),
        expressed in any format permitted by rasterio, to use for the
        resulting basemap. If None (default), no warping is performed
        and the original Spherical Mercator (EPSG:3857) is used.
    resampling : <enum 'Resampling'>
        [Optional. Default=Resampling.bilinear] Resampling
        method for executing warping, expressed as a
        `rasterio.enums.Resampling` method
    zoom_adjust : int or None
        [Optional. Default: None]
        The amount to adjust a chosen zoom level if it is chosen automatically. 
        Values outside of -1 to 1 are not recommended as they can lead to slow execution.
    **extra_imshow_args :
        Other parameters to be passed to `imshow`.

    Examples
    --------

    >>> import geopandas
    >>> import contextily as cx
    >>> db = geopandas.read_file(ps.examples.get_path('virginia.shp'))

    Ensure the data is in Spherical Mercator:

    >>> db = db.to_crs(epsg=3857)

    Add a web basemap:

    >>> ax = db.plot(alpha=0.5, color='k', figsize=(6, 6))
    >>> cx.add_basemap(ax, source=url)
    >>> plt.show()

    Or download a basemap to a local file and then plot it:

    >>> source = 'virginia.tiff'
    >>> _ = cx.bounds2raster(*db.total_bounds, zoom=6, source=source)
    >>> ax = db.plot(alpha=0.5, color='k', figsize=(6, 6))
    >>> cx.add_basemap(ax, source=source)
    >>> plt.show()

    """

    xmin, xmax, ymin, ymax = ax.axis()
    
    # Rescale bounds
    xmin, xmax, ymin, ymax = xmin/scale, xmax/scale, ymin/scale, ymax/scale

    if isinstance(source, str):
        try:
            source = providers.query_name(source)
        except ValueError:
            pass

    # If web source
    if (
        source is None
        or isinstance(source, (dict, TileProvider))
        or (isinstance(source, str) and source[:4] == "http")
    ):
        # Extent
        left, right, bottom, top = xmin, xmax, ymin, ymax
        # Convert extent from `crs` into WM for tile query
        if crs is not None:
            left, right, bottom, top = _reproj_bb(
                left, right, bottom, top, crs, "epsg:3857"
            )
        # Download image
        image, extent = bounds2img(
            left, bottom, right, top, zoom=zoom, source=source, ll=False, zoom_adjust=zoom_adjust
        )
        # Warping
        if crs is not None:
            image, extent = warp_tiles(image, extent, t_crs=crs, resampling=resampling)
        # Check if overlay
        if _is_overlay(source) and "zorder" not in extra_imshow_args:
            # If zorder was not set then make it 9 otherwise leave it
            extra_imshow_args["zorder"] = 9
    # If local source
    else:
        import rasterio as rio

        # Read file
        with rio.open(source) as raster:
            if reset_extent:
                from rasterio.mask import mask as riomask

                # Read window
                if crs:
                    left, bottom, right, top = rio.warp.transform_bounds(
                        crs, raster.crs, xmin, ymin, xmax, ymax
                    )
                else:
                    left, bottom, right, top = xmin, ymin, xmax, ymax
                window = [
                    {
                        "type": "Polygon",
                        "coordinates": (
                            (
                                (left, bottom),
                                (right, bottom),
                                (right, top),
                                (left, top),
                                (left, bottom),
                            ),
                        ),
                    }
                ]
                image, img_transform = riomask(raster, window, crop=True)
                extent = left, right, bottom, top
            else:
                # Read full
                image = np.array([band for band in raster.read()])
                img_transform = raster.transform
                bb = raster.bounds
                extent = bb.left, bb.right, bb.bottom, bb.top
            # Warp
            if (crs is not None) and (raster.crs != crs):
                image, bounds, _ = _warper(
                    image, img_transform, raster.crs, crs, resampling
                )
                extent = bounds.left, bounds.right, bounds.bottom, bounds.top
            image = image.transpose(1, 2, 0)
    
    # Rescale bounds and extent
    xmin, xmax, ymin, ymax = [e*scale for e in (xmin, xmax, ymin, ymax)]
    extent = [e*scale for e in extent]
    
    # Plotting
    if image.shape[2] == 1:
        image = image[:, :, 0]
    img = ax.imshow(
        image, extent=extent, interpolation=interpolation, **extra_imshow_args
    )

    if reset_extent:
        ax.axis((xmin, xmax, ymin, ymax))
    else:
        max_bounds = (
            min(xmin, extent[0]),
            max(xmax, extent[1]),
            min(ymin, extent[2]),
            max(ymax, extent[3]),
        )
        ax.axis(max_bounds)

    # Add attribution text
    if source is None:
        source = providers.OpenStreetMap.HOT
    if isinstance(source, (dict, TileProvider)) and attribution is None:
        attribution = source.get("attribution")
    if attribution and add_attribution:
        add_attribution_(ax, attribution, font_size=attribution_size)

    return