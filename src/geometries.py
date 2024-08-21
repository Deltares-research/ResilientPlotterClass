import cartopy.feature as cfeature
import geopandas as gpd
import pandas as pd
from pyproj import CRS as pyprojCRS
from rasterio.crs import CRS as rasterioCRS
from shapely.geometry import Polygon, MultiPolygon, MultiLineString, MultiPoint

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
        geometries = list(gdf.loc[idx, 'geometry'].geoms)
        kwargs = gdf.loc[idx, 'kwargs']

        gdf_feature = gpd.GeoDataFrame({'index':[idx]*len(geometries),
                                        'geometry':geometries,
                                        'kwargs':[kwargs]*len(geometries)},
                                        crs=gdf.crs)
        gdf_exploded = pd.concat([gdf_exploded, gdf_feature])
    gdf_exploded.reset_index(drop=True, inplace=True)

    # Clip the geodataframe
    gdf_clipped = gdf_exploded.copy()
    gdf_clipped['within'] = gdf_clipped['geometry'].within(bounds)
    gdf_clipped['intersects'] = gdf_clipped['geometry'].intersects(bounds)
    gdf_clipped = gdf_clipped[gdf_clipped['within'] | gdf_clipped['intersects']]
    gdf_clipped.loc[gdf_clipped['intersects'], 'geometry'] = gdf_clipped[gdf_clipped['intersects']].intersection(bounds)
    gdf_clipped = gdf_clipped.drop(columns=['within', 'intersects'])

    # Dissolve the geodataframe
    gdf_dissolved = gpd.GeoDataFrame()
    for idx in gdf_clipped['index'].unique():
        
        # Get the geometries and keyword arguments of the geodataframe
        geometries = list(gdf_clipped[gdf_clipped['index'] == idx]['geometry'])
        kwargs = gdf_clipped[gdf_clipped['index'] == idx]['kwargs'].iloc[0]

        # Split multi geometries into individual geometries
        geometries2 = []
        for geometry in geometries:
            if geometry.geom_type in ['MultiPolygon', 'MultiLineString', 'MultiPoint']:
                geometries2.extend(list(geometry.geoms))
            else:
                geometries2.append(geometry)
        
        # Combine geometries into multi geometries of the same type
        if geometries2[0].geom_type == 'Polygon':
            geometry = MultiPolygon(geometries2)
        elif geometries2[0].geom_type == 'LineString':
            geometry = MultiLineString(geometries2)
        elif geometries2[0].geom_type == 'Point':
            geometry = MultiPoint(geometries2)
        
        # Create a geodataframe for the feature
        gdf_feature = gpd.GeoDataFrame({'geometry':[geometry],
                                        'kwargs':[kwargs]},
                                        index = [idx], crs=gdf.crs)
        
        # Concatenate the geodataframe to the dissolved geodataframe
        gdf_dissolved = pd.concat([gdf_dissolved, gdf_feature])
    
    # Return the dissolved geodataframe
    return gdf_dissolved

