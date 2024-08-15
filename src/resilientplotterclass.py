# Packages
import inspect
import json
import os
import xarray as xr
import xugrid as xu

# Resilient Plotter Class
class resilientplotterclass:
    # =============================================================================
    # Constructor
    # =============================================================================
    def __init__(self, file_path_project_guidelines=None):
        """ Constructor for the resilient plotter class.

        :param file_path_guidelines: File path to guidelines.
        :type file_path_guidelines: str
        :return: None
        :rtype: None
        """
        # Set guidelines
        self.set_guidelines(file_path_project_guidelines)

        # Get cartopy geodataframe
        self.set_cartopy()

    # =============================================================================
    # Support methods
    # =============================================================================
    # Set guidelines
    def set_guidelines(self, file_path_project_guidelines=None):
        """ Set guidelines.

        :param file_path_project_guidelines: File path to project guidelines.
        :type file_path_project_guidelines: str
        :return: None
        :rtype: None
        """

        # Read default guidelines
        with open(os.path.join(os.path.dirname(__file__), 'default_guidelines.json')) as f:
            default_guidelines = json.load(f)

        # Read project guidelines
        if file_path_project_guidelines is not None:
            with open(file_path_project_guidelines) as f:
                project_guidelines = json.load(f)
        else:
            project_guidelines = {'general': {}, 'reference_type': {}, 'data_type': {}, 'geometry_type': {}, 'extent_type': {}}

        # Combine guidelines (prioritising project guidelines)
        guidelines = {}
        guidelines['general'] = {**default_guidelines['general'], **project_guidelines['general']}
        guidelines['reference_type'] = {**default_guidelines['reference_type'], **project_guidelines['reference_type']}
        guidelines['data_type'] = {**default_guidelines['data_type'], **project_guidelines['data_type']}
        guidelines['geometry_type'] = {**default_guidelines['geometry_type'], **project_guidelines['geometry_type']}
        guidelines['extent_type'] = {**default_guidelines['extent_type'], **project_guidelines['extent_type']}

        # Set guidelines
        self.guidelines = guidelines
    
    # Get guidelines
    def get_guidelines(self):
        """ Get guidelines.

        :return: Guidelines.
        :rtype: dict
        """
        return self.guidelines
    
    # Set cartopy geodataframe
    def set_cartopy(self, features=None):
        pass

    # Get cartopy geodataframe
    def get_cartopy(self):
        """ Get cartopy geodataframe.

        :return: Cartopy geodataframe.
        :rtype: geopandas.GeoDataFrame
        """
        return self.gdf_cartopy
    
    # =============================================================================
    # General plot methods
    # =============================================================================
    # Plot data using pcolormesh
    def pcolormesh(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        """ Plot data using pcolormesh.

        :param da: Data array.
        :type da: xarray.DataArray or xugrid.UgridDataArray
        :param ax: Axes.
        :type ax: matplotlib.axes.Axes
        :param data_type: Data type.
        :type data_type: str
        :param extent_type: Extent type.
        :type extent_type: str
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        
        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Combine guidelines and user keyword arguments
        if data_type is not None:
            kwargs = {**self.guidelines['data_type'][data_type][plot_type], **kwargs}
        if extent_type is not None:
            kwargs = {**self.guidelines['extent_type'][extent_type], **kwargs}

        # Plot data
        if type(da) == xr.DataArray:
            da.plot.pcolormesh(ax=ax, **kwargs)
        elif type(da) == xu.UgridDataArray:
            da.ugrid.plot.pcolormesh(ax=ax, **kwargs)

    # Plot data using imshow
    def imshow(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        """ Plot data using imshow.

        :param da: Data array.
        :type da: xarray.DataArray or xugrid.UgridDataArray
        :param ax: Axes.
        :type ax: matplotlib.axes.Axes
        :param data_type: Data type.
        :type data_type: str
        :param extent_type: Extent type.
        :type extent_type: str
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        
        # get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Combine guidelines and user keyword arguments
        if data_type is not None:
            kwargs = {**self.guidelines['data_type'][data_type][plot_type], **kwargs}
        if extent_type is not None:
            kwargs = {**self.guidelines['extent_type'][extent_type], **kwargs}
        
        # Plot data
        if type(da) == xr.DataArray:
            da.plot.imshow(ax=ax, **kwargs)
        elif type(da) == xu.UgridDataArray:
            da.ugrid.plot.imshow(ax=ax, **kwargs)

    # Plot data using contour
    def contour(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        """ Plot data using contour.

        :param da: Data array.
        :type da: xarray.DataArray or xugrid.UgridDataArray
        :param ax: Axes.
        :type ax: matplotlib.axes.Axes
        :param data_type: Data type.
        :type data_type: str
        :param extent_type: Extent type.
        :type extent_type: str
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        
        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Combine guidelines and user keyword arguments
        if data_type is not None:
            kwargs = {**self.guidelines['data_type'][data_type][plot_type], **kwargs}
        if extent_type is not None:
            kwargs = {**self.guidelines['extent_type'][extent_type], **kwargs}

        # Plot data
        if type(da) == xr.DataArray:
            da.plot.contour(ax=ax, **kwargs)
        elif type(da) == xu.UgridDataArray:
            da.ugrid.plot.contour(ax=ax, **kwargs)

    # Plot data using contourf
    def contourf(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        """ Plot data using contourf.

        :param da: Data array.
        :type da: xarray.DataArray or xugrid.UgridDataArray
        :param ax: Axes.
        :type ax: matplotlib.axes.Axes
        :param data_type: Data type.
        :type data_type: str
        :param extent_type: Extent type.
        :type extent_type: str
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        
        # Get plot_type (function name)
        plot_type = inspect.currentframe().f_code.co_name

        # Combine guidelines and user keyword arguments
        if data_type is not None:
            kwargs = {**self.guidelines['data_type'][data_type][plot_type], **kwargs}
        if extent_type is not None:
            kwargs = {**self.guidelines['extent_type'][extent_type], **kwargs}

        # Plot data
        if type(da) == xr.DataArray:
            da.plot.contourf(ax=ax, **kwargs)
        elif type(da) == xu.UgridDataArray:
            da.ugrid.plot.contourf(ax=ax, **kwargs)
    
    # Plot data using quiver
    def quiver(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        pass

    # Plot data using streamplot
    def streamplot(self, da, ax=None, data_type=None, extent_type=None, **kwargs):
        pass

    # Plot geometries using geopandas
    def geometries(self, gdf, ax=None, geometry_type=None, extent_type=None, **kwargs):
        pass

    # Plot cartopy geometries using geopandas
    def cartopy(self, ax=None, extent_type=None, **kwargs):
        pass

    # Plot basemap using contextily
    def basemap(self, ax=None, map_type=None, extent_type=None, **kwargs):
        pass

    # =============================================================================
    # Specialised plot methods
    # =============================================================================
    # Plot bathymetry
    def bathymetry(self, da, ax=None, extent_type=None, **kwargs):
        """ Plot data and geometries as bathymetry.

        :param da: Data array.
        :type da: xarray.DataArray or xugrid.UgridDataArray
        :param ax: Axes.
        :type ax: matplotlib.axes.Axes
        :param extent_type: Extent type.
        :type extent_type: str
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: None
        :rtype: None
        """

        # Plot data
        if type(da) == xr.DataArray:
            self.pcolormesh(da, ax=ax, data_type='bathymetry', extent_type=extent_type, **kwargs)
            self.contour(da, ax=ax, data_type='bathymetry', extent_type=extent_type, **kwargs)
        elif type(da) == xu.UgridDataArray:
            self.pcolormesh(da, ax=ax, data_type='bathymetry', extent_type=extent_type, **kwargs)
            self.contour(da, ax=ax, data_type='bathymetry', extent_type=extent_type, **kwargs)
    
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

    # Plot sediment transport
    def sediment_transport(self, da, ax=None, extent_type=None, **kwargs):
        pass

   

    # Plot model grid
    def model_grid(self, da, ax=None, extent_type=None, **kwargs):
        pass

