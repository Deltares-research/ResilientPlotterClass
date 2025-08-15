import branca
import folium
import geopandas as gpd
import ipyleaflet
import ipywidgets
import matplotlib.pyplot as plt
import numpy as np
import xyzservices
from folium.plugins import Draw
from matplotlib.colors import to_hex


def _explore_image(da, m, cmap="Spectral_r", vmin=None, vmax=None, legend=None, legend_kwds={}, **kwargs):
    """ "Plot data interactively using folium.

    :param da:          Data to plot.
    :type da:           xarray.DataArray
    :param m:           Folium map to plot on.
    :type m:            folium.Map, optional
    :param cmap:        Colormap to use.
    :type cmap:         str, optional
    :param vmin:        Minimum value for colormap.
    :type vmin:         float, optional
    :param vmax:        Maximum value for colormap.
    :type vmax:         float, optional
    :param legend:      Whether to show legend.
    :type legend:       bool, optional
    :param legend_kwds: Keyword arguments for legend.
    :type legend_kwds:  dict, optional
    :param kwargs:      Keyword arguments for :func:`folium.raster_layers.ImageOverlay`.
    :type kwargs:       dict, optional
    :return:            Plot.
    :rtype:             folium.Map

    :See also: `folium.raster_layers.ImageOverlay <https://python-visualization.github.io/folium/latest/reference.html#folium.raster_layers.ImageOverlay>`_
    :See also: `folium.LinearColormap <https://python-visualization.github.io/folium/latest/advanced_guide/colormaps.html>`_
    """

    # Convert da to number
    if not np.issubdtype(da.dtype, np.number):
        da = da.astype(float)

    # Get cmap
    cmap = plt.get_cmap(cmap)

    # Get vmin and vmax
    if vmin is None:
        vmin = da.min().values
    if vmax is None:
        vmax = da.max().values

    # Get legend
    if legend is None:
        legend = True if da.ndim == 2 else False

    # Default kwargs
    kwargs.setdefault("mercator_project", True)

    # Normalise values
    da = ((da - vmin) / (vmax - vmin)).clip(0, 1)

    # Get colors
    if da.ndim == 2 or (da.ndim == 3 and da.shape[0] == 1):
        rgba = cmap(da.values).reshape((*da.shape, 4))
    elif da.ndim == 3 and da.shape[0] == 3:
        rgb = da.values.transpose(1, 2, 0)
        rgba = np.concatenate([rgb, np.ones((*rgb.shape[:2], 1))], axis=2)
    else:
        raise ValueError("DataArray must be 2D or 3D with shape (3, y, x)")

    # Fix color range for mercator projection
    if "mercator_project" in kwargs and kwargs["mercator_project"]:
        # Find first two non-nan values
        nan_indices = np.where(np.isnan(da.values))

        # If there are less than two non-nan values, set first two values to 0 and 1
        if len(nan_indices[0]) < 2:
            nan_indices = (np.array([0, 0]), np.array([0, 1]))

        # Set first two values to 0 and 1
        rgba[nan_indices[0][0], nan_indices[1][0], :3] = 0
        rgba[nan_indices[0][1], nan_indices[1][1], :3] = 1

    # Convert range to 0-255
    rgba = (rgba * 255).astype(np.uint8)

    # Get bounds
    bounds = da.rio.bounds()
    bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]

    # Create image
    img = folium.raster_layers.ImageOverlay(image=rgba, bounds=bounds, **kwargs)

    # Add to map
    m.add_child(img)

    # Add legend
    if legend:
        # Get colors
        colors = cmap(np.linspace(0, 1, 256))

        # Convert colors to hex
        colors = [to_hex(color) for color in colors]

        # Create colormap
        cmap = folium.LinearColormap(colors, vmin=vmin, vmax=vmax, **legend_kwds)

        # Add to map
        m.add_child(cmap)

    # Return map
    return m


def _set_map_bounds(m, bounds):
    # Convert bounds to list
    bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]

    # Get map bounds
    map_bounds = m.get_bounds()

    # Combine bounds
    if np.all(np.array(map_bounds) != None):
        bounds = [
            [min(bounds[0][0], map_bounds[0][0]), min(bounds[0][1], map_bounds[0][1])],
            [max(bounds[1][0], map_bounds[1][0]), max(bounds[1][1], map_bounds[1][1])],
        ]

    # Set bounds
    m.fit_bounds(bounds)

    # Return map
    return m


