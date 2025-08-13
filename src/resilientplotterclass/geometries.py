import cartopy.feature as cfeature
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch
from pyproj import CRS as pyprojCRS
from rasterio.crs import CRS as rasterioCRS
from shapely.geometry import MultiLineString, MultiPoint, MultiPolygon, Polygon

import resilientplotterclass as rpc


def _clip_gdf_cartopy(gdf, bounds):
    """Clip GeoDataFrame with cartopy geometries to bounds.

    :param gdf:    GeoDataFrame to clip.
    :type gdf:     geopandas.GeoDataFrame
    :param bounds: Bounding box to clip to (``[xmin, ymin, xmax, ymax]``).
    :type bounds:  list[float]
    :return:       Clipped GeoDataFrame.
    :rtype:        geopandas.GeoDataFrame
    """

    # Bounds to Polygon
    bounds = Polygon([(bounds[0], bounds[1]), (bounds[2], bounds[1]), (bounds[2], bounds[3]), (bounds[0], bounds[3])])

    # Explode the geodataframe
    gdf_exploded = gpd.GeoDataFrame()
    for idx in gdf.index:
        # Get the geometries and keyword arguments of the geodataframe
        geometries = list(gdf.loc[idx, "geometry"].geoms)
        kwargs = gdf.loc[idx, "kwargs"]

        gdf_feature = gpd.GeoDataFrame({"index": [idx] * len(geometries), "geometry": geometries, "kwargs": [kwargs] * len(geometries)}, crs=gdf.crs)
        gdf_exploded = pd.concat([gdf_exploded, gdf_feature])
    gdf_exploded.reset_index(drop=True, inplace=True)

    # Clip the geodataframe
    gdf_clipped = gdf_exploded.copy()
    gdf_clipped["within"] = gdf_clipped["geometry"].within(bounds)
    gdf_clipped["intersects"] = gdf_clipped["geometry"].intersects(bounds)
    gdf_clipped = gdf_clipped[gdf_clipped["within"] | gdf_clipped["intersects"]]
    gdf_clipped.loc[gdf_clipped["intersects"], "geometry"] = gdf_clipped[gdf_clipped["intersects"]].intersection(bounds)
    gdf_clipped = gdf_clipped.drop(columns=["within", "intersects"])

    # Dissolve the geodataframe
    gdf_dissolved = gpd.GeoDataFrame()
    for idx in gdf_clipped["index"].unique():
        # Get the geometries and keyword arguments of the geodataframe
        geometries = list(gdf_clipped[gdf_clipped["index"] == idx]["geometry"])
        kwargs = gdf_clipped[gdf_clipped["index"] == idx]["kwargs"].iloc[0]

        # Split multi geometries into individual geometries
        geometries2 = []
        for geometry in geometries:
            if geometry.geom_type in ["MultiPolygon", "MultiLineString", "MultiPoint"]:
                geometries2.extend(list(geometry.geoms))
            else:
                geometries2.append(geometry)

        # Combine geometries into multi geometries of the same type
        if geometries2[0].geom_type == "Polygon":
            geometry = MultiPolygon(geometries2)
        elif geometries2[0].geom_type == "LineString":
            geometry = MultiLineString(geometries2)
        elif geometries2[0].geom_type == "Point":
            geometry = MultiPoint(geometries2)

        # Create a geodataframe for the feature
        gdf_feature = gpd.GeoDataFrame({"geometry": [geometry], "kwargs": [kwargs]}, index=[idx], crs=gdf.crs)

        # Concatenate the geodataframe to the dissolved geodataframe
        gdf_dissolved = pd.concat([gdf_dissolved, gdf_feature])

    # Return the dissolved geodataframe
    return gdf_dissolved


