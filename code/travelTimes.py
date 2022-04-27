import numpy as np
import pandas as pd
import geopandas as gpd
import scipy
import shapely
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from shapely.geometry import MultiPoint,Point,Polygon,MultiPoint,MultiPolygon
from shapely.ops import nearest_points

def writeGeoDFToGis(geodf,targetFile):
    if len(geodf)==0:
        return 
    os.makedirs(os.path.dirname(targetFile), exist_ok=True)

    geodf.to_file(targetFile, driver='ESRI Shapefile')

def get_nearest_values(point, other_gdf, value_column="geometry"):
    """Find the nearest point and return the corresponding value from specified value column."""

    # Create an union of the other GeoDataFrame's geometries:
    other_points = other_gdf["geometry"].unary_union

    # Find the nearest points
    nearest_geoms = nearest_points(point, other_points)

    return nearest_geoms[1]


def main():
    minX=-8.44896
    minY=40.17894
    maxX=-8.38804
    maxY=40.22520
    bbox = (minX,minY,maxX,maxY)
    
    walkingMetersPerMinute=0.085*1000
    busMetersPerMinute=0.33*1000
    squareWidth=50

    buildingsFileName="./datasets/buildings/hotosm_prt_buildings_polygons.shp"
    clustersFileName="./datasets/pois/comercio/final/clustersDBSCAN400.shp"
    stopsFilename="./datasets/bus/stops.shp"
    newbuildingsFileName="./datasets/buildings/travelTimes/buildings.shp"

    buildings = gpd.read_file(buildingsFileName,bbox=bbox)
    clusters=gpd.read_file(clustersFileName)
    busStops=gpd.read_file(stopsFilename)

    buildings=buildings.to_crs(epsg=3857)
    clusters=clusters.to_crs(epsg=3857)   
    busStops=busStops.to_crs(epsg=3857)

    squaresDic = {'geometry': [],'time': [],'busTime':[],'walkTime':[]}
    squares = gpd.GeoDataFrame(squaresDic, crs="EPSG:3857")

    print("Calculating Squares Times")
    x=-942687.6
    while x<-933027.4:
        y=4891166.6
        while y<4900545.5:
            square=Polygon([(x,y),(x+squareWidth,y),(x+squareWidth,y+squareWidth),(x,y+squareWidth)])
            centerPoint=square.centroid
            nearestStop=get_nearest_values(centerPoint, busStops)
            nearestCluster=get_nearest_values(nearestStop, clusters)

            timeToBus=centerPoint.distance(nearestStop)/walkingMetersPerMinute
            timeToCluster=nearestStop.distance(nearestCluster)/busMetersPerMinute

            aux = { 'geometry': [square],'time': [timeToBus+timeToCluster],'busTime':[timeToCluster],'walkTime':[timeToBus]}
            squareRow = gpd.GeoDataFrame(aux, crs="EPSG:3857")
            squares=pd.concat([squares,squareRow])
            #print("{} {}".format(timeToBus,timeToCluster))
            y+=squareWidth
        x+=squareWidth
    print(squares)
    writeGeoDFToGis(squares, newbuildingsFileName)

if __name__=="__main__":
    main()