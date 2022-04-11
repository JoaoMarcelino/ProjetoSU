import numpy as np
import pandas as pd
import geopandas as gpd
import scipy
import shapely
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from shapely.geometry import MultiPoint,Point,Polygon,MultiPoint,MultiPolygon

def writeGeoDFToGis(geodf,targetFile):
    if len(geodf)==0:
        return 
    os.makedirs(os.path.dirname(targetFile), exist_ok=True)

    geodf.to_file(targetFile, driver='ESRI Shapefile')


if __name__=='__main__':
    minX=-8.44896
    minY=40.17894
    maxX=-8.38804
    maxY=40.22520
    
    poiBuffer=100 #meters
    bbox = (minX,minY,maxX,maxY)

    buildingsFileName="./datasets/buildings/hotosm_prt_buildings_polygons.shp"
    poisFileName="./datasets/pois/comercio/points/points.shp"

    build = gpd.read_file(buildingsFileName,bbox=bbox)
    pois=gpd.read_file(poisFileName)

    build=build.to_crs(epsg=3857)
    pois=pois.to_crs(epsg=3857)
    #print(build.crs)
    #print(build)
    #print(pois)

    aux = {'clusterID': [], 'geometry': []}
    newBuild = gpd.GeoDataFrame(aux, crs="EPSG:3857")
    
    for i in tqdm(range(len(build))):
        poly=build.loc[i,'geometry']
        for k in range(len(pois)):
            clusterID=pois.loc[k,'clusterID']
            poi=pois.loc[k,'geometry'].buffer(poiBuffer)
            if clusterID==-1:
                continue
            if poi.intersects(poly):
                aux = {'clusterID': [clusterID], 'geometry': [poly]}
                newBuild1 = gpd.GeoDataFrame(aux, crs="EPSG:3857")
                newBuild=pd.concat([newBuild,newBuild1])
                break

    print(newBuild)
    writeGeoDFToGis(newBuild, "./datasets/buildings/Coimbra/comercio/comercio.shp")



