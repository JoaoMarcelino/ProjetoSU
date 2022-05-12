import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from shapely.geometry import *
from shapely.ops import nearest_points
from utils import *
import warnings
import googlemaps

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

def main():
    bbox,bbox1=getUsualBbox()
    crs,crs1=getUsualCRS()
    neighborsNumber=3
    gmaps = googlemaps.Client(key=getKeyFromFile("./keys.txt"))
    #amadora=(-1028025.5,4684553.5,-1024641.3,4687879.2)
    #alvalade=(-1019164,4683422,-1016834,4687388)
    #squares=getSquaresFromBounds([amadora,alvalade], 100, crs)
    #print(len(squares))

    lisboaReduzida=(-1048057,4677425,-1012800,4690708)
    points=getPointsFromGridSearch(lisboaReduzida, 1000, crs)
    print(len(points))
    
    #ax=plotBaseMap("../Dados/BaseLayer/roads.shp", "../Dados/BaseLayer/water.shp", bbox, bbox1, crs)
    #squares.plot(ax=ax,alpha=0.3)
    #points.plot(ax=ax,alpha=0.3)
    #plt.show()
    categorias=taxonomy().keys()
    print(categorias)
    
    for categoria in tqdm(list(categorias)):
        clusters=readGeodatafromFile("./datasets/facebookPOIS/clusters/clusters{}.shp".format(categoria),crs=crs)
        for i in tqdm(range(len(points))):
            neighbors=getNNearestPoints(points.loc[i,'geometry'], clusters, neighborsNumber)
            for k,neig in enumerate(neighbors):
                name="{}{}".format(categoria,k)
                points.at[i,name]=neig.iloc[0]['clusterID']
                 
    stops=readGeodatafromFile("./datasets/bus/Lisboa/stops.shp",crs=crs)
    for i in tqdm(range(len(points))):
            neighbors=getNNearestPoints(points.loc[i,'geometry'], stops, 1)
            for k,neig in enumerate(neighbors):
                name="stop{}".format(k)
                points.at[i,name]=neig.iloc[0]['id']
    
    print(points.head())
    writeGeodataToGis(points, "./datasets/facebookPOIS/richPOIS/rishPOIS.shp",crs=crs)

if __name__=="__main__":
    #squares_Type = ["comercio", "educacao"]#, "infrasestrutura", "lazer", "saude"]
    #for type in squares_Type:
    #    pass
    #getBuildingsByType()
    warnings.filterwarnings("ignore")
    main()