class _Draw(Draw):
    """Wrapper for folium.plugins.Draw to add a button to export the map.

    :param Draw: Folium Draw object.
    :type Draw: folium.plugins.Draw
    """

    def render(self, **kwargs):
        super().render(**kwargs)

        figure = self.get_root()
        assert isinstance(figure, branca.element.Figure), "You cannot render this Element if it is not in a Figure."

        export_style = """
            <style>
                #export {
                    position: absolute;
                    bottom: 12px;
                    left: 12px;
                    z-index: 1000;
                    background: white;
                    outline: 2px solid rgba(0, 0, 0, 0.2);
                    padding: 7px;
                    border-radius: 2px;
                    cursor: pointer;
                    font-size: 12px;
                    text-decoration: none;
                }

                #export:hover {
                    background: #f0f0f0;
                }
            </style>
        """
        export_button = """<a href='#' id='export'>💾</a>"""
        if self.export:
            # Add button to figure
            figure.header.add_child(branca.element.Element(export_style), name="export")
            figure.html.add_child(branca.element.Element(export_button), name="export_button")


def pcolormesh(da, m=None, skip=1, smooth=1, **kwargs):
    raise NotImplementedError("pcolormesh plot not implemented yet")


def imshow(da, m=None, skip=1, smooth=1, **kwargs):
    """Plot data interactively using imshow.

    :param da:     Data to plot.
    :type da:      xarray.DataArray
    :param m:      Folium map to plot on.
    :type m:       folium.Map, optional
    :param skip:   Plot every nth value in x and y direction.
    :type skip:    int, optional
    :param smooth: Smooth data array with rolling mean in x and y direction.
    :type smooth:  int, optional
    :param xlim:   x limits.
    :type xlim:    list[float], optional
    :param ylim:   y limits.
    :type ylim:    list[float], optional

    :param kwargs: Keyword arguments for :func:`resilientplotterclass.interactive._explore_image`.
    :type kwargs:  dict, optional
    :return:       Plot.
    :rtype:        folium.Map
    """

    # Reproject DataArray
    if da.rio.crs != "EPSG:4326":
        print("\033[93mReprojecting DataArray to EPSG:4326.\033[0m")
        da = da.rio.reproject("EPSG:4326")

    # Get map
    if m is None:
        m = folium.Map()

    # Set map bounds
    m = _set_map_bounds(m, da.rio.bounds())

    # Reproject DataArray
    if da.rio.crs != "EPSG:4326":
        da = da.rio.reproject("EPSG:4326")

    # Skip DataArray values
    if skip > 1:
        da = da.isel(x=slice(None, None, skip), y=slice(None, None, skip))

    # Smooth DataArray
    if smooth > 1:
        da = da.rolling(x=smooth, center=True).mean().rolling(y=smooth, center=True).mean()

    # Plot DataArray
    m = _explore_image(da, m=m, **kwargs)

    # Return plot
    return m


def scatter(da, m=None, skip=1, smooth=1, **kwargs):
    raise NotImplementedError("scatter plot not implemented yet")


def contourf(da, m=None, skip=1, smooth=1, **kwargs):
    raise NotImplementedError("contourf plot not implemented yet")


def contour(da, m=None, skip=1, smooth=1, **kwargs):
    raise NotImplementedError("contour plot not implemented yet")


def quiver(da, m=None, skip=1, smooth=1, **kwargs):
    raise NotImplementedError("quiver plot not implemented yet")


def streamplot(da, m=None, skip=1, smooth=1, **kwargs):
    raise NotImplementedError("streamplot plot not implemented yet")


def plot_geometries(gdf, m=None, **kwargs):
    """Plot geometries interactively using folium.

    :param gdf:    GeoDataFrame to plot.
    :type gdf:     geopandas.GeoDataFrame
    :param m:      Folium map to plot on.
    :type m:       folium.Map, optional
    :param kwargs: Keyword arguments for :func:`geopandas.explore`.
    :type kwargs:  dict, optional
    :return:       Plot.
    :rtype:        folium.Map

    :See also: `geopandas.explore <https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html>`_
    """

    # Reproject GeoDataFrame
    if gdf.crs != "EPSG:4326":
        print("\033[93mReprojecting GeoDataFrame to EPSG:4326.\033[0m")
        gdf = gdf.to_crs("EPSG:4326")

    # Get map
    if m is None:
        m = folium.Map()

    # Set map bounds
    m = _set_map_bounds(m, gdf.total_bounds)

    # Plot GeoDataFrame
    gdf.explore(m=m, **kwargs)

    # Return plot
    return m


