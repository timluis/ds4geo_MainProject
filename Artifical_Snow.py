import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.plot import show


def normalize(array):
    """Normalizes numpy arrays into scale 0.0 - 1.0"""
    array_min, array_max = array.min(), array.max()
    return ((array - array_min)/(array_max - array_min))

def RGBnorm(raster):
    """Returns a raster with RGB color normalized
    raster: rasterio DatasetReader"""
    color_dict = {color.name:raster.read(n+1) for n,color in enumerate(raster.colorinterp)}
    for k,v in color_dict.items():
      color_dict[k] = normalize(v)
    rgb =  np.dstack(tuple(v for v in color_dict.values()))
    rgb=rasterio.plot.reshape_as_raster(rgb)
    return rgb

