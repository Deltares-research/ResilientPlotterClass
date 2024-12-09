# Packages
import geopandas as gpd
import holoviews as hv
import inspect
from IPython.display import display
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import pandas as pd
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
    # Support methods
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
    
    # Remove conflicting kwargs from dictionary
    def _remove_dictonary_conflicts(self, dict, warn=True):
        """ Remove conflicting kwargs from dictionary, prioritising the last kwargs.

        :param dict: Dictionary.
        :type dict:  dict
        :param warn: Print warning if conflicting kwargs.
        :type warn:  bool, optional
        :return:     Dictionary without conflicting kwargs.
        :rtype:      dict
        """

        # Define conflicting kwargs
        CONFLICT_DICT = {'color': ['cmap'],
                         'colors': ['cmap'],
                         'cmap': ['color', 'colors']}

        # Remove conflicting kwargs
        dict2 = {}
        for key in list(dict.keys())[::-1]:
            if key not in CONFLICT_DICT.keys():
                dict2[key] = dict[key]
            elif not any([conflict in dict2.keys() for conflict in CONFLICT_DICT[key]]):
                dict2[key] = dict[key]
            elif warn:
                key2 = [key2 for key2 in CONFLICT_DICT[key] if key2 in dict2.keys()][0]
                print("\033[93m Warning: Conflicting kwargs ('{}' and '{}') using '{}'. \033[0m".format(key2, key, key2))
        
        # Return dictionary without conflicting kwargs
        return dict2

    # Get guidelines dataframe
    def _get_df_guidelines(self, guidelines, section):
        """Get guidelines dataframe.	

        :param guidelines: Guidelines.
        :type guidelines:  dict
        :return:           General guidelines dataframe.
        :rtype:            pandas.DataFrame
        """

        # Create dataframe
        df_guidelines = gpd.GeoDataFrame({key: [value] for key, value in guidelines[section].items()}, index=[''])

        # Sort dataframe
        df_guidelines = df_guidelines[list(guidelines[section].keys())]

        # Return dataframe
        return df_guidelines

    # Get argument guidelines dataframe
    def _get_df_argument_guidelines(self, guidelines, default_guidelines, project_guidelines):
        """Get argument guidelines dataframe.

        :param guidelines:       Guidelines.
        :type guidelines:        dict
        :param default_guidelines: Default guidelines.
        :type default_guidelines:  dict
        :param project_guidelines: Project guidelines.
        :type project_guidelines:  dict
        :param guidelines_type:  Guidelines type.
        :type guidelines_type:   str
        :return:                 Argument guidelines dataframe.
        :rtype:                  pandas.DataFrame
        """
        
        # Get guidelines
        def _get_guideline(guidelines, parameter, argument, method):
            if parameter in guidelines.keys() and parameter == 'data_type' and argument in guidelines[parameter].keys() and method in guidelines[parameter][argument].keys():
                guideline = guidelines[parameter][argument][method] # Data type
            elif parameter in guidelines.keys() and parameter == 'geom_type' and argument in guidelines[parameter].keys() and method in ['grid', 'geometries']:
                guideline = guidelines[parameter][argument] # Geom type
            elif parameter in guidelines.keys() and parameter == 'map_type' and argument in guidelines[parameter].keys() and method in ['basemap']:
                guideline = guidelines[parameter][argument] # Map type
            elif parameter in guidelines.keys() and parameter == 'extent_type' and argument in guidelines[parameter].keys():
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
        for parameter in ['data_type', 'geom_type', 'map_type', 'extent_type']:
            if parameter not in guidelines.keys():
                continue
            for argument in guidelines[parameter]:
                parameters.append(parameter)
                arguments.append(argument)
                for method in methods.keys():
                    methods[method].append(_compare_guidelines(guidelines, default_guidelines, project_guidelines, parameter, argument, method))

        # Create dataframe
        df_guidelines = pd.DataFrame({'parameter': parameters, 'argument': arguments, **methods})

        # Set multi-index
        df_guidelines = df_guidelines.set_index(['parameter', 'argument'])

        # Reindex argument guidelines dataframe
        df_guidelines = df_guidelines.reindex(['data_type', 'geom_type', 'map_type', 'extent_type'], level=0)

        # Return dataframe
        return df_guidelines

    # Set guidelines
    def set_guidelines(self, project_guidelines=None):
        """Set guidelines.

        :param project_guidelines: File path to the project guidelines file or dictionary with project guidelines.
        :type project_guidelines:  str or dict, optional
        :return:                   None.
        :rtype:                    None
        """

        # Read default guidelines
        dir_path_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        with open(os.path.join(dir_path_data, 'default_guidelines.json')) as f:
            default_guidelines = json.load(f)
        
        # Read project guidelines
        if project_guidelines is None:
            project_guidelines = {}
        elif isinstance(project_guidelines, dict):
            project_guidelines = project_guidelines
        elif isinstance(project_guidelines, str):
            if os.path.exists(os.path.join(dir_path_data, project_guidelines)) and not os.path.exists(project_guidelines):
                project_guidelines = os.path.join(dir_path_data, project_guidelines)
            with open(project_guidelines) as f:
                project_guidelines = json.load(f)
        else:
            raise ValueError('Project guidelines must be a file path (str) or a dictionary (dict). Received: {}'.format(type(project_guidelines)))

        # Combine guidelines, prioritising project guidelines
        guidelines = self._combine_dictionaries(default_guidelines, project_guidelines)

        # Remove conflicting kwargs from guidelines
        guidelines = self._remove_dictonary_conflicts(guidelines, warn=False)

        # Set guidelines
        self.guidelines = guidelines

        # Set metadata guidelines dataframe
        self._df_metadata_guidelines = self._get_df_guidelines(guidelines, 'metadata')

        # Set general guidelines dataframe
        self._df_general_guidelines = self._get_df_guidelines(guidelines, 'general')

        # Set argument guidelines dataframe
        self._df_argument_guidelines = self._get_df_argument_guidelines(guidelines, default_guidelines, project_guidelines)
    
    # Get guidelines
    def get_guidelines(self):
        """Get guidelines.

        :return: Guidelines.
        :rtype:  dict
        """

        # Return guidelines
        return self.guidelines
    
    # Print guidelines
    def print_guidelines(self):
        """Print guidelines.

        :return: None.
        :rtype:  None
        """

        # Print metadata guidelines dataframe
        s = self._df_metadata_guidelines.style
        s = s.set_properties(**{'text-align': 'center'}).set_caption('Metadata')
        s = s.set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]},
                                {'selector': 'thead', 'props': [('border-bottom', '2px solid black')]},
                                {'selector': 'caption', 'props': [('font-weight', 'bold')]}])
        display(s)

        # Print general guidelines dataframe
        s = self._df_general_guidelines.style
        s = s.set_properties(**{'text-align': 'center'}).set_caption('General')
        s = s.set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]},
                                {'selector': 'thead', 'props': [('border-bottom', '2px solid black')]},
                                {'selector': 'caption', 'props': [('font-weight', 'bold')]}])
        display(s)

        # Print argument guidelines dataframe
        s = self._df_argument_guidelines.style
        for _, df_group in self._df_argument_guidelines.groupby(level=0):
            s = s.set_properties(**{'text-align': 'center'})
            s = s.set_table_styles({df_group.index[0]: [{'selector': '', 'props': 'border-top: 2px solid black'}]}, overwrite=False, axis=1)
        s = s.set_caption('Arguments (D: Default, P: Project, D=P: Default equal to Project, D+P: Default merged with Project)')
        s = s.set_table_styles([{'selector': 'thread', 'props': [('border-top', '2px solid black')]},
                                {'selector': 'caption', 'props': [('font-weight', 'bold')]}], overwrite=False)
        display(s)

    # Set cartopy
    def set_cartopy(self, features=None, bounds=None, crs=None):
        """Set cartopy geometries.

        :param features: List of features to get.
        :type features:  list[str], optional
        :param bounds:   Bounds of the cartopy geometries (``[xmin, ymin, xmax, ymax]``).
        :type bounds:    list[float], optional
        :param crs:      Coordinate reference system of the cartopy geometries.
        :type crs:       str, optional
        :return:         None.
        :rtype:          None
        """
        
        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        features = self.guidelines['general']['cartopy_features'] if features is None else features
        bounds = self.guidelines['general']['bounds'] if bounds is None else bounds
        crs = self.guidelines['general']['crs'] if crs is None else crs

        # Set cartopy geometries
        self.gdf_cartopy = rpc.geometries.get_gdf_cartopy(features=features, bounds=bounds, crs=crs)

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

    # Save figure
    def save_fig(self, fig, file_path, close=True, dpi=300, bbox_inches='tight', **kwargs):
        """Save figure.

        :param file_path:   File path to save figure.
        :type file_path:    str
        :param fig:         Figure to save.
        :type fig:          matplotlib.figure.Figure or holoviews.element.chart.Element or holoviews.element.chart.Overlay or holoviews.element.chart.DynamicMap
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

        # Save figure
        if isinstance(fig, plt.Figure):
            fig.savefig(file_path, dpi=dpi, bbox_inches=bbox_inches, **kwargs)
        elif any(isinstance(fig, getattr(hv, x)) for x in ['Overlay', 'Element', 'DynamicMap']):
            # Remove file extension
            file_path = file_path.rsplit('.', maxsplit=1)[0]
            
            # Save figure
            renderer = hv.renderer('bokeh')
            renderer.save(fig, file_path, fmt='html')
        else:
            raise TypeError('fig must be a matplotlib.figure.Figure or holoviews.element.chart.Element or holoviews.element.chart.Overlay or holoviews.element.chart.DynamicMap. Received: {}'.format(type(fig)))
        
    # Create video
    def create_video(self, file_paths, file_path_video, fps=5, frame_size=(1920, 1080), **kwargs):
        """Create video from images.

        :param file_paths:      File paths to images.
        :type file_paths:       list[str]
        :param file_path_video: File path to video.
        :type file_path_video:  str
        :param fps:             Frames per second.
        :type fps:              int, optional
        :param frame_size:      Frame size.
        :type frame_size:       tuple[int, int], optional
        :param kwargs:          Keyword arguments for :func:`resilientplotterclass.video.create_video`.
        :type kwargs:           dict, optional
        :return:                None.
        """

        # Create video
        rpc.videos.create_video(file_paths, file_path_video, fps=fps, frame_size=frame_size, **kwargs)

    # =============================================================================
    # General plot methods
    # =============================================================================
    # Plot data using pcolormesh
    def pcolormesh(self, data, ax=None, data_type=None, extent_type=None, **kwargs):
        """Plot data using pcolormesh.

        :param data:        Data to plot.
        :type data:         xarray.DataArray or xugrid.UgridDataArray, optional
        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param data_type:   Data type from guidelines.
        :type data_type:    str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.data_xarray.pcolormesh` or :func:`resilientplotterclass.data_xugrid.pcolormesh`.
        :type kwargs:       dict, optional
        :return:            Plot.
        :rtype:             matplotlib.collections.QuadMesh
        """
        
        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Get default types
        if data_type is None:
            data_type = self.guidelines['general']['default_types']['data_type']
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if data_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['data_type'][data_type][plot_type], kwargs)
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)


        # Plot data
        if isinstance(data, xr.DataArray):
            p = rpc.data_xarray.pcolormesh(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataArray):
            p = rpc.data_xugrid.pcolormesh(data, ax=ax, **kwargs)
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p
        
    # Plot data using imshow
    def imshow(self, data, ax=None, data_type=None, extent_type=None, **kwargs):
        """Plot data using imshow.

        :param data:        Data to plot.
        :type data:         xarray.DataArray or xugrid.UgridDataArray, optional
        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param data_type:   Data type from guidelines.
        :type data_type:    str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.data_xarray.imshow` or :func:`resilientplotterclass.data_xugrid.imshow`.
        :type kwargs:       dict, optional
        :return:            Plot.
        :rtype:             matplotlib.collections.QuadMesh
        """

        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Get default types
        if data_type is None:
            data_type = self.guidelines['general']['default_types']['data_type']
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if data_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['data_type'][data_type][plot_type], kwargs)
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)
        
        # Plot data
        if isinstance(data, xr.DataArray):
            p = rpc.data_xarray.imshow(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataArray):
            p = rpc.data_xugrid.imshow(data, ax=ax, **kwargs)
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p
    
    # Plot data using scatter
    def scatter(self, data, ax=None, data_type=None, extent_type=None, **kwargs):
        """Plot data using scatter.

        :param data:        Data to plot.
        :type data:         xarray.DataArray or xarray.Dataset or xugrid.UgridDataArray, optional
        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param data_type:   Data type from guidelines.
        :type data_type:    str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.data_xarray.scatter` or :func:`resilientplotterclass.data_xugrid.scatter`.
        :type kwargs:       dict, optional
        :return:            Plot.
        :rtype:             matplotlib.collections.QuadMesh
        """

        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Get default types
        if data_type is None:
            data_type = self.guidelines['general']['default_types']['data_type']
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if data_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['data_type'][data_type][plot_type], kwargs)
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)

        # Plot data
        if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset):
            p = rpc.data_xarray.scatter(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataArray):
            p = rpc.data_xugrid.scatter(data, ax=ax, **kwargs)
        else: 
            raise TypeError('data type not supported. Please provide a xarray.DataArray, xarray.Dataset or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p
    
    # Plot data using contourf
    def contourf(self, data, ax=None, data_type=None, extent_type=None, **kwargs):
        """Plot data using contourf.

        :param data:        Data to plot.
        :type data:         xarray.DataArray or xugrid.UgridDataArray, optional
        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param data_type:   Data type from guidelines.
        :type data_type:    str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.data_xarray.contourf` or :func:`resilientplotterclass.data_xugrid.contourf`.
        :type kwargs:       dict, optional
        :return:            Plot.
        :rtype:             matplotlib.collections.QuadMesh
        """

        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Get default types
        if data_type is None:
            data_type = self.guidelines['general']['default_types']['data_type']
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if data_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['data_type'][data_type][plot_type], kwargs)
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)

        # Plot data
        if isinstance(data, xr.DataArray):
            p = rpc.data_xarray.contourf(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataArray):
            p = rpc.data_xugrid.contourf(data, ax=ax, **kwargs)
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p
    
    # Plot data using contour
    def contour(self, data, ax=None, data_type=None, extent_type=None, **kwargs):
        """Plot data using contour.

        :param data:        Data to plot.
        :type data:         xarray.DataArray or xugrid.UgridDataArray, optional
        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param data_type:   Data type from guidelines.
        :type data_type:    str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.data_xarray.contour` or :func:`resilientplotterclass.data_xugrid.contour`.
        :type kwargs:       dict, optional
        :return:            Plot.
        :rtype:             matplotlib.collections.QuadMesh
        """

        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Get default types
        if data_type is None:
            data_type = self.guidelines['general']['default_types']['data_type']
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if data_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['data_type'][data_type][plot_type], kwargs)
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)

        # Plot data
        if isinstance(data, xr.DataArray):
            p = rpc.data_xarray.contour(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataArray) or isinstance(data, xu.UgridDataset):
            p = rpc.data_xugrid.contour(data, ax=ax, **kwargs)
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p

    # Plot data using quiver
    def quiver(self, data, ax=None, data_type=None, extent_type=None, **kwargs):
        """Plot data using quiver.

        :param data:        Data to plot.
        :type data:         xarray.Dataset or xugrid.UgridDataArray or xugrid.UgridDataset, optional
        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param data_type:   Data type from guidelines.
        :type data_type:    str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.data_xarray.quiver` or :func:`resilientplotterclass.data_xugrid.quiver`.
        :type kwargs:       dict, optional
        :return:            Plot.
        :rtype:             matplotlib.collections.QuadMesh
        """

        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Get default types
        if data_type is None:
            data_type = self.guidelines['general']['default_types']['data_type']
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if data_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['data_type'][data_type][plot_type], kwargs)
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)
        
        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)

        # Plot data
        if isinstance(data, xr.Dataset):
            p = rpc.data_xarray.quiver(data, ax=ax, **kwargs)
        elif isinstance(data, xu.UgridDataset):
            p = rpc.data_xugrid.quiver(data, ax=ax, **kwargs)
        else:
            raise TypeError('data type not supported. Please provide a xarray.Dataset or xugrid.UgridDataset. Received: {}'.format(type(data)))
        
        # Return plot
        return p

    # Plot data using streamplot
    def streamplot(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        """Plot data using streamplot.

        :param da:          Data to plot.
        :type da:           xarray.Dataset, optional
        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param data_type:   Data type from guidelines.
        :type data_type:    str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.data_xarray.streamplot`.
        :type kwargs:       dict, optional
        :return:            Plot.
        :rtype:             matplotlib.collections.QuadMesh
        """

        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Get default types
        if data_type is None:
            data_type = self.guidelines['general']['default_types']['data_type']
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if data_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['data_type'][data_type][plot_type], kwargs)
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)
        
        # Plot data
        if isinstance(da, xr.Dataset):
            p = rpc.data_xarray.streamplot(da, ax=ax, **kwargs)
        else:
            raise TypeError('data type not supported. Please provide a xarray.Dataset. Received: {}'.format(type(da)))

        # Return plot
        return p

    # Plot grid using xugrid
    def grid(self, data, ax=None, geom_type='grid', extent_type=None, **kwargs):
        """Plot grid using xugrid.

        :param data:          Data to plot.
        :type data:           xugrid.UgridDataArray
        :param ax:            Axis.
        :type ax:             matplotlib.axes.Axes, optional
        :param geom_type:     Geometry type from guidelines.
        :type geom_type:      str, optional
        :param extent_type:   Extent type from guidelines.
        :type extent_type:    str, optional
        :param kwargs:        Keyword arguments for :func:`resilientplotterclass.data_xugrid.grid`.
        :type kwargs:         dict, optional
        :return:              Axis.
        :rtype:               matplotlib.axes.Axes
        """

        # Get default types
        if geom_type is None:
            geom_type = self.guidelines['general']['default_types']['geom_type']
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if geom_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['geom_type'][geom_type], kwargs)
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)
        
        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)
        
        # Plot grid
        if isinstance(data, xu.UgridDataArray) or isinstance(data, xu.UgridDataset):
            ax = rpc.data_xugrid.grid(data, ax=ax, **kwargs)
        else:
            raise TypeError('data type not supported. Please provide a xugrid.UgridDataArray. Received: {}'.format(type(data)))

        # Return axis
        return ax
    
    # Plot geometries using geopandas
    def geometries(self, gdf, ax=None, geom_type=None, extent_type=None, **kwargs):
        """Plot geometries using geopandas.

        :param gdf:           geometries to plot.
        :type gdf:            geopandas.GeoDataFrame
        :param ax:            Axis.
        :type ax:             matplotlib.axes.Axes, optional
        :param geom_type:     Geometry type from guidelines.
        :type geom_type:      str, optional
        :param extent_type:   Extent type from guidelines.
        :type extent_type:    str, optional
        :param kwargs:        Keyword arguments for :func:`resilientplotterclass.geometries.plot_geometries`.
        :type kwargs:         dict, optional
        :return:              Axis.
        :rtype:               matplotlib.axes.Axes
        """
        
        # Get default types
        if geom_type is None:
            geom_type = self.guidelines['general']['default_types']['geom_type']
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if geom_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['geom_type'][geom_type], kwargs)
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)
        
        # Plot geometries
        if isinstance(gdf, gpd.GeoDataFrame):
            ax = rpc.geometries.plot_geometries(gdf, ax=ax, **kwargs)
        else:
            raise TypeError('gdf must be a geopandas.GeoDataFrame. Received: {}'.format(type(gdf)))

        # Return axis
        return ax
    
    # Plot basemap using contextily
    def basemap(self, crs=None, ax=None, map_type=None, extent_type=None, **kwargs):
        """Plot basemap using contextily.

        :param crs:         Coordinate reference system.
        :type crs:          pyproj.CRS or rasterio.CRS or str, optional
        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param map_type:    Map type from guidelines.
        :type map_type:     str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.basemaps.plot_basemap`.
        :type kwargs:       dict, optional
        :return:            None.
        :rtype:             None
        """

        # Get default types
        if crs is None:
            crs = self.guidelines['general']['crs']
        if map_type is None:
            map_type = self.guidelines['general']['default_types']['map_type']
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']
        
        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if map_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['map_type'][map_type], kwargs)
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)
        
        # Plot basemap
        rpc.basemaps.plot_basemap(crs=crs, ax=ax, **kwargs)
    
    # Plot cartopy geometries using geopandas
    def cartopy(self, ax=None, extent_type=None, **kwargs):
        """Plot cartopy geometries using geopandas.

        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.geometries.plot_geometries`.
        :type kwargs:       dict, optional
        :return:            Axis.
        :rtype:             matplotlib.axes.Axes
        """

        # Get default types
        if extent_type is None:
            extent_type = self.guidelines['general']['default_types']['extent_type']
        
        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if extent_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)
        
        # Plot cartopy geometries
        ax = rpc.geometries.plot_geometries(self.get_cartopy(), ax=ax, **kwargs)

        # Return axis
        return ax
    
    def interactive_data(self, data, data_type=None, **kwargs):
        """Plot data interactively.

        :param data:        Data to plot.
        :type data:         xarray.DataArray or xugrid.UgridDataArray, optional
        :param data_type:   Data type from guidelines.
        :type data_type:    str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.interactive.da_interactive` or :func:`resilientplotterclass.interactive.uda_interactive`.
        :type kwargs:       dict, optional
        :return:            Interactive plot.
        :rtype:             holoviews.core.spaces.DynamicMap
        """

        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if data_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['data_type'][data_type][plot_type], kwargs)
        
        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)
        
        # Plot data
        if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset):
            p = rpc.interactive.interactive_da(data, **kwargs)
        elif isinstance(data, xu.UgridDataArray) or isinstance(data, xu.UgridDataset):
            p = rpc.interactive.interactive_uda(data, **kwargs)
        else:
            raise TypeError('data type not supported. Please provide a xarray.DataArray or xugrid.UgridDataArray. Received: {}'.format(type(data)))
        
        # Return plot
        return p
    
    def interactive_geometries(self, gdf, geom_type=None, **kwargs):
        """Plot geometries interactively.

        :param gdf:           Geodataframe to plot.
        :type gdf:            geopandas.GeoDataFrame
        :param ax:            Axis.
        :type ax:             matplotlib.axes.Axes, optional
        :param geom_type:     Geometry type from guidelines.
        :type geom_type:      str, optional
        :param kwargs:        Keyword arguments for :func:`resilientplotterclass.interactive.geometries_interactive`.
        :type kwargs:         dict, optional
        :return:              Interactive plot.
        :rtype:               holoviews.element.path.Polygons
        """

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if geom_type is not None:
            kwargs = self._combine_dictionaries(self.guidelines['geom_type'][geom_type], kwargs)

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)
        
        # Plot geometries interactively
        p = rpc.interactive.interactive_gdf(gdf, **kwargs)

        # Return plot
        return p
    
    def interactive_cartopy(self, **kwargs):
        """Plot cartopy geometries interactively.

        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.interactive.interactive_gdf_cartopy`.
        :type kwargs:       dict, optional
        :return:            Interactive plot.
        :rtype:             holoviews.core.overlay.Overlay
        """

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)
        
        # Plot cartopy geometries interactively 
        p = rpc.interactive.interactive_gdf_cartopy(self.get_cartopy(), **kwargs)

        # Return plot
        return p
    
    def interactive_basemap(self, map_type=None, **kwargs):
        """Plot basemap interactively.

        :return: 
        :rtype:  
        """

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        if map_type is None:
            map_type = self.guidelines['general']['map_type']

        # Remove conflicting kwargs
        kwargs = self._remove_dictonary_conflicts(kwargs)

        # Plot basemap interactively
        p = rpc.interactive.interactive_basemap(map_type=map_type, **kwargs)

        # Return plot
        return p
    
    # =============================================================================
    # Specialised plot methods
    # =============================================================================
    # Plot bathymetry
    def bathymetry(self, da, gdf=None, ax=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        """Plot bathymetry.

        :param da:            DataArray or UgridDataArray to plot.
        :type da:             xarray.DataArray or xugrid.UgridDataArray
        :param gdf:           Geodataframe to plot.
        :type gdf:            geopandas.GeoDataFrame, optional
        :param ax:            Axis.
        :type ax:             matplotlib.axes.Axes, optional
        :param data_type:     Data type from guidelines.
        :type data_type:      str, optional
        :param geom_type:     Geometry type from guidelines.
        :type geom_type:      str, optional
        :param map_type:      Map type from guidelines.
        :type map_type:       str, optional
        :param extent_type:   Extent type from guidelines.
        :type extent_type:    str, optional
        :return:              Figure and axis.
        :rtype:               tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
        """
                
        # Create axis if not provided
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(10, 10))

        # Remove values above 0 (land)
        if isinstance(da, xr.DataArray):
            da = da.where(da < 0)
        elif isinstance(da, xu.UgridDataArray):
            da = da.where(da < 0, drop=True)
        
        # Plot bathymetry
        self.imshow(da, ax=ax, data_type=data_type, extent_type=extent_type)
        self.contour(da, ax=ax, data_type=data_type, extent_type=extent_type)
        
        # Plot geometries
        if gdf is not None:
            self.geometries(gdf, ax=ax, geom_type=geom_type, extent_type=extent_type)
            ax.legend(loc='upper right')

        # Get coordinate reference system
        if isinstance(da, xr.DataArray):
            crs = da.rio.crs
        elif isinstance(da, xu.UgridDataArray):
            crs = da.grid.crs

        # Plot basemap
        self.basemap(crs=crs, ax=ax, map_type=map_type, extent_type=extent_type)

        # Return figure and axis
        return ax

    # Plot topography
    def topography(self, da, gdf=None, ax=None, data_type='topography', geom_type='aoi', map_type='satellite', extent_type=None):
        pass

    # Plot bedforms
    def bedforms(self, da, ax=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        pass

    # Plot morphology
    def morphology(self, da, gdf=None, ax=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        pass

    # Plot flow velocity
    def flow_velocity(self, da, gdf=None, ax=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        pass

    # Plot flow direction
    def flow_direction(self,da, gdf=None, ax=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        pass

    # Plot wave height
    def wave_height(self, da, gdf=None, ax=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        pass

    # Plot wave period
    def wave_period(self, da, gdf=None, ax=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        pass

    # Plot wave direction
    def wave_direction(self, da, gdf=None, ax=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        pass
    
    # Plot sediment transport
    def sediment_transport(self, da, gdf=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        pass
    
    # Plot sediment concentration
    def sediment_concentration(self, da, gdf=None, ax=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        pass

    # Plot sediment particle size
    def sediment_particle_size(self, da, gdf=None, ax=None, data_type='bathymetry', geom_type='aoi', map_type='satellite', extent_type=None):
        pass

    # Plot pretty geometries
    def pretty_geometries(self, gdf, ax=None, geom_type='aoi', map_type='satellite', extent_type=None):
        """Plot pretty geometries.

        :param gdf:           Geodataframe to plot.
        :type gdf:            geopandas.GeoDataFrame
        :param ax:            Axis.
        :type ax:             matplotlib.axes.Axes, optional
        :param geom_type:     Geometry type from guidelines.
        :type geom_type:      str, optional
        :param map_type:      Map type from guidelines.
        :type map_type:       str, optional
        :param extent_type:   Extent type from guidelines.
        :type extent_type:    str, optional
        :return:              Figure and axis.
        :rtype:               tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
        """
            
        # Create axis if not provided
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(10, 10))

        # Plot geometries
        self.geometries(gdf, ax=ax, geom_type=geom_type, extent_type=extent_type)
        ax.legend(loc='upper right')

        # Get coordinate reference system
        crs = gdf.crs

        # Plot basemap
        self.basemap(crs=crs, ax=ax, map_type=map_type, extent_type=extent_type)

        # Return figure and axis
        return ax
    
    # Plot pretty grid
    def pretty_grid(self, da, gdf=None, ax=None, geom_type='aoi', map_type='satellite', extent_type=None):
        """Plot pretty grid.

        :param da:             DataArray or UgridDataArray to plot.
        :type da:              xarray.DataArray or xugrid.UgridDataArray
        :param gdf:            Geodataframe to plot.
        :type gdf:             geopandas.GeoDataFrame, optional
        :param ax:             Axis.
        :type ax:              matplotlib.axes.Axes, optional
        :param geom_type:      Geometry type from guidelines.
        :type geom_type:       str, optional
        :param geom_type2:     Geometry type from guidelines.
        :type geom_type2:      str, optional
        :param map_type:       Map type from guidelines.
        :type map_type:        str, optional
        :param extent_type:    Extent type from guidelines.
        :type extent_type:     str, optional
        :return:               Figure and axis.
        :rtype:                tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
        """

        # Create axis if not provided
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(10, 10))

        # Plot grid
        self.grid(da, ax=ax, extent_type=extent_type)
        
        # Plot geometries
        if gdf is not None:
            self.geometries(gdf, ax=ax, geom_type=geom_type, extent_type=extent_type)
            ax.legend(loc='upper right')

        # Get coordinate reference system
        crs = da.grid.crs

        # Plot basemap
        self.basemap(crs=crs, ax=ax, map_type=map_type, extent_type=extent_type)

        # Return figure and axis
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