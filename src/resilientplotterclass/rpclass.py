# Packages
import folium
import geopandas as gpd
import html
import inspect
from IPython.display import display, HTML
import json
import matplotlib.pyplot as plt
import os
import pandas as pd
from pyproj import CRS as pyprojCRS
from rasterio.crs import CRS as rasterioCRS
import xarray as xr
import xugrid as xu
import resilientplotterclass as rpc

# Resilient Plotter Class
class rpclass:
    # =============================================================================
    # Constructor
    # =============================================================================
    def __init__(self, project_guidelines=None, cartopy=False):
        """Constructor for the resilient plotter class.

        :param project_guidelines: File path to the project guidelines file or dictionary with project guidelines.
        :type project_guidelines:  str, optional
        :param cartopy:            Set cartopy geometries.
        :type cartopy:             bool, optional
        :return:                   None.
        :rtype:                    None
        """

        # Set guidelines
        self.set_guidelines(project_guidelines)

        # Set cartopy geometries
        if cartopy:
            self.set_cartopy()
        else:
            self.gdf_cartopy = None
        
        # Register colormaps
        rpc.colormaps.register_colormaps()
        import colorcet as cc    # See also: https://colorcet.holoviz.org/
        import cmocean.cm as cmo # See also: https://matplotlib.org/cmocean/

    # =============================================================================
    # Guideline support methods
    # =============================================================================
    # Combine dictionaries recursively
    def _combine_dictionaries(self, dict1, dict2, max_depth=4):
        """Recursively combine dictionaries, prioritising dictionary 2.

        :param dict1:     Dictionary 1.
        :type dict1:      dict
        :param dict2:     Dictionary 2.
        :type dict2:      dict
        :param max_depth: Maximum depth to combine dictionaries.
        :type max_depth:  int, optional
        :return:          Combined dictionary.
        :rtype:           dict
        """

        # Maximum depth reached --> return dictionary 2
        if max_depth == 0:
            return dict2

        # Both dictionaries are not dictionaries --> return dictionary 2
        if not isinstance(dict1, dict) and not isinstance(dict2, dict):
            return dict2
        
        # Dictionary 1 is not a dictionary --> return dictionary 2
        elif not isinstance(dict1, dict):
            return dict2
        
        # Dictionary 2 is not a dictionary --> return dictionary 1
        elif not isinstance(dict2, dict):
            return dict1
        
        # Both dictionaries are dictionaries --> combine dictionaries
        keys = list(dict1.keys()) + list(dict2.keys())
        dict3 = {}
        for key in keys:
            # Key not in dictionary 1 --> use dictionary 2
            if not key in dict1.keys():
                dict3[key] = dict2[key]

            # Key not in dictionary 2 --> use dictionary 1
            elif not key in dict2.keys():
                dict3[key] = dict1[key]
            
            # Key in both dictionaries --> combine dictionaries
            else:
                dict3[key] = self._combine_dictionaries(dict1[key], dict2[key], max_depth=max_depth-1)
        
        # Return combined dictionary
        return dict3
    
    # Substitute string in dictionary
    def _substitute_str_in_dict(self, dict1, org_str=None, new_str=None):
        """Recursively substitute string in dictionary.

        :param dict1:   Dictionary.
        :type dict1:    dict
        :param org_str: Original string to substitute.
        :type org_str:  str
        :param new_str: New string to substitute.
        :type new_str:  str
        :return:        Dictionary with substituted strings.
        :rtype:         dict
        """

        # Check if original string and new string are set
        if org_str is None or new_str is None:
            return dict1

        # Substitute string in dictionary
        for key, value in dict1.items():
            if isinstance(value, dict):
                dict1[key] = self._substitute_str_in_dict(value, org_str, new_str)
            elif isinstance(value, str):
                dict1[key] = value.replace(org_str, new_str)

        # Return dictionary with substituted strings
        return dict1
    
    # Remove conflicting kwargs
    def _remove_conflicting_kwargs(self, dict1, plot_style=None, warn=True, reverse=True):
        """ Remove conflicting kwargs from dictionary, prioritising the last kwargs.

        :param dict1:     Dictionary.
        :type dict1:      dict
        :param plot_style: Plot style.
        :type plot_style:  str
        :param warn:      Print warning if conflicting kwargs.
        :type warn:       bool, optional
        :return:          Dictionary without conflicting kwargs.
        :rtype:           dict
        """

        # Check if dictionary must be reversed
        i = -1 if reverse else 1

        # Define conflicting kwargs
        CONFLICT_DICT = {'color': ['cmap'],
                         'colors': ['cmap'],
                         'cmap': ['color', 'colors']}

        # Remove conflicting kwargs
        dict2 = {}
        for key in list(dict1.keys())[::i]:
            if key not in CONFLICT_DICT.keys():
                dict2[key] = dict1[key]
            elif not any([conflict in dict2.keys() for conflict in CONFLICT_DICT[key]]):
                dict2[key] = dict1[key]
            elif warn:
                key2 = [key2 for key2 in CONFLICT_DICT[key] if key2 in dict2.keys()][0]
                print("\033[93m Warning: Conflicting kwargs ('{}' and '{}') using '{}'. \033[0m".format(key2, key, key2))
        
        # Remove conflicting kwargs for colorbar
        if ('add_colorbar' in dict2.keys() and not dict2['add_colorbar']) or (plot_style in ['contour', 'quiver', 'streamplot'] and 'add_colorbar' not in dict2.keys()):
            if 'cbar_kwargs' in dict2.keys():
                dict2.pop('cbar_kwargs')
                print("\033[93m Warning: 'cbar_kwargs' removed because 'add_colorbar' is False. \033[0m")

        # Return dictionary without conflicting kwargs
        return dict2

    # Get keyword arguments
    def _get_kwargs(self, data_style=None, geom_style=None, map_style=None, extent_style=None, interactive=False, show_kwargs=False, **kwargs):
        """Get keyword arguments.

        :param data_style:   Data type from guidelines.
        :type data_style:    str, optional
        :param geom_style:   Geometry type from guidelines.
        :type geom_style:    str, optional
        :param map_style:    Map type from guidelines.
        :type map_style:     str, optional
        :param extent_style: Extent type from guidelines.
        :type extent_style:  str, optional
        :param interactive:  Interactive plot.
        :type interactive:   bool, optional
        :param show_kwargs:  Show keyword arguments.
        :type show_kwargs:   bool, optional
        :param kwargs:       Keyword arguments.
        :type kwargs:        dict, optional
        :return:             Keyword arguments.
        :rtype:              dict
        """
        # Get parameters and arguments
        parameters, arguments = [], []
        if data_style is not None:
            parameters.append('data_style' if not interactive else 'interactive_data_style')
            arguments.append(data_style)
        if geom_style is not None:
            parameters.append('geom_style' if not interactive else 'interactive_geom_style')
            arguments.append(geom_style)
        if map_style is not None:
            parameters.append('map_style' if not interactive else 'interactive_map_style')
            arguments.append(map_style)
        if extent_style is not None:
            parameters.append('extent_style' if not interactive else 'interactive_extent_style')
            arguments.append(extent_style)
        
        # Get plot type (name of the function calling this method)
        plot_style = inspect.stack()[1].function

        # Get guidelines
        guideline_kwargs_ls = []
        for parameter, argument in zip(parameters, arguments):
            # Check if parameter and argument are in guidelines
            if parameter not in self.guidelines.keys():
                raise ValueError("{} not in guidelines. Available: {}".format(parameter, list(self.guidelines.keys())))
            if argument not in self.guidelines[parameter].keys():
                raise ValueError("{} '{}' not in guidelines. Available: {}".format(parameter, argument, list(self.guidelines[parameter].keys())))
            
            if parameter in ['data_style', 'interactive_data_style']:
                # Check if plot_style is in guidelines
                if plot_style not in self.guidelines[parameter][argument].keys():
                    raise ValueError('plot_style {} not in guidelines. Available: {}'.format(plot_style, list(self.guidelines[parameter][argument].keys())))
                guideline_kwargs_ls.append(self.guidelines[parameter][argument][plot_style].copy())
            else:
                guideline_kwargs_ls.append(self.guidelines[parameter][argument].copy())

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        if not interactive:
            kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        for guideline_kwargs in guideline_kwargs_ls:
            kwargs = self._combine_dictionaries(guideline_kwargs, kwargs)
        
        # Remove conflicting kwargs
        kwargs = self._remove_conflicting_kwargs(kwargs, plot_style)

        # Show keyword arguments
        if show_kwargs:
            print('Keyword arguments for {}: {}'.format(plot_style, kwargs))
        
        # Return keyword arguments
        return kwargs

    # Show guideline levels
    def _show_guideline_levels(self, dict1, level, indent):
        """Recursively show guideline levels.

        :param dict:   Dictionary.
        :type dict:    dict
        :param level:  Level of the dictionary.
        :type level:   int
        :param indent: Indent for the dictionary.
        :type indent:  int
        :return:       HTML string of the dictionary.
        :rtype:        str
        """

        indent_px = indent * level
        html_str = ""

        for key, value in dict1.items():
            safe_key = html.escape(str(key))
            if isinstance(value, dict):
                html_str += f"""
                <div style="margin-left: {indent_px}px">
                    <details>
                        <summary><strong>{safe_key}</strong></summary>
                        {self._show_guideline_levels(value, level + 1, indent)}
                    </details>
                </div>
                """
            else:
                safe_value = html.escape(str(value))
                html_str += f"""
                <div style="margin-left: {indent_px}px">
                    <strong>{safe_key}:</strong> {safe_value}
                </div>
                """

        return html_str

    # Get guideline origins dataframe
    def _get_df_guideline_origins(self, guidelines, default_guidelines, project_guidelines):
        """Get guideline origins dataframe.

        :param guidelines:         Guidelines.
        :type guidelines:          dict
        :param default_guidelines: Default guidelines.
        :type default_guidelines:  dict
        :param project_guidelines: Project guidelines.
        :type project_guidelines:  dict
        :return:                   Guideline origins dataframe.
        :rtype:                    pandas.DataFrame
        """
        
        # Get guidelines
        def _get_guideline(guidelines, parameter, argument, method):
            if parameter in guidelines.keys() and parameter == 'data_style' and argument in guidelines[parameter].keys() and method in guidelines[parameter][argument].keys():
                guideline = guidelines[parameter][argument][method] # Data type
            elif parameter in guidelines.keys() and parameter == 'geom_style' and argument in guidelines[parameter].keys() and method in ['grid', 'geometries']:
                guideline = guidelines[parameter][argument] # Geom type
            elif parameter in guidelines.keys() and parameter == 'map_style' and argument in guidelines[parameter].keys() and method in ['basemap']:
                guideline = guidelines[parameter][argument] # Map type
            elif parameter in guidelines.keys() and parameter == 'extent_style' and argument in guidelines[parameter].keys():
                guideline = guidelines[parameter][argument] # Extent type
            else:
                guideline = None
            return guideline
        
        # Compare guidelines
        def _compare_guidelines(guidelines, default_guidelines, project_guidelines, parameter, argument, method):
            # Get guidelines
            guideline = _get_guideline(guidelines, parameter, argument, method)
            default_guideline = _get_guideline(default_guidelines, parameter, argument, method)
            project_guideline = _get_guideline(project_guidelines, parameter, argument, method)

            # Compare guidelines
            if guideline is None:
                return '' # No guidelines
            elif guideline == default_guideline and guideline == project_guideline:
                return 'D=P' # Default guideline equal to project guideline
            elif guideline == default_guideline:
                return 'D' # Default guideline
            elif guideline == project_guideline:
                return 'P' # Project guideline
            else:
                return 'D+P' # Default guideline merged with project guideline

        # Initialise lists
        parameters = []
        arguments = []
        methods = {'pcolormesh': [], 'imshow': [], 'scatter': [], 'contourf': [], 'contour': [],
                    'quiver': [], 'streamplot': [], 'grid': [], 'geometries': [], 'basemap': [], 'cartopy': []}

        # Add parameters, arguments and methods
        styles = ['data_style', 'geom_style', 'map_style', 'extent_style', 'interactive_data_style', 'interactive_geom_style', 'interactive_map_style', 'interactive_extent_style']
        for parameter in styles:
            if parameter not in guidelines.keys():
                continue
            for argument in guidelines[parameter]:
                parameters.append(parameter)
                arguments.append(argument)
                for method in methods.keys():
                    methods[method].append(_compare_guidelines(guidelines, default_guidelines, project_guidelines, parameter, argument, method))

        # Create dataframe
        df_guideline_origins = pd.DataFrame({'parameter': parameters, 'argument': arguments, **methods})

        # Set multi-index
        df_guideline_origins = df_guideline_origins.set_index(['parameter', 'argument'])

        # Reindex dataframe
        df_guideline_origins = df_guideline_origins.reindex(styles, level=0)

        # Return dataframe
        return df_guideline_origins

    # =============================================================================
    # Guidelines methods
    # =============================================================================
    # Set guidelines
    def set_guidelines(self, project_guidelines=None):
        """Set guidelines.

        :param project_guidelines: File path to the project guidelines file or dictionary with project guidelines.
        :type project_guidelines:  str or dict, optional
        :return:                   None.
        :rtype:                    None
        """

        # Read default guidelines
        dir_path_guidelines = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guidelines')
        with open(os.path.join(dir_path_guidelines, 'default.json')) as f:
            default_guidelines = json.load(f)
        
        # Read project guidelines
        if project_guidelines is None:
            project_guidelines = {}
        elif isinstance(project_guidelines, dict):
            project_guidelines = project_guidelines
        elif isinstance(project_guidelines, str):
            __, ext = os.path.splitext(project_guidelines)
            if ext == '':
                project_guidelines = project_guidelines + '.json'
            elif ext != '.json':
                raise ValueError('Project guidelines must be a json file. Received: {}'.format(ext))
            if os.path.exists(os.path.join(dir_path_guidelines, project_guidelines)) and not os.path.exists(project_guidelines):
                project_guidelines = os.path.join(dir_path_guidelines, project_guidelines)
            with open(project_guidelines) as f:
                project_guidelines = json.load(f)
        else:
            raise ValueError('Project guidelines must be a file path (str) or a dictionary (dict). Received: {}'.format(type(project_guidelines)))

        # Combine guidelines, prioritising project guidelines
        guidelines = self._combine_dictionaries(default_guidelines, project_guidelines)

        # Substitute strings in guidelines
        guidelines = self._substitute_str_in_dict(guidelines, '@vrl', guidelines['general']['vrl'])

        # Remove conflicting kwargs from guidelines
        guidelines = self._remove_conflicting_kwargs(guidelines, warn=False, reverse=False)

        # Set guidelines
        self.guidelines = guidelines

        # Set guideline origins dataframe
        self._df_guideline_origins = self._get_df_guideline_origins(guidelines, default_guidelines, project_guidelines)
    
    # Get guidelines
    def get_guidelines(self):
        """Get guidelines.

        :return: Guidelines.
        :rtype:  dict
        """

        # Return guidelines
        return self.guidelines
    
    # Show guidelines
    def show_guidelines(self, indent=20, open=True):
        """Show guidelines.

        :return: None.
        :rtype:  None
        """

        # Set open
        open = 'open' if open else 'closed'

        # Show guidelines
        html_str = f"""
        <details {open}>
            <summary><strong>Guidelines</strong></summary>
            <div style="margin-left: {indent}px">
                {self._show_guideline_levels(self.get_guidelines(), 0, indent)}
            </div>
        </details>
        """
        display(HTML(html_str))
    
    # Show guideline origins
    def show_guideline_origins(self):
        """Show guideline origins.

        :return: None.
        :rtype:  None
        """

        # Show guidelines
        self.show_guidelines(open=False)

        # Show guideline origins dataframe
        style = self._df_guideline_origins.style
        for _, df_group in self._df_guideline_origins.groupby(level=0):
            style = style.set_properties(**{'text-align': 'center'})
            style = style.set_table_styles({df_group.index[0]: [{'selector': '', 'props': 'border-top: 2px solid black'}]}, overwrite=False, axis=1)
        style = style.set_caption('Guideline Origins (D: Default, P: Project, D=P: Default equal to Project, D+P: Default merged with Project)')
        style = style.set_table_styles([{'selector': 'thread', 'props': [('border-top', '2px solid black')]},
                                {'selector': 'caption', 'props': [('font-weight', 'bold')]}], overwrite=False)
        display(style)
        
    # =============================================================================
    # Cartopy methods
    # =============================================================================
    # Set cartopy
    def set_cartopy(self, features=None, bounds=None, crs=None, buffer=0.1):
        """Set cartopy geometries.

        :param features: List of features to get.
        :type features:  list[str], optional
        :param bounds:   Bounds of the cartopy geometries (``[xmin, ymin, xmax, ymax]``).
        :type bounds:    list[float], optional
        :param crs:      Coordinate reference system of the cartopy geometries.
        :type crs:       str, optional
        :param buffer:   Buffer ratio to apply to the bounds.
        :return:         None.
        :rtype:          None
        """
        
        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        features = self.guidelines['general']['cartopy_features'] if features is None else features
        bounds = self.guidelines['general']['cartopy_bounds'] if bounds is None else bounds
        crs = self.guidelines['general']['crs'] if crs is None else crs

        # Set cartopy geometries
        self.gdf_cartopy = rpc.geometries.get_gdf_cartopy(features=features, bounds=bounds, crs=crs, buffer=buffer)

    # Get cartopy
    def get_cartopy(self):
        """Get cartopy geometries.

        :return: Cartopy geometries.
        :rtype:  geopandas.GeoDataFrame
        """

        # Set cartopy geometries if not set
        if self.gdf_cartopy is None:
            self.set_cartopy()

        # Return cartopy geometries
        return self.gdf_cartopy
    
    # =============================================================================
    # Plot support methods
    # =============================================================================
    # Create figure and axes
    def subplots(self, *args, **kwargs):
        """Create figure and axes.

        :param args:  Positional arguments for :func:`matplotlib.pyplot.subplots`.
        :type args:   tuple, optional
        :param kwargs: Keyword arguments for :func:`matplotlib.pyplot.subplots`.
        :type kwargs:  dict, optional
        :return:       Figure and axes.
        :rtype:        tuple[matplotlib.figure.Figure, numpy.ndarray[matplotlib.axes.Axes]]

        See also: `matplotlib.pyplot.subplots() <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html>`_
        """

        # Create subplots
        fig, axs = plt.subplots(*args, **kwargs)
        
        # Return figure and axes
        return fig, axs
    
    def map(self, **kwargs):
        """Create map.

        :param kwargs: Keyword arguments for :func:`folium.Map`.
        :type kwargs:  dict, optional
        :return:       Map.
        :rtype:        folium.Map

        See also: `folium.Map() <https://python-visualization.github.io/folium/modules.html#folium.folium.Map>`_
        """

        # Create map
        m = folium.Map(**kwargs)

        # Create map
        return m
        
    # Show figure
    def show(self, fig=None, m=None, **kwargs):
        """Show figure.

        :param fig:    Figure to show.
        :type fig:     matplotlib.figure.Figure
        :param m:      Map to show.
        :type m:       folium.Map
        :param kwargs: Keyword arguments for :func:`matplotlib.pyplot.show`.
        :type kwargs:  dict, optional
        :return:       None.
        :rtype:        None

        See also: `matplotlib.pyplot.show() <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html>`_
        """
        # Determine if plot is interactive
        fig = m if fig is None else fig
        if isinstance(fig, plt.Figure):
            interactive = False
        elif isinstance(fig, folium.Map):
            interactive = True
        else:
            raise TypeError('fig must be a matplotlib.figure.Figure or folium.Map. Received: {}'.format(type(fig)))

        # Show figure
        if not interactive:
            fig.tight_layout()
            plt.show(**kwargs)
        else:
            if 'draw' in kwargs.keys() and kwargs['draw']:
                rpc.interactive.Draw(export=True, filename="draw.geojson").add_to(m)
            folium.LayerControl().add_to(m)
            display(m)

    # Save figure
    def save(self, fig=None, m=None, file_path=None, **kwargs):
        """Save figure.

        :param file_path:   File path to save figure.
        :type file_path:    str
        :param fig:         Figure to save.
        :type fig:          matplotlib.figure.Figure or folium.Map
        :param dpi:         Dots per inch.
        :type dpi:          int, optional
        :param bbox_inches: Bounding box in inches.
        :type bbox_inches:  str, optional
        :param kwargs:      Keyword arguments for :func:`matplotlib.figure.Figure.savefig`.
        :type kwargs:       dict, optional
        :return:            None.
        :rtype:             None

        See also: `matplotlib.figure.Figure.savefig() <https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure.savefig>`_
        """
        # Determine if plot is interactive
        fig = m if fig is None else fig
        if isinstance(fig, plt.Figure):
            interactive = False
        elif isinstance(fig, folium.Map):
            interactive = True
        else:
            raise TypeError('fig must be a matplotlib.figure.Figure or folium.Map. Received: {}'.format(type(fig)))
        
        # Determine if file path is set
        if file_path is None:
            raise ValueError('file_path must be set. Received: {}'.format(file_path))
        
        # Save figure
        if not interactive:
            kwargs.setdefault('dpi', 300)
            kwargs.setdefault('bbox_inches', 'tight')
            fig.savefig(file_path, **kwargs)
        else:
            fig.save(file_path, **kwargs)

    # Create video
    def create_video(self, file_paths, file_path_video, fps=5, **kwargs):
        """Create video from images.

        :param file_paths:      File paths to images.
        :type file_paths:       list[str]
        :param file_path_video: File path to video.
        :type file_path_video:  str
        :param fps:             Frames per second.
        :type fps:              int, optional
        :param kwargs:          Keyword arguments for :func:`resilientplotterclass.video.create_video`.
        :type kwargs:           dict, optional
        :return:                None.
        """

        # Create video
        rpc.videos.create_video(file_paths, file_path_video, fps=fps, **kwargs)
    
    # Plot custom colormaps
    def plot_colormaps(self):
        """Plot custom colormaps.

        :return: None.
        :rtype:  None
        """

        # Plot custom colormaps
        rpc.colormaps.plot_colormaps()

    # =============================================================================
    # Plot methods
    # =============================================================================    
    def pcolormesh(self, data, ax=None, m=None, data_style=None, extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot data using pcolormesh.

        :param data:         Data to plot.
        :type data:          xarray.DataArray or xugrid.UgridDataArray, optional
        :param ax:           Axis.
        :type ax:            matplotlib.axes.Axes, optional
        :param m:            Map.
        :type m:             folium.Map, optional
        :param data_style:   Data type from guidelines.
        :type data_style:    str, optional
        :param extent_style: Extent type from guidelines.
        :type extent_style:  str, optional
        :param interactive:  Interactive plot.
        :type interactive:   bool, optional
        :param show_kwargs:  Show keyword arguments.
        :type show_kwargs:   bool, optional
        :param kwargs:       Keyword arguments for :func:`resilientplotterclass.data_xarray.pcolormesh` or :func:`resilientplotterclass.data_xugrid.pcolormesh`.
        :type kwargs:        dict, optional
        :return:             Plot.
        :rtype:              matplotlib.collections.QuadMesh or geoviews.element.chart.Image
        """

        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False
        
        # Get keyword arguments
        kwargs = self._get_kwargs(data_style=data_style, extent_style=extent_style, interactive=interactive, show_kwargs=show_kwargs, **kwargs)

        # Plot data
        if isinstance(data, xr.DataArray) and not interactive:
            p = rpc.data_xarray.pcolormesh(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataArray) and not interactive:
            p = rpc.data_xugrid.pcolormesh(data, ax=ax, **kwargs)
        elif isinstance(data, xr.DataArray) and interactive:
            p = rpc.interactive.pcolormesh(data, m=m, **kwargs)
        elif isinstance(data, xu.UgridDataArray) and interactive:
            raise TypeError('Interactive pcolormesh not supported for xugrid.UgridDataArray.')
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p
        
    # Plot data using imshow
    def imshow(self, data, ax=None, m=None, data_style=None, extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot data using imshow.

        :param data:         Data to plot.
        :type data:          xarray.DataArray or xugrid.UgridDataArray, optional
        :param ax:           Axis.
        :type ax:            matplotlib.axes.Axes, optional
        :param m:            Map.
        :type m:             folium.Map, optional
        :param data_style:   Data type from guidelines.
        :type data_style:    str, optional
        :param extent_style: Extent type from guidelines.
        :type extent_style:  str, optional
        :param interactive:  Interactive plot.
        :type interactive:   bool, optional
        :param show_kwargs:  Show keyword arguments.
        :type show_kwargs:   bool, optional
        :param kwargs:       Keyword arguments for :func:`resilientplotterclass.data_xarray.imshow` or :func:`resilientplotterclass.data_xugrid.imshow`.
        :type kwargs:        dict, optional
        :return:             Plot.
        :rtype:              matplotlib.collections.QuadMesh or geoviews.element.chart.Image 
        """
        
        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False
        
        # Get keyword arguments
        kwargs = self._get_kwargs(data_style=data_style, extent_style=extent_style, interactive=interactive, show_kwargs=show_kwargs, **kwargs)

        # Plot data
        if isinstance(data, xr.DataArray) and not interactive:
            p = rpc.data_xarray.imshow(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataArray) and not interactive:
            p = rpc.data_xugrid.imshow(data, ax=ax, **kwargs)
        elif isinstance(data, xr.DataArray) and interactive:
            p = rpc.interactive.imshow(data, m=m, **kwargs)
        elif isinstance(data, xu.UgridDataArray) and interactive:
            raise TypeError('Interactive imshow not supported for xugrid.UgridDataArray.')
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p
    
    # Plot data using scatter
    def scatter(self, data, ax=None, m=None, data_style=None, extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot data using scatter.

        :param data:         Data to plot.
        :type data:          xarray.DataArray or xarray.Dataset or xugrid.UgridDataArray, optional
        :param ax:           Axis.
        :type ax:            matplotlib.axes.Axes, optional
        :param m:            Map.
        :type m:             folium.Map, optional
        :param data_style:   Data type from guidelines.
        :type data_style:    str, optional
        :param extent_style: Extent type from guidelines.
        :type extent_style:  str, optional
        :param interactive:  Interactive plot.
        :type interactive:   bool, optional
        :param show_kwargs:  Show keyword arguments.
        :type show_kwargs:   bool, optional
        :param kwargs:       Keyword arguments for :func:`resilientplotterclass.data_xarray.scatter` or :func:`resilientplotterclass.data_xugrid.scatter`.
        :type kwargs:        dict, optional
        :return:             Plot.
        :rtype:              matplotlib.collections.QuadMesh
        """

        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False

        # Get keyword arguments
        kwargs = self._get_kwargs(data_style=data_style, extent_style=extent_style, interactive=interactive, show_kwargs=show_kwargs, **kwargs)

        # Plot data
        if (isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset)) and not interactive:
            p = rpc.data_xarray.scatter(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataArray) and not interactive:
            p = rpc.data_xugrid.scatter(data, ax=ax, **kwargs)
        elif isinstance(data, xr.DataArray) and interactive:
            p = rpc.interactive.scatter(data, m=m, **kwargs)
        elif isinstance(data, xu.UgridDataArray) and interactive:
            raise TypeError('Interactive scatter not supported for xugrid.UgridDataArray.')
        else: 
            raise TypeError('data type not supported. Please provide a xarray.DataArray, xarray.Dataset or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p
    
    # Plot data using contourf
    def contourf(self, data, ax=None, m=None, data_style=None, extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot data using contourf.

        :param data:         Data to plot.
        :type data:          xarray.DataArray or xugrid.UgridDataArray, optional
        :param ax:           Axis.
        :type ax:            matplotlib.axes.Axes,
        :param m:            Map.
        :type m:             folium.Map, optional
        :param data_style:   Data type from guidelines.
        :type data_style:    str, optional
        :param extent_style: Extent type from guidelines.
        :type extent_style:  str, optional
        :param interactive:  Interactive plot.
        :type interactive:   bool, optional
        :param show_kwargs:  Show keyword arguments.
        :type show_kwargs:   bool, optional
        :param kwargs:       Keyword arguments for :func:`resilientplotterclass.data_xarray.contourf` or :func:`resilientplotterclass.data_xugrid.contourf`.
        :type kwargs:        dict, optional
        :return:             Plot.
        :rtype:              matplotlib.collections.QuadMesh
        """

        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False
        
        # Get keyword arguments
        kwargs = self._get_kwargs(data_style=data_style, extent_style=extent_style, interactive=interactive, show_kwargs=show_kwargs, **kwargs)

        # Plot data
        if isinstance(data, xr.DataArray) and not interactive:
            p = rpc.data_xarray.contourf(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataArray) and not interactive:
            p = rpc.data_xugrid.contourf(data, ax=ax, **kwargs)
        elif isinstance(data, xr.DataArray) and interactive:
            p = rpc.interactive.contourf(data, m=m, **kwargs)
        elif isinstance(data, xu.UgridDataArray) and interactive:
            raise TypeError('Interactive contourf not supported for xugrid.UgridDataArray.')
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p
    
    # Plot data using contour
    def contour(self, data, ax=None, m=None, data_style=None, extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot data using contour.

        :param data:         Data to plot.
        :type data:          xarray.DataArray or xugrid.UgridDataArray, optional
        :param ax:           Axis.
        :type ax:            matplotlib.axes.Axes or folium.Map, optional
        :param m:            Map.
        :type m:             folium.Map, optional
        :param data_style:   Data type from guidelines.
        :type data_style:    str, optional
        :param extent_style: Extent type from guidelines.
        :type extent_style:  str, optional
        :param interactive:  Interactive plot.
        :type interactive:   bool, optional
        :param show_kwargs:  Show keyword arguments.
        :type show_kwargs:   bool, optional
        :param kwargs:       Keyword arguments for :func:`resilientplotterclass.data_xarray.contour` or :func:`resilientplotterclass.data_xugrid.contour`.
        :type kwargs:        dict, optional
        :return:             Plot.
        :rtype:              matplotlib.collections.QuadMesh
        """

        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False

        # Get keyword arguments
        kwargs = self._get_kwargs(data_style=data_style, extent_style=extent_style, interactive=interactive, show_kwargs=show_kwargs, **kwargs)

        # Plot data
        if isinstance(data, xr.DataArray) and not interactive:
            p = rpc.data_xarray.contour(data, ax=ax, **kwargs)
        elif (isinstance(data, xu.UgridDataArray) or isinstance(data, xu.UgridDataset)) and not interactive:
            p = rpc.data_xugrid.contour(data, ax=ax, **kwargs)
        elif isinstance(data, xr.DataArray) and interactive:
            p = rpc.interactive.contour(data, m=m, **kwargs)
        elif isinstance(data, xu.UgridDataArray) and interactive:
            raise TypeError('Interactive contour not supported for xugrid.UgridDataArray.')
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p

    # Plot data using quiver
    def quiver(self, data, ax=None, m=None, data_style=None, extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot data using quiver.

        :param data:         Data to plot.
        :type data:          xarray.Dataset or xugrid.UgridDataArray or xugrid.UgridDataset, optional
        :param ax:           Axis.
        :type ax:            matplotlib.axes.Axes, optional
        :param m:            Map.
        :type m:             folium.Map, optional
        :param data_style:   Data type from guidelines.
        :type data_style:    str, optional
        :param extent_style: Extent type from guidelines.
        :type extent_style:  str, optional
        :param interactive:  Interactive plot.
        :type interactive:   bool, optional
        :param show_kwargs:  Show keyword arguments.
        :type show_kwargs:   bool, optional
        :param kwargs:       Keyword arguments for :func:`resilientplotterclass.data_xarray.quiver` or :func:`resilientplotterclass.data_xugrid.quiver`.
        :type kwargs:        dict, optional
        :return:             Plot.
        :rtype:              matplotlib.collections.QuadMesh
        """

        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False

        # Get keyword arguments
        kwargs = self._get_kwargs(data_style=data_style, extent_style=extent_style, interactive=interactive, show_kwargs=show_kwargs, **kwargs)

        # Plot data
        if isinstance(data, xr.Dataset) and not interactive:
            p = rpc.data_xarray.quiver(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataset) and not interactive:
            p = rpc.data_xugrid.quiver(data, ax=ax, **kwargs)
        elif isinstance(data, xr.Dataset) and interactive:
            p = rpc.interactive.quiver(data, m=m, **kwargs)
        elif isinstance(data, xu.UgridDataset) and interactive:
            raise TypeError('Interactive quiver not supported for xugrid.UgridDataset.')
        else:
            raise TypeError('data type not supported. Please provide a xarray.Dataset or xugrid.UgridDataset. Received: {}'.format(type(data)))
        
        # Return plot
        return p

    # Plot data using streamplot
    def streamplot(self, da, ax=None, m=None, data_style=None, extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot data using streamplot.

        :param da:           Data to plot.
        :type da:            xarray.Dataset, optional
        :param ax:           Axis.
        :type ax:            matplotlib.axes.Axes, optional
        :param m:            Map.
        :type m:             folium.Map, optional
        :param data_style:   Data type from guidelines.
        :type data_style:    str, optional
        :param extent_style: Extent type from guidelines.
        :type extent_style:  str, optional
        :param interactive:  Interactive plot.
        :type interactive:   bool, optional
        :param show_kwargs:  Show keyword arguments.
        :type show_kwargs:   bool, optional
        :param kwargs:       Keyword arguments for :func:`resilientplotterclass.data_xarray.streamplot`.
        :type kwargs:        dict, optional
        :return:             Plot.
        :rtype:              matplotlib.collections.QuadMesh
        """
        
        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False

        # Get keyword arguments
        kwargs = self._get_kwargs(data_style=data_style, extent_style=extent_style, interactive=interactive, show_kwargs=show_kwargs, **kwargs)

        # Plot data
        if isinstance(da, xr.Dataset) and not interactive:
            p = rpc.data_xarray.streamplot(da, ax=ax, **kwargs)
        elif isinstance(da, xr.Dataset) and interactive:
            p = rpc.interactive.streamplot(da, m=m, **kwargs)
        else:
            raise TypeError('data type not supported. Please provide a xarray.Dataset. Received: {}'.format(type(da)))

        # Return plot
        return p

    # Plot grid using xugrid
    def grid(self, data, ax=None, m=None, geom_style='grid', extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot grid using xugrid.

        :param data:           Data to plot.
        :type data:            xarray.DataArray or xugrid.UgridDataArray, optional
        :param ax:             Axis.
        :type ax:              matplotlib.axes.Axes, optional
        :param m:              Map.
        :type m:               folium.Map, optional
        :param geom_style:     Geometry type from guidelines.
        :type geom_style:      str, optional
        :param extent_style:   Extent type from guidelines.
        :type extent_style:    str, optional
        :param interactive:    Interactive plot.
        :type interactive:     bool, optional
        :param show_kwargs:    Show keyword arguments.
        :type show_kwargs:     bool, optional
        :param kwargs:         Keyword arguments for :func:`resilientplotterclass.data_xarray.grid` or :func:`resilientplotterclass.data_xugrid.grid`.
        :type kwargs:          dict, optional
        :return:               Axis.
        :rtype:                matplotlib.axes.Axes
        """

        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False

        # Get keyword arguments
        kwargs = self._get_kwargs(geom_style=geom_style, extent_style=extent_style, show_kwargs=show_kwargs, **kwargs)

        # Plot grid
        if (isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset)) and not interactive:
            ax = rpc.data_xarray.grid(data, ax=ax, **kwargs)
        elif (isinstance(data, xu.UgridDataArray) or isinstance(data, xu.UgridDataset)) and not interactive:
            ax = rpc.data_xugrid.grid(data, ax=ax, **kwargs)
        elif (isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset)) and interactive:
            raise TypeError('Interactive grid not supported for xarray.DataArray or xarray.Dataset.')
        elif (isinstance(data, xu.UgridDataArray) or isinstance(data, xu.UgridDataset)) and interactive:
            raise TypeError('Interactive grid not supported for xugrid.UgridDataArray or xugrid.UgridDataset.')
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray, xarray.Dataset, xugrid.UgridDataArray or xugrid.UgridDataset. Received: {}'.format(type(data)))

        # Return axis
        return ax
    
    # Plot geometries using geopandas
    def geometries(self, gdf, ax=None, m=None, geom_style=None, extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot geometries using geopandas.

        :param gdf:            geometries to plot.
        :type gdf:             geopandas.GeoDataFrame
        :param ax:             Axis.
        :type ax:              matplotlib.axes.Axes or folium.Map, optional
        :param m:              Map.
        :type m:               folium.Map, optional
        :param geom_style:     Geometry type from guidelines.
        :type geom_style:      str, optional
        :param extent_style:   Extent type from guidelines.
        :type extent_style:    str, optional
        :param interactive:    Interactive plot.
        :type interactive:     bool, optional
        :param show_kwargs:    Show keyword arguments.
        :type show_kwargs:     bool, optional
        :param kwargs:         Keyword arguments for :func:`resilientplotterclass.geometries.plot_geometries`.
        :type kwargs:          dict, optional
        :return:               Axis.
        :rtype:                matplotlib.axes.Axes or geoviews.element.chart.Polygons
        """

        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False
            
        # Get keyword arguments
        kwargs = self._get_kwargs(geom_style=geom_style, extent_style=extent_style, interactive=interactive, show_kwargs=show_kwargs, **kwargs)
        
        # Plot geometries
        if isinstance(gdf, gpd.GeoDataFrame) and not interactive:
            ax = rpc.geometries.plot_geometries(gdf, ax=ax, **kwargs)
        elif isinstance(gdf, gpd.GeoDataFrame) and interactive:
            ax = rpc.interactive.plot_geometries(gdf, m=m, **kwargs)
        else:
            raise TypeError('gdf must be a geopandas.GeoDataFrame. Received: {}'.format(type(gdf)))

        # Return axis
        return ax
    
    # Plot basemap using contextily
    def basemap(self, crs=None, ax=None, m=None, map_style=None, extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot basemap using contextily.

        :param crs:          Coordinate reference system.
        :type crs:           pyproj.CRS or rasterio.CRS or str, optional
        :param ax:           Axis.
        :type ax:            matplotlib.axes.Axes or folium.Map, optional
        :param m:            Map.
        :type m:             folium.Map, optional
        :param map_style:    Map type from guidelines.
        :type map_style:     str, optional
        :param extent_style: Extent type from guidelines.
        :type extent_style:  str, optional
        :param interactive:  Interactive plot.
        :type interactive:   bool, optional
        :param show_kwargs:  Show keyword arguments.
        :type show_kwargs:   bool, optional
        :param kwargs:       Keyword arguments for :func:`resilientplotterclass.basemaps.plot_basemap`.
        :type kwargs:        dict, optional
        :return:             Axis.
        :rtype:              matplotlib.axes.Axes or holoviews.element.tiles.Tiles
        """

        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False

        # Get keyword arguments
        if crs is None:
            crs = self.guidelines['general']['crs']
        kwargs = self._get_kwargs(map_style=map_style, extent_style=extent_style, interactive=interactive, show_kwargs=show_kwargs, **kwargs)
        
        # Plot basemap
        if (isinstance(crs, pyprojCRS) or isinstance(crs, rasterioCRS) or isinstance(crs, str)) and not interactive:
            ax = rpc.basemaps.plot_basemap(crs=crs, ax=ax, **kwargs)
        elif interactive:
            ax = rpc.interactive.plot_basemap(m=m, **kwargs)
        else:
            raise TypeError('crs must be a pyproj.CRS or rasterio.CRS or str. Received: {}'.format(type(crs)))
        
        # Return axis
        return ax
    
    # Plot cartopy geometries using geopandas
    def cartopy(self, ax=None, m=None, extent_style=None, interactive=None, show_kwargs=False, **kwargs):
        """Plot cartopy geometries using geopandas.

        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes or folium.Map, optional
        :param m:           Map.
        :type m:            folium.Map, optional
        :param extent_style: Extent type from guidelines.
        :type extent_style:  str, optional
        :param interactive: Interactive plot.
        :type interactive:  bool, optional
        :param show_kwargs: Show keyword arguments.
        :type show_kwargs:  bool, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.geometries.plot_geometries`.
        :type kwargs:       dict, optional
        :return:            Axis.
        :rtype:             matplotlib.axes.Axes
        """

        # Determine if plot is interactive
        if isinstance(ax, plt.Axes):
            interactive = False
        elif isinstance(m, folium.Map):
            interactive = True
        elif interactive is None:
            interactive = False

        # Get keyword arguments
        kwargs = self._get_kwargs(extent_style=extent_style, show_kwargs=show_kwargs, **kwargs)
        
        # Plot cartopy geometries
        if not interactive:
            ax = rpc.geometries.plot_geometries(self.get_cartopy(), ax=ax, **kwargs)
        else:
            raise TypeError('Interactive cartopy not supported.')

        # Return axis
        return ax
    
    # =============================================================================
    # Utility methods
    # =============================================================================
    # Reproject data
    def reproject(self, data, crs, **kwargs):
        """Reproject data.

        :param data:   Data to reproject.
        :type data:    xarray.DataArray or xarray.Dataset or xugrid.UgridDataArray or xugrid.UgridDataset or geopandas.GeoDataFrame
        :param crs:    Coordinate reference system.
        :type crs:     pyproj.CRS or rasterio.CRS or str
        :param kwargs: Keyword arguments for :func:`rioxarray.reproject`, :func:`resilientplotterclass.utils.reproject_xugrid` or :func:`geopandas.GeoDataFrame.to_crs`.
        :type kwargs:  dict, optional
        :return:       Reprojected data.
        :rtype:        xarray.DataArray or xarray.Dataset or xugrid.UgridDataArray or xugrid.UgridDataset or geopandas.GeoDataFrame

        See also: `rioxarray.reproject <https://corteva.github.io/rioxarray/html/rioxarray.html#rioxarray.raster_array.RasterArray.reproject>`_,
                  `geopandas.GeoDataFrame.to_crs <https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html>`_.
        """

        # Reproject data
        if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset):
            data = data.rio.reproject(crs, **kwargs)
        elif isinstance(data, xu.UgridDataArray) or isinstance(data, xu.UgridDataset):
            data = rpc.utils.reproject_xugrid(data, crs, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            data = data.to_crs(crs, **kwargs)
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray, xarray.Dataset, xugrid.UgridDataArray, xugrid.UgridDataset or geopandas.GeoDataFrame. Received: {}'.format(type(data)))
        
        # Return reprojected data
        return data
    
    # Structured data to unstructured data
    def to_unstructured(self, data, **kwargs):
        """Structured data to unstructured data.

        :param data:   Data to convert.
        :type data:    xarray.DataArray or xarray.Dataset
        :param kwargs: Keyword arguments for :func:`resilientplotterclass.utils.to_unstructured`.
        :type kwargs:  dict, optional
        :return:       Unstructured data.
        :rtype:        xugrid.UgridDataArray or xugrid.UgridDataset
        """

        # Convert structured data to unstructured data
        if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset):
            crs = data.rio.crs
            data = xu.UgridDataArray.from_structured(data, **kwargs)
            data.grid.crs = crs
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray or xarray.Dataset. Received: {}'.format(type(data)))
        
        # Return unstructured data
        return data
    
    # Unstructured data to structured data
    def to_structured(self, data, data_blueprint=None, bounds=None, resolution=None):
        """Unstructured data to structured data.

        :param data:           Data to convert.
        :type data:            xugrid.UgridDataArray or xugrid.UgridDataset
        :param data_blueprint: Data blueprint.
        :type data_blueprint:  xarray.DataArray or xarray.Dataset, optional
        :param bounds:         Bounds of the rasterised data.
        :type bounds:          tuple, optional
        :param resolution:     Resolution of the rasterised data.
        :type resolution:      float, optional
        :param kwargs:         Keyword arguments for :func:`resilientplotterclass.utils.rasterise_uda` or :func:`resilientplotterclass.utils.rasterise_uds`.
        :type kwargs:          dict, optional
        :return:               Structured data.
        :rtype:                xarray.DataArray or xarray.Dataset
        """

        # Convert unstructured data to structured data
        if isinstance(data, xu.UgridDataArray) or isinstance(data, xu.UgridDataset):
            data = rpc.utils.rasterise_uds(data, data_blueprint, bounds=bounds, resolution=resolution)
        else:
            raise TypeError('data type not supported. Please provide a xugrid.UgridDataArray or xugrid.UgridDataset. Received: {}'.format(type(data)))
        
        # Return structured data
        return data