import importlib.metadata

from . import axes, basemaps, colormaps, geometries, interactive, rescale, structured_data, unstructured_data, utils, videos
from .rpclass import rpclass

__version__ = importlib.metadata.version(__package__)

__all__ = ["axes", "basemaps", "colormaps", "structured_data", "unstructured_data", "geometries", "interactive", "rescale", "utils", "videos"]

rpc = rpclass()
