import importlib.metadata

from . import axes, basemaps, colormaps, data_xarray, data_xugrid, geometries, interactive, rescale, utils, videos
from .rpclass import rpclass

__version__ = importlib.metadata.version(__package__)

__all__ = ["axes", "basemaps", "colormaps", "data_xarray", "data_xugrid", "geometries", "interactive", "rescale", "utils", "videos"]

rpc = rpclass()