def plot_basemap(m=None, **kwargs):
    """Plot basemaps interactively using folium.

    :param m:      Folium map to plot on.
    :type m:       folium.Map, optional
    :param kwargs: Keyword arguments for :func:`folium.Map`.
    :type kwargs:  dict, optional
    :return:       Plot.
    :rtype:        folium.Map

    :See also: `folium.TileLayer <https://python-visualization.github.io/folium/latest/reference.html#folium.raster_layers.TileLayer>`_
    """

    # Get map
    if m is None:
        m = folium.Map()
    # Plot basemap
    folium.TileLayer(**kwargs).add_to(m)

    # Return plot
    return m


class Draw_Map(ipyleaflet.Map):
    """
    A class to create a map to draw geometries.
    """

    STYLE = {"weight": 2}

    def __init__(
        self,
        center: tuple[float] = None,
        zoom: int = 8,
        basemap: xyzservices.TileProvider = ipyleaflet.basemaps.OpenStreetMap.Mapnik,
        file_path_gdf: str = None,
        gdf: gpd.GeoDataFrame = None,
        **kwargs,
    ):
        """Constructor for the draw map class.

        :param center:        Center of the map.
        :type center:         tuple[float], optional
        :param zoom:          Zoom level of the map.
        :type zoom:           int, optional
        :param basemap:       Basemap layer for the map.
        :type basemap:        xyzservices.TileProvider, optional
        :param file_path_gdf: File path to the GeoDataFrame file.
        :type file_path_gdf:  str, optional
        :param gdf:           GeoDataFrame to display on the map.
        :type gdf:            gpd.GeoDataFrame, optional
        """
        # Get geometries from file or list
        gdf = None
        if file_path_gdf is not None:
            gdf = gpd.read_file(file_path_gdf).to_crs("EPSG:4326")
        elif gdf is not None and not gdf.empty:
            gdf = gpd.GeoDataFrame(geometry=gdf, crs="EPSG:4326")

        # Get center of the map
        if center is None and gdf is not None and not gdf.empty:
            centroid = gdf.geometry.union_all().representative_point()
            center = (centroid.y, centroid.x)

        # Set default kwargs
        kwargs.setdefault("scroll_wheel_zoom", True)  # Enable scroll wheel zoom
        kwargs.setdefault("attribution_control", False)  # Disable attribution control
        kwargs.setdefault("layout", ipywidgets.Layout(height="600px", width="100%"))  # Set layout height and width

        # Initialize map superclass
        super().__init__(center=center, zoom=zoom, basemap=basemap, **kwargs)

        # Initialise draw control
        self.draw_control = ipyleaflet.DrawControl(
            polygon={"shapeOptions": self.STYLE},
            rectangle={"shapeOptions": self.STYLE},
            circlemarker={"shapeOptions": self.STYLE},
            polyline={"shapeOptions": self.STYLE},
        )

        # Add draw control to the map
        self.add_control(self.draw_control)

        # Set geometries to the map
        if gdf is not None and not gdf.empty:
            self.set_geometries(gdf)
            self.fit_bounds(gdf.total_bounds)

    def set_geometries(self, gdf: gpd.GeoDataFrame) -> None:
        """Set geometries to the map.

        :param aoi: The GeoDataFrame containing the geometries.
        :type aoi: gpd.GeoDataFrame

        Returns:
            None
        """
        # Update draw flag
        self.drawn = True

        # Add style to GeoDataFrame
        gdf["style"] = [self.STYLE] * len(gdf)

        # Add geometries to the draw control
        self.draw_control.data = self.draw_control.data + list(gdf.iterfeatures())

    def get_geometries(self, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
        """
        Get geometries from the map.

        Args:
            crs (str): The coordinate reference system to reproject the geometries to.
        Returns:
            gpd.GeoDataFrame: A GeoDataFrame containing the geometries from the map.
        """
        # Get geometries from the map
        if not self.draw_control.data:
            gdf = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")
        else:
            gdf = gpd.GeoDataFrame.from_features(self.draw_control.data, crs="EPSG:4326").drop(columns="style")

        # Reproject geometries
        gdf = gdf.to_crs(crs)

        return gdf