def get_gdf_cartopy(features=None, bounds=None, crs=None, buffer=0.1):
    """Get a GeoDataFrame with cartopy geometries.

    :param features: Cartopy features to include in the GeoDataFrame. If ``None``, all cartopy features are included.
    :type features:  list[str], optional
    :param bounds:   Bounds of the cartopy geometries (``[xmin, ymin, xmax, ymax]``).
    :type bounds:    list[float], optional
    :param crs:      Coordinate reference system of the cartopy geometries. If ``None``, the coordinate reference system is set to ``'EPSG:4326'``.
    :type crs:       str, optional
    :param buffer:   Buffer ratio to apply to the bounds before clipping the cartopy geometries.
    :type buffer:    float, optional
    :return:         GeoDataFrame with cartopy geometries.
    :rtype:          geopandas.GeoDataFrame

    See also: `cartopy.feature <https://scitools.org.uk/cartopy/docs/latest/matplotlib/feature_interface.html>`_.
    """

    # Define cartopy features and their styles
    CFEATURES = {
        "borders": cfeature.BORDERS,
        "coastline": cfeature.COASTLINE,
        "lakes": cfeature.LAKES,
        "land": cfeature.LAND,
        "ocean": cfeature.OCEAN,
        "rivers": cfeature.RIVERS,
        "states": cfeature.STATES,
    }
    KWARGS = {
        "borders": {"color": "black", "linewidth": 1, "linestyle": "-", "zorder": 0.03},
        "coastline": {"color": "black", "linewidth": 1, "linestyle": "-", "zorder": 0.03},
        "lakes": {"facecolor": [0.59375, 0.71484375, 0.8828125], "edgecolor": "none", "zorder": 0.02},
        "land": {"facecolor": [0.9375, 0.9375, 0.859375], "edgecolor": "none", "zorder": 0.01},
        "ocean": {"facecolor": [0.59375, 0.71484375, 0.8828125], "edgecolor": "none", "zorder": 0.01},
        "rivers": {"color": [0.59375, 0.71484375, 0.8828125], "linewidth": 1, "linestyle": "-", "zorder": 0.02},
        "states": {"facecolor": "none", "edgecolor": "black", "linewidth": 1, "linestyle": ":", "zorder": 0.03},
    }

    # Get the cartopy features
    if features is None:
        features = ["land", "ocean", "lakes", "rivers", "coastline", "borders", "states"]

    # Convert the crs to a pyproj.CRS
    if isinstance(crs, pyprojCRS):
        crs = crs
    elif isinstance(crs, rasterioCRS):
        crs = pyprojCRS.from_string(crs.to_string())
    elif isinstance(crs, str):
        crs = pyprojCRS.from_string(crs)
    elif crs is None:
        crs = "EPSG:4326"
    else:
        raise ValueError("CRS type not supported. Please provide a pyproj.CRS, rasterio.CRS or str object.")

    # Create a GeoDataFrame for the cartopy features
    gdf_cartopy_ls = []
    for feature in features:
        # Get the cartopy geometries
        geometries_ = list(CFEATURES[feature].with_scale("10m").geometries())

        # Combine geometries into one MultiPolygon or MultiLineString
        geometries = []
        for geometry in geometries_:
            if geometry.geom_type == "Polygon":
                geometries.append(geometry)
            elif geometry.geom_type == "MultiPolygon":
                geometries.extend(list(geometry.geoms))
            elif geometry.geom_type == "LineString":
                geometries.append(geometry)
            elif geometry.geom_type == "MultiLineString":
                geometries.extend(list(geometry.geoms))

        # Convert list of geometries to MultiPolygon or MultiLineString
        if geometries[0].geom_type == "Polygon":
            geometries = MultiPolygon(geometries)
        elif geometries[0].geom_type == "LineString":
            geometries = MultiLineString(geometries)

        # Create a GeoDataFrame for the cartopy feature
        gdf_cartopy_ls.append(gpd.GeoDataFrame({"geometry": [geometries], "kwargs": [KWARGS[feature]]}, index=[feature], crs="EPSG:4326"))

    # Concatenate the GeoDataFrame to the cartopy features
    gdf_cartopy = gpd.GeoDataFrame(pd.concat(gdf_cartopy_ls), crs="EPSG:4326")

    # Clip the cartopy geodataframe
    if bounds is not None:
        # Convert bounds to Polygon
        bounds = Polygon([(bounds[0], bounds[1]), (bounds[2], bounds[1]), (bounds[2], bounds[3]), (bounds[0], bounds[3])])

        # Get size of the bounds
        size = max(bounds.bounds[2] - bounds.bounds[0], bounds.bounds[3] - bounds.bounds[1])

        # Buffer the bounds
        bounds = bounds.buffer(size * buffer)

        # Reproject the bounds to EPSG:4326
        gdf_bounds = gpd.GeoDataFrame({"geometry": [bounds]}, crs=crs)
        gdf_bounds = gdf_bounds.to_crs("EPSG:4326")
        gdf_cartopy = _clip_gdf_cartopy(gdf_cartopy, gdf_bounds.total_bounds)

    # Reproject the cartopy geodataframe
    if crs != "EPSG:4326":
        gdf_cartopy = gdf_cartopy.to_crs(crs)

    # Remove invalid geometries
    for index in gdf_cartopy.index:
        geometries = gdf_cartopy.loc[index, "geometry"]
        if geometries.geom_type == "MultiPolygon":
            gdf_cartopy.loc[index, "geometry"] = MultiPolygon([geom for geom in geometries.geoms if geom.is_valid])
        elif geometries.geom_type == "MultiLineString":
            gdf_cartopy.loc[index, "geometry"] = MultiLineString([geom for geom in geometries.geoms if geom.is_valid])

    # Return the GeoDataFrame of cartopy features
    return gdf_cartopy


