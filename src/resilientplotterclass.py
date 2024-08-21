# Packages
import inspect
import json
import os
import matplotlib.pyplot as plt
import xarray as xr
import xugrid as xu
import sys

# Local packages
sys.path.append(os.path.join(os.path.dirname(__file__)))
from colormaps import register_colormaps, plot_colormaps
from geometries import get_gdf_cartopy
from plot_structured_data import pcolormesh_DataArray
from plot_unstructured_data import pcolormesh_UgridDataArray, grid_UgridDataArray
from plot_geometries import plot_geometries
from plot_basemaps import add_basemap

# Resilient Plotter Class
class resilientplotterclass:
    # =============================================================================
    # Constructor
    # =============================================================================
    def __init__(self, project_guidelines=None, cartopy=True):
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
        register_colormaps()
        import colorcet as cc    # See also: https://colorcet.holoviz.org/
        import cmocean.cm as cmo # See also: https://matplotlib.org/cmocean/
        # TODO: Add more colormaps

    # =============================================================================
    # Support methods
    # =============================================================================
    # Combine dictionaries recursively
    def combine_dictionaries(self, dict1, dict2):
        """Recursively combine dictionaries, prioritising dictionary 2.

        :param dict1: Dictionary 1.
        :type dict1:  dict
        :param dict2: Dictionary 2.
        :type dict2:  dict
        :return:      Combined dictionary.
        :rtype:       dict
        """

        # Both dictionaries are not dictionaries --> return dictionary 2
        if type(dict1) != dict and type(dict2) != dict:
            return dict2
        
        # Dictionary 1 is not a dictionary --> return dictionary 2
        elif type(dict1) != dict:
            return dict2
        
        # Dictionary 2 is not a dictionary --> return dictionary 1
        elif type(dict2) != dict:
            return dict1
        
        # Both dictionaries are dictionaries --> combine dictionaries
        keys = set(list(dict1.keys()) + list(dict2.keys()))
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
                dict3[key] = self.combine_dictionaries(dict1[key], dict2[key])
        
        # Return combined dictionary
        return dict3
    
    # Set guidelines
    def set_guidelines(self, project_guidelines=None):
        """Set guidelines.

        :param project_guidelines: File path to the project guidelines file or dictionary with project guidelines.
        :type project_guidelines:  str or dict, optional
        :return:                   None.
        :rtype:                    None
        """

        # Read default guidelines
        with open(os.path.join(os.path.dirname(__file__), 'default_guidelines.json')) as f:
            default_guidelines = json.load(f)

        # Read project guidelines
        if project_guidelines is None:
            project_guidelines = {}
        elif type(project_guidelines) == str:
            with open(project_guidelines) as f:
                project_guidelines = json.load(f)
        elif type(project_guidelines) == dict:
            project_guidelines = project_guidelines
        else:
            raise ValueError('Project guidelines must be a file path (str) or a dictionary (dict).')
        
        # Combine guidelines, prioritising project guidelines
        guidelines = self.combine_dictionaries(default_guidelines, project_guidelines)

        # Set guidelines
        self.guidelines = guidelines
    
    # Get guidelines
    def get_guidelines(self):
        """Get guidelines.

        :return: Guidelines.
        :rtype:  dict
        """

        # Return guidelines
        return self.guidelines
    
    # Get guideline options
    def get_guideline_options(self):
        """Get guideline options per guideline type.

        :return: Guideline options per guideline type.
        :rtype:  dict
        """
        
        # Return guideline options
        return {key: list(value.keys()) for key, value in self.guidelines.items()}
    
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
        self.gdf_cartopy = get_gdf_cartopy(features=features, bounds=bounds, crs=crs)

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
        plot_colormaps()
    
    # =============================================================================
    # General plot methods
    # =============================================================================
    # Plot DataArray or UgridDataArray using pcolormesh
    def pcolormesh(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        """Plot data using pcolormesh.

        :param da:          DataArray or UgridDataArray to plot.
        :type da:           xarray.DataArray or xugrid.UgridDataArray, optional
        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param data_type:   Data type from guidelines.
        :type data_type:    str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.pcolormeshDataArray` or :func:`resilientplotterclass.pcolormeshUgridDataArray`.
        :type kwargs:       dict, optional
        :return:            Plot.
        :rtype:             matplotlib.collections.QuadMesh
        """
        
        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if data_type is not None:
            kwargs = self.combine_dictionaries(self.guidelines['data_type'][data_type][plot_type], kwargs)
        if extent_type is not None:
            kwargs = self.combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)

        # Plot data
        if type(da) == xr.DataArray or type(da) == xr.Dataset:
            p = pcolormesh_DataArray(da, ax=ax, **kwargs)
        elif type(da) == xu.UgridDataArray or type(da) == xu.UgridDataset:
            p = pcolormesh_UgridDataArray(da, ax=ax, **kwargs)
        return p
        
    # Plot DataArray or UgridDataArray using imshow
    def imshow(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        pass

    # Plot DataArray or UgridDataArray using contour
    def contour(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        pass

    # Plot data using contourf
    def contourf(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        pass

    # Plot data using quiver
    def quiver(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        pass

    # Plot data using streamplot
    def streamplot(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        pass

    # Plot grid using xugrid
    def grid(self, uda, ax=None, geometry_type='grid', extent_type=None, **kwargs):
        """" Plot grid using xugrid.

        :param uda:          UgridDataArray to plot.
        :type uda:           xugrid.UgridDataArray
        :param ax:           Axis.
        :type ax:            matplotlib.axes.Axes, optional
        :param geometry_type: Geometry type from guidelines.
        :type geometry_type:  str, optional
        :param extent_type:   Extent type from guidelines.
        :type extent_type:    str, optional
        :param kwargs:        Keyword arguments for :func:`resilientplotterclass.grid_UgridDataArray`.
        :type kwargs:         dict, optional
        :return:              Axis.
        :rtype:               matplotlib.axes.Axes
        """

        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if geometry_type is not None:
            kwargs = self.combine_dictionaries(self.guidelines['geometry_type'][geometry_type], kwargs)
        if extent_type is not None:
            kwargs = self.combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)
        
        # Plot grid
        ax = grid_UgridDataArray(uda, ax=ax, **kwargs)

        # Return axis
        return ax
    
    # Plot geometries using geopandas
    def geometries(self, gdf, ax=None, geometry_type=None, extent_type=None, **kwargs):
        """Plot geometries using geopandas.

        :param gdf:           GeoDataFrame to plot.
        :type gdf:            geopandas.GeoDataFrame
        :param ax:            Axis.
        :type ax:             matplotlib.axes.Axes, optional
        :param geometry_type: Geometry type from guidelines.
        :type geometry_type:  str, optional
        :param extent_type:   Extent type from guidelines.
        :type extent_type:    str, optional
        :param kwargs:        Keyword arguments for :func:`resilientplotterclass.plot_geometries`.
        :type kwargs:         dict, optional
        :return:              Axis.
        :rtype:               matplotlib.axes.Axes
        """
        
        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if geometry_type is not None:
            kwargs = self.combine_dictionaries(self.guidelines['geometry_type'][geometry_type], kwargs)
        if extent_type is not None:
            kwargs = self.combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)
        
        # Plot geometries
        ax = plot_geometries(gdf, ax=ax, **kwargs)

        # Return axis
        return ax

    # Plot cartopy geometries using geopandas
    def cartopy(self, ax=None, extent_type=None, **kwargs):
        """Plot cartopy geometries using geopandas.

        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.plot_geometries`.
        :type kwargs:       dict, optional
        :return:            Axis.
        :rtype:             matplotlib.axes.Axes
        """
        
        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        if extent_type is not None:
            kwargs = self.combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)
        
        # Plot cartopy geometries
        ax = plot_geometries(self.gdf_cartopy, ax=ax, **kwargs)

        # Return axis
        return ax

    # Plot basemap using contextily
    def basemap(self, ax=None, map_type=None, extent_type=None, **kwargs):
        """Plot basemap using contextily.

        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param map_type:    Map type from guidelines.
        :type map_type:     str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :param kwargs:      Keyword arguments for :func:`resilientplotterclass.add_basemap
        :type kwargs:       dict, optional
        :return:            None.
        :rtype:             None
        """
        
        # Combine guidelines and user keyword arguments, prioritising user keyword arguments
        kwargs.setdefault('xy_unit', self.guidelines['general']['xy_unit'])
        kwargs.setdefault('crs', self.guidelines['general']['crs'])
        if map_type is not None:
            kwargs = self.combine_dictionaries(self.guidelines['map_type'][map_type], kwargs)
        if extent_type is not None:
            kwargs = self.combine_dictionaries(self.guidelines['extent_type'][extent_type], kwargs)
        
        # Plot basemap
        add_basemap(ax=ax, **kwargs)
    
    # =============================================================================
    # Specialised plot methods
    # =============================================================================
    # Plot specialised data
    def specialised(self, da=None, gdf=None, ax=None, data_type=None, geometry_type=None, map_type=None, extent_type=None):
        """Plot data as a specialised plot.

        :param da:          DataArray or UgridDataArray to plot.
        :type da:           xarray.DataArray or xugrid.UgridDataArray, optional
        :param gdf:         Geodataframe to plot.
        :type gdf:          geopandas.GeoDataFrame, optional
        :param ax:          Axis.
        :type ax:           matplotlib.axes.Axes, optional
        :param data_type:   Data type from guidelines.
        :type data_type:    str, optional
        :param map_type:    Map type from guidelines.
        :type map_type:     str, optional
        :param extent_type: Extent type from guidelines.
        :type extent_type:  str, optional
        :return:            None.
        :rtype:             None
        """

        # Create axis if not provided
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(10, 10))

        # Plot data
        if da is not None:
            self.pcolormesh(da, ax=ax, data_type=data_type, extent_type=extent_type)

        # Plot geometries
        if gdf is not None:
            self.geometries(gdf, ax=ax, geometry_type=geometry_type, extent_type=extent_type)

        # Get coordinate reference system
        if da is not None and type(da) == xr.DataArray:
            crs = da.rio.crs
        elif da is not None and type(da) == xu.UgridDataArray:
            crs = da.crs
        elif gdf is not None:
            crs = gdf.crs           
                
        # Plot basemap
        self.basemap(ax=ax, map_type=map_type, extent_type=extent_type, crs=crs)

        # Add legend
        ax.legend(loc='upper right')

        # Return axis
        return ax
    
    # Plot bathymetry
    def bathymetry(self, da, gdf=None, ax=None, data_type='bathymetry', geometry_type=None, map_type='osm', extent_type=None):
        self.specialised(da=da, gdf=gdf, ax=ax, data_type=data_type, geometry_type=geometry_type, map_type=map_type, extent_type=extent_type)

    # Plot bedforms
    def bedforms(self, da, ax=None, extent_type=None, **kwargs):
        pass

    # Plot morphology
    def morphology(self, da, ax=None, extent_type=None, **kwargs):
        pass

    # Plot flow velocity
    def flow_velocity(self, da, ax=None, extent_type=None, **kwargs):
        pass

    # Plot flow direction
    def flow_direction(self, da, ax=None, extent_type=None, **kwargs):
        pass

    # Plot wave height
    def wave_height(self, da, ax=None, extent_type=None, **kwargs):
        pass

    # Plot wave period
    def wave_period(self, da, ax=None, extent_type=None, **kwargs):
        pass

    # Plot wave direction
    def wave_direction(self, da, ax=None, extent_type=None, **kwargs):
        pass
    
    # Plot sediment concentration
    def sediment_concentration(self, da, ax=None, extent_type=None, **kwargs):
        pass

    # Plot sediment particle size
    def sediment_particle_size(self, da, ax=None, extent_type=None, **kwargs):
        pass

    # Plot sediment transport
    def sediment_transport(self, da, ax=None, extent_type=None, **kwargs):
        pass
    
    # Plot grid
    def grid2(self, da, ax=None, extent_type=None, **kwargs):
        pass

