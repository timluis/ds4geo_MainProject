import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.plot import show


def normalize(array):
    """Normalizes numpy arrays into scale 0.0 - 1.0"""
    array_min, array_max = array.min(), array.max()
    return ((array - array_min)/(array_max - array_min))

def RGBnorm(raster,img_shape=True):
    """Returns a raster with RGB color normalized
    raster: rasterio DatasetReader"""
    color_dict = {color.name:raster.read(n+1) for n,color in enumerate(raster.colorinterp)}
    for k,v in color_dict.items():
      color_dict[k] = normalize(v)
    rgb =  np.dstack(tuple(v for v in color_dict.values()))
    if img_shape==False:
      rgb=rasterio.plot.reshape_as_raster(rgb)
    return rgb

def reproject_raster(raster_in,raster_out,dst_crs):

  with rasterio.open(raster_in) as src:
      transform, width, height = calculate_default_transform(
          src.crs, dst_crs, src.width, src.height, *src.bounds)
      kwargs = src.meta.copy()
      kwargs.update({
          'crs': dst_crs,
          'transform': transform,
          'width': width,
          'height': height
          })
      kwargs['photometric'] = 'RGB'

      with rasterio.open(raster_out, 'w', **kwargs) as dst:
          for i in range(1, src.count + 1):
              reproject(
                  source=rasterio.band(src, i),
                  destination=rasterio.band(dst, i),
                  src_transform=src.transform,
                  src_crs=src.crs,
                  dst_transform=transform,
                  dst_crs=dst_crs,
                  resampling=Resampling.nearest)
              
def crop_to_skiarea(raster_in,raster_out,skiarea):
  with rasterio.open(raster_in) as src:
    out_image,out_transform = rasterio.mask.mask(src,ski_areas.loc[ski_areas.NAME == skiarea].geometry,crop=True)
    out_meta = src.meta

  out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
  out_meta['photometric'] = 'RGB'
  with rasterio.open(raster_out,'r+',**out_meta) as dest:
    dest.write(out_image)

def crop_and_transform(raster_in,raster_out,crs,skiarea):
  reproject_raster(raster_in,raster_out,crs)
  crop_to_skiarea(raster_out,raster_out,skiarea)