def _plot_gdf(gdf, ax, **kwargs):
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

    # Function to add arrow to plot
    def add_arrow_to_plot(ax, geometries, arrow_kwargs, plot_kwargs):
        if geometries[0].geom_type in ["LineString", "MultiLineString"]:
            # Convert the geometries to MultiLineString
            if geometries[0].geom_type == "LineString":
                lines = MultiLineString(list(geometries))
            else:
                lines = MultiLineString([line for lines in list(geometries) for line in lines.geoms])

            # Set the arrow_kwargs based on the plot_kwargs
            if arrow_kwargs is None:
                arrow_kwargs = plot_kwargs.copy()
            else:
                arrow_kwargs = {**plot_kwargs, **arrow_kwargs}
            arrow_kwargs.setdefault("arrowstyle", "-|>")
            arrow_kwargs.setdefault("mutation_scale", 20)
            arrow_kwargs.setdefault("shrinkA", 0)
            arrow_kwargs.setdefault("shrinkB", 0)
            if "color" not in arrow_kwargs:
                arrow_kwargs["edgecolor"] = "none"

            # Add arrow to last segment of each line
            for line in lines.geoms:
                x1, y1, x2, y2 = line.xy[0][-2], line.xy[1][-2], line.xy[0][-1], line.xy[1][-1]
                ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), **arrow_kwargs))

    # Function to add label to legend
    def add_label_to_legend(geometry, plot_label, kwargs):
        # Plot a point with label
        if geometry.geom_type in ["Point", "MultiPoint"]:
            if "markersize" in kwargs:
                kwargs["s"] = kwargs.pop("markersize")
            ax.scatter(np.nan, np.nan, label=plot_label, **kwargs)

        # Plot a line with label
        elif geometry.geom_type in ["LineString", "MultiLineString"]:
            ax.plot(np.nan, np.nan, label=plot_label, **kwargs)

        # Plot a polygon with label
        elif geometry.geom_type in ["Polygon", "MultiPolygon"]:
            kwargs.setdefault("zorder", 2)
            ax.add_patch(plt.Polygon(np.array([[np.nan, np.nan]]), label=plot_label, **kwargs))

    # Copy the GeoDataFrame to prevent changing the original GeoDataFrame
    gdf = gdf.copy().reset_index(drop=True)

    # Combine keyword arguments on GeoDataFrame with user keyword arguments, prioritising user keyword arguments
    if "kwargs" in gdf.columns:
        gdf["kwargs"] = gdf["kwargs"].apply(lambda x: {**x, **kwargs})
    else:
        gdf["kwargs"] = [kwargs] * len(gdf)

    # Add string representation of keyword arguments to GeoDataFrame
    gdf["kwargs_str"] = gdf["kwargs"].apply(lambda x: str(x))

    # Plot get the groups of GeoDataFrames with same string representation of keyword arguments
    gdf_groups = gdf.groupby("kwargs_str")

    # Sort GeoDataFrame based on minimum index
    gdf_groups = sorted(gdf_groups, key=lambda x: x[1].index.min())

    # Plot groups of GeoDataFrames with same string representation of keyword arguments
    for kwargs, gdf_group in gdf_groups:
        # Evaluate string representation of keyword arguments
        kwargs = gdf_group["kwargs"].iloc[0]

        # Seperate label from keyword arguments
        label = kwargs.pop("label", None)

        # Seperate add_arrow from keyword arguments
        add_arrow = kwargs.pop("add_arrow", False)

        # Seperate arrow_kwargs from keyword arguments
        arrow_kwargs = kwargs.pop("arrow_kwargs", None)

        # Plot geodataframe
        ax = gdf_group.plot(ax=ax, **kwargs)

        # Add arrow to plot
        if add_arrow:
            add_arrow_to_plot(ax, gdf_group["geometry"], arrow_kwargs, kwargs)

        # Add label to legend
        if label is not None and "column" not in kwargs:
            add_label_to_legend(gdf_group["geometry"].iloc[0], label, kwargs)

    # Return axis
    return ax


def plot_geometries(
    gdf,
    ax=None,
    xy_unit=None,
    xlim=None,
    ylim=None,
    xlabel_kwargs=None,
    ylabel_kwargs=None,
    title_kwargs=None,
    aspect_kwargs=None,
    grid_kwargs=None,
    append_axes_kwargs=None,
    **kwargs,
):
    """Plot a GeoDataFrame using plot.

    :param gdf:                GeoDataFrame to plot.
    :type gdf:                 geopandas.GeoDataFrame
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
    :param kwargs:             Keyword arguments for :func:`geopandas.GeoDataFrame.plot`.
    :type kwargs:              dict, optional
    :return:                   Axis.
    :rtype:                    matplotlib.axes.Axes

    :See also: `matplotlib.axis.set_xlabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xlabel.html>`_,
               `matplotlib.axis.set_ylabel <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_ylabel.html>`_,
               `matplotlib.axis.set_title <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html>`_,
               `matplotlib.axis.set_aspect <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>`_,
               `matplotlib.axis.grid <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.grid.html>`_,
               `mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes <https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.axes_grid1.axes_divider.AxesDivider.html#mpl_toolkits.axes_grid1.axes_divider.AxesDivider.append_axes>`_,
               `geopandas.GeoDataFrame.plot <https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.plot.html>`_.
    """

    # Initialise axis
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Get the rescale parameters
    scale_factor, _, _ = rpc.rescale.get_rescale_parameters(data=gdf, xy_unit=xy_unit)

    # Rescale the GeoDataFrame
    gdf = rpc.rescale.rescale(data=gdf, scale_factor=scale_factor)

    # Append colorbar axis
    print("Here.")
    print(f"append_axes_kwargs: {append_axes_kwargs}")
    print(f"kwargs: {kwargs}")
    if append_axes_kwargs is not None and "cax" not in kwargs and "legend" in kwargs and kwargs["legend"]:
        print("Appending colorbar axis to the plot.")
        kwargs["cax"] = rpc.axes.append_cbar_axis(ax, append_axes_kwargs)

    # Plot GeoDataFrame
    ax = _plot_gdf(gdf, ax=ax, **kwargs)

    # Format axis
    ax = rpc.axes.format(
        data=gdf,
        ax=ax,
        xy_unit=xy_unit,
        xlim=xlim,
        ylim=ylim,
        xlabel_kwargs=xlabel_kwargs,
        ylabel_kwargs=ylabel_kwargs,
        title_kwargs=title_kwargs,
        aspect_kwargs=aspect_kwargs,
        grid_kwargs=grid_kwargs,
    )

    # Return axis
    return ax
