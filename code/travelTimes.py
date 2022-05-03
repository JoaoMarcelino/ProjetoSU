from turtle import getscreen
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


def getBuildings(type):
    minX=-8.44896
    minY=40.17894
    maxX=-8.38804
    maxY=40.22520
    bbox = (minX,minY,maxX,maxY)
    
    walkingMetersPerMinute=0.085*1000
    busMetersPerMinute=0.33*1000
    squareWidth=300

    buildingsFileName="./datasets/buildings/hotosm_prt_buildings_polygons.shp"
    clustersFileName=f"./datasets/pois/{type}/final/clustersDBSCAN400.shp"
    #clustersFileName=f"./datasets/pois/{type}/clusters/clusters.shp"
    stopsFilename="./datasets/bus/stops.shp"
    newbuildingsFileName=f"./datasets/buildings/travelTimes/{type}/buildings.shp"

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
            nearestCluster=get_nearest_values(centerPoint, clusters)
            timeToCluster=centerPoint.distance(nearestCluster)/busMetersPerMinute

            timeToBus=centerPoint.distance(nearestStop)/walkingMetersPerMinute
            timeToCluster=nearestStop.distance(nearestCluster)/busMetersPerMinute

            aux = { 
                'geometry': [square],
                'time': [timeToBus+timeToCluster],
                'busTime':[timeToCluster],
                'walkTime':[timeToBus],
                'nCluster_X':[nearestCluster.x],
                'nCluster_Y':[nearestCluster.y],
                'nStop_X':[nearestStop.x],
                'nStop_y':[nearestStop.y],
                }

            squareRow = gpd.GeoDataFrame(aux, crs="EPSG:3857")
            squares=pd.concat([squares,squareRow])
            #print("{} {}".format(timeToBus,timeToCluster))
            y+=squareWidth
        x+=squareWidth
    #print(squares)
    writeGeoDFToGis(squares, newbuildingsFileName)


def getClusterInfo(point, clusters):

    for i in range(len(clusters.X)):
        cluster_test = Point(float(clusters.X[i]), float(clusters.Y[i]))

        #print(cluster, cluster_test, cluster.distance(cluster_test))

        if point.distance(cluster_test) <= 0.0000001:
            return clusters.nPoints[i], clusters.clusterID[i]

    return None, None

def getBuildingsByType():
    minX=-8.44896
    minY=40.17894
    maxX=-8.38804
    maxY=40.22520
    bbox = (minX,minY,maxX,maxY)
    
    walkingMetersPerMinute=0.085*1000
    busMetersPerMinute=0.33*1000
    squareWidth=300

    buildingsFileName="./datasets/buildings/hotosm_prt_buildings_polygons.shp"
    stopsFilename="./datasets/bus/stops.shp"
    score_file = "./datasets/buildings/score/score2.shp"

    buildings = gpd.read_file(buildingsFileName,bbox=bbox)
    busStops=gpd.read_file(stopsFilename)

    buildings=buildings.to_crs(epsg=3857)  
    busStops=busStops.to_crs(epsg=3857)


    types = ["comercio", "educacao", "infraestrutura", "lazer", "saude"]

    squaresDic = {'geometry': [],'time': [],'busTime':[],'walkTime':[]}
    squares = gpd.GeoDataFrame(squaresDic, crs="EPSG:3857")

    print("Calculating Squares Times")
    x=-942687.6
    while x<-933027.4:
        y=4891166.6
        while y<4900545.5:
            square=Polygon([(x,y),(x+squareWidth,y),(x+squareWidth,y+squareWidth),(x,y+squareWidth)])
            centerPoint=square.centroid

            walkTime = []
            busTime = []
            totalTime = []
            scores = []
            ids = []

            for type in types:

                clustersFileName=f"./datasets/pois/{type}/final/clustersDBSCAN400.shp"
                clusters=gpd.read_file(clustersFileName)
                clusters=clusters.to_crs(epsg=3857) 

                nearestStop=get_nearest_values(centerPoint, busStops)
                nearestCluster=get_nearest_values(nearestStop, clusters)

                nPoi, id = getClusterInfo(nearestCluster, clusters)
                

                timeToBus=centerPoint.distance(nearestStop)/walkingMetersPerMinute
                timeToCluster=nearestStop.distance(nearestCluster)/busMetersPerMinute

                time = timeToBus + timeToCluster

                score = 1 / float(time)

                walkTime.append(timeToBus)
                busTime.append(timeToCluster)
                totalTime.append(time)
                scores.append(score)
                ids.append(id)

            #get max

            index = scores.index(max(scores))

            aux = { 
                'geometry': [square],
                'time': [totalTime[index]],
                'busTime':[busTime[index]],
                'walkTime':[walkTime[index]],
                'nCluster_X':[nearestCluster.x],
                'nCluster_Y':[nearestCluster.y],
                'type': types[index],
                'score':scores[index],
                'id':ids[index],
                }

            squareRow = gpd.GeoDataFrame(aux, crs="EPSG:3857")
            squares=pd.concat([squares,squareRow])
            #print("{} {}".format(timeToBus,timeToCluster))
            y+=squareWidth
        x+=squareWidth
    #print(squares)
    writeGeoDFToGis(squares, score_file)


if __name__=="__main__":

    #squares_Type = ["comercio", "educacao"]#, "infrasestrutura", "lazer", "saude"]

    #for type in squares_Type:
    #    pass
    getBuildingsByType()