def get_gdf_cartopy(features=None, bounds=None, crs=None):
    """Get a GeoDataFrame with cartopy geometries.

    :param features: Cartopy features to include in the GeoDataFrame. If ``None``, all cartopy features are included.
    :type features:  list[str], optional
    :param bounds:   Bounds of the cartopy geometries (``[xmin, ymin, xmax, ymax]``).
    :type bounds:    list[float], optional
    :param crs:      Coordinate reference system of the cartopy geometries. If ``None``, the coordinate reference system is set to ``'EPSG:4326'``.
    :type crs:       str, optional
    :return:         GeoDataFrame with cartopy geometries.
    :rtype:          geopandas.GeoDataFrame

    See also: `cartopy.feature <https://scitools.org.uk/cartopy/docs/latest/matplotlib/feature_interface.html>`_.
    """
    
    # Define cartopy features and their styles
    CFEATURES = {'borders':cfeature.BORDERS,
                 'coastline':cfeature.COASTLINE,
                 'lakes':cfeature.LAKES,
                 'land':cfeature.LAND,
                 'ocean':cfeature.OCEAN,
                 'rivers':cfeature.RIVERS,
                 'states':cfeature.STATES}
    KWARGS = {'borders':{'color':'black', 'linewidth':1, 'linestyle':'-', 'zorder':0.03},
              'coastline':{'color':'black', 'linewidth':1, 'linestyle':'-', 'zorder':0.03},
              'lakes':{'facecolor':[0.59375 , 0.71484375, 0.8828125], 'edgecolor':'none', 'zorder':0.02},
              'land':{'facecolor':[0.9375 , 0.9375 , 0.859375], 'edgecolor':'none', 'zorder':0.01},
              'ocean':{'facecolor':[0.59375 , 0.71484375, 0.8828125], 'edgecolor':'none', 'zorder':0.01},
              'rivers':{'color':[0.59375 , 0.71484375, 0.8828125], 'linewidth':1, 'linestyle':'-', 'zorder':0.02},
              'states':{'facecolor':'none', 'edgecolor':'black', 'linewidth':1, 'linestyle':':' , 'zorder':0.03}}
    
    # Get the cartopy features
    if features is None:
        features = ['land','ocean','lakes','rivers','coastline','borders','states']
    
    # Convert the crs to a pyproj.CRS
    if isinstance(crs, pyprojCRS):
        crs = crs
    elif isinstance(crs, rasterioCRS):
        crs = pyprojCRS.from_string(crs.to_string())
    elif isinstance(crs, str):
        crs = pyprojCRS.from_string(crs)
    elif crs is None:
        crs = 'EPSG:4326'
    else:
        raise ValueError('CRS type not supported. Please provide a pyproj.CRS, rasterio.CRS or str object.')
    
    # Create a GeoDataFrame for the cartopy features
    gdf_cartopy = gpd.GeoDataFrame()
    for feature in features:
        # Get the cartopy geometries
        geometries_ = list(CFEATURES[feature].with_scale('10m').geometries())

        # Combine geometries into one MultiPolygon or MultiLineString
        geometries = []
        for geometry in geometries_:
            if geometry.geom_type == 'Polygon':
                geometries.append(geometry)
            elif geometry.geom_type == 'MultiPolygon':
                geometries.extend(list(geometry.geoms))
            elif geometry.geom_type == 'LineString':
                geometries.append(geometry)
            elif geometry.geom_type == 'MultiLineString':
                geometries.extend(list(geometry.geoms))
               
        # Convert list of geometries to MultiPolygon or MultiLineString
        if geometries[0].geom_type == 'Polygon':
            geometries = MultiPolygon(geometries)
        elif geometries[0].geom_type == 'LineString':
            geometries = MultiLineString(geometries)
        
        # Create a GeoDataFrame for the cartopy feature
        gdf_feature = gpd.GeoDataFrame({'geometry':[geometries], 'kwargs':[KWARGS[feature]]}, index=[feature], crs='EPSG:4326')        
        
        # Concatenate the GeoDataFrame to the cartopy features
        gdf_cartopy = pd.concat([gdf_cartopy, gdf_feature])
    
    # Clip the cartopy geodataframe
    if bounds is not None:
        # Reproject the bounds to EPSG:4326
        gdf_bounds = gpd.GeoDataFrame({'geometry':[Polygon([(bounds[0], bounds[1]), (bounds[2], bounds[1]), (bounds[2], bounds[3]), (bounds[0], bounds[3])])]}, crs=crs)
        gdf_bounds = gdf_bounds.to_crs('EPSG:4326')
        gdf_cartopy = _clip_gdf_cartopy(gdf_cartopy, gdf_bounds.total_bounds)
    
    # Reproject the cartopy geodataframe
    if crs != 'EPSG:4326':
        gdf_cartopy = gdf_cartopy.to_crs(crs)
    
    # Remove invalid geometries
    for index in gdf_cartopy.index:
        geometries = gdf_cartopy.loc[index, 'geometry']
        if geometries.geom_type == 'MultiPolygon':
            gdf_cartopy.loc[index, 'geometry'] = MultiPolygon([geom for geom in geometries.geoms if geom.is_valid])
        elif geometries.geom_type == 'MultiLineString':
            gdf_cartopy.loc[index, 'geometry'] = MultiLineString([geom for geom in geometries.geoms if geom.is_valid])
    
    # Return the GeoDataFrame of cartopy features
    return gdf_cartopy