import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
#from rasterio.plot import show
import pandas as pd 
from sentinelhub import SHConfig, MimeType, CRS, BBox, SentinelHubRequest, SentinelHubDownloadClient, \
    DataCollection, bbox_to_dimensions
import datetime



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


def RequestSatImg(time_interval,evalscript,coords_bbox,size,config,ski_area,ccov=0.8,collection=DataCollection.SENTINEL2_L2A):
    """ SentinelHubRequest for timeinterval with given evalscript 
    time_interval: tuple,string,datetimeobject,
    evalscript: string
    coord_bbox: sentinelhub.geometry.BBox
    size: tuple
    config: sentinelhub sh config
    ski_area: string 
    ccov: int
    collection: sentinelhub.DataCollection"""
    folder = 'Data/Satellite_data/' + ski_area
    return SentinelHubRequest(
    data_folder=folder,
    evalscript=evalscript,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=collection,
            maxcc=ccov,
            time_interval=time_interval,
            mosaicking_order='leastCC'
        )
    ],
    responses=[
        SentinelHubRequest.output_response('default', MimeType.TIFF)
    ],
    bbox=coords_bbox,
    size=size,
    config=config
)

def DownloadTimeseries(from_date,to_date,evalscript,coords_bbox,size,config,ski_area):
    """ Downloads satellite image weekly timeseries 
    from_date: datetime object
    to_date: datetime object
    evalscript: string
    coord_bbox: sentinelhub.geometry.BBox
    size: tuple
    config: sentinelhub sh config
    ski_area: string """
    delta = abs(to_date-from_date).days//7
    dates = [(from_date + datetime.timedelta(weeks=x),from_date + datetime.timedelta(weeks=x+1)) for x in range(delta+1)]
    list_of_requests = [RequestSatImg(date,evalscript,coords_bbox,size,config,ski_area) for date in dates]
    list_of_requests = [request.download_list[0] for request in list_of_requests]
    SentinelHubDownloadClient(config=config).download(list_of_requests, max_threads=5)

def GetBBoxSize(ski_areas,name):
    """ Creates bbox and size for a given ski area
    ski_areas: geopandas.DataFrame
    name: string"""
    coords = ski_areas.loc[ski_areas.NAME == name].geometry.bounds.to_numpy()[0]
    res = 10
    coords_bbox = BBox(bbox=[x for x in coords],crs=CRS.WGS84)
    size = bbox_to_dimensions(coords_bbox,resolution=res)
    return coords_bbox,size