import folium
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
import numpy as np
from branca.element import Element, Figure
from folium.plugins import Draw

def _explore_image(da, m, cmap='Spectral_r', vmin=None, vmax=None, legend=None, legend_kwds={}, **kwargs):    
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
    kwargs.setdefault('mercator_project', True)
    
    # Normalise values
    da = ((da - vmin) / (vmax - vmin)).clip(0, 1)

    # Get colors
    if da.ndim == 2 or (da.ndim == 3 and da.shape[0] == 1):
        rgba = cmap(da.values).reshape((*da.shape, 4))
    elif da.ndim == 3 and da.shape[0] == 3:
        rgb = da.values.transpose(1, 2, 0)
        rgba = np.concatenate([rgb, np.ones((*rgb.shape[:2], 1))], axis=2)
    else:
        raise ValueError('DataArray must be 2D or 3D with shape (3, y, x)')
    
    # Fix color range for mercator projection
    if 'mercator_project' in kwargs and kwargs['mercator_project']:
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
        bounds = [[min(bounds[0][0], map_bounds[0][0]), min(bounds[0][1], map_bounds[0][1])],
                  [max(bounds[1][0], map_bounds[1][0]), max(bounds[1][1], map_bounds[1][1])]]

    # Set bounds
    m.fit_bounds(bounds)

    # Return map
    return m

def pcolormesh(da, m=None, skip=1, smooth=1, **kwargs):
    return imshow(da, m=m, skip=skip, smooth=smooth, **kwargs)

def imshow(da, m=None, skip=1, smooth=1, **kwargs):
    # Reproject DataArray
    if da.rio.crs != 'EPSG:4326':
        print("\033[93m Reprojecting DataArray to EPSG:4326.\033[0m")
        da = da.rio.reproject('EPSG:4326')
    
    # Get map
    if m is None:
         m = folium.Map()

    # Set map bounds
    m = _set_map_bounds(m, da.rio.bounds())

    # Reproject DataArray
    if da.rio.crs != 'EPSG:4326':
        da = da.rio.reproject('EPSG:4326')

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
    raise NotImplementedError('scatter plot not implemented yet')

def contourf(da, m=None, skip=1, smooth=1, **kwargs):
    raise NotImplementedError('contourf plot not implemented yet')

def contour(da, m=None, skip=1, smooth=1, **kwargs):
    raise NotImplementedError('contour plot not implemented yet')

def quiver(da, m=None, skip=1, smooth=1, **kwargs):
    raise NotImplementedError('quiver plot not implemented yet')

def streamplot(da, m=None, skip=1, smooth=1, **kwargs):
    raise NotImplementedError('streamplot plot not implemented yet')

def plot_geometries(gdf, m=None, **kwargs):
    # Reproject GeoDataFrame
    if gdf.crs != 'EPSG:4326':
        print("\033[93m Reprojecting GeoDataFrame to EPSG:4326.\033[0m")
        gdf = gdf.to_crs('EPSG:4326')
    
    # Get map
    if m is None:
         m = folium.Map()

    # Set map bounds
    m = _set_map_bounds(m, gdf.total_bounds)

    # Plot GeoDataFrame
    gdf.explore(m=m, **kwargs)

    # Return plot
    return m

class Draw(Draw):
    def render(self, **kwargs):
        super().render(**kwargs)

        figure = self.get_root()
        assert isinstance(
            figure, Figure
        ), "You cannot render this Element if it is not in a Figure."

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
            figure.header.add_child(Element(export_style), name="export")
            figure.html.add_child(Element(export_button), name="export_button")