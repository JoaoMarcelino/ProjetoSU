import json
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

from travelTimes import writeGeoDFToGis


def get_number_pois(file, cluster, type):
    clusters = gpd.read_file(file)

    for i in range(len(clusters.X)):
        cluster_test = Point(float(clusters.X[i]), float(clusters.Y[i]))

        #print(cluster, cluster_test, cluster.distance(cluster_test))

        if cluster.distance(cluster_test) <= 0.0000001:
            return clusters.nPoints[i], clusters.clusterID[i]

    return None, None

def getScore(point, square = None):

    #find Square where house is situated

    squares_Type = ["comercio", "educacao", "infraestrutura", "lazer", "saude"]

    #Get Closest Cluster by type (distance and number of poi)

    info = {}
    val = []
    max_score = 0

    for index, type in enumerate(squares_Type):

        file_cluster = f"./datasets/pois/{type}/final/clustersDBSCAN400.shp"

        file_square = f"./datasets/buildings/travelTimes/{type}/buildings.shp"

        squares = gpd.read_file(file_square)

        for i in range(len(squares.time)):


            if squares.geometry[i].contains(point):
                #print("Sucess")
                
                cluster = Point(squares.nCluster_X[i], squares.nCluster_Y[i])
                #cluster = Point(squares.nearestClu[i], squares.nearestC_1[i])

                pois, id= get_number_pois(file_cluster, cluster, type)

                score = int(pois)/float(squares.time[i])

                info[index] = {
                    "type": type,
                    "time":squares.time[i],
                    "busTime":squares.busTime[i],
                    "walkTime":squares.walkTime[i],
                    "pois":pois,
                    "id": id,
                    "score": score,
                    }

                val.append(score)

    return val, info

    #print(values)

    if square == None:
        values["point"] = point

    out_file = open("./datasets/score.json", "w")
  
    json.dump(values, out_file, indent = 4)
    
    out_file.close()

    #Score

    return values



def getBestBySquare():
    score_file = f"./datasets/buildings/travelTimes/score.shp"
    squareWidth=300
        
    squaresDic = {}
    squares = gpd.GeoDataFrame(squaresDic, crs="EPSG:3857")
    
    x=-942687.6
    while x<-933027.4:
        y=4891166.6
        while y<4900545.5:
            square=Polygon([(x,y),(x+squareWidth,y),(x+squareWidth,y+squareWidth),(x,y+squareWidth)])
            centerPoint=square.centroid

            score, info = getScore(centerPoint, square)
            
            index = score.index(max(score))

            aux = info[index]
            aux['geometry'] = [square]

            squareRow = gpd.GeoDataFrame(aux, crs="EPSG:3857")
            squares=pd.concat([squares,squareRow])
            #print("{} {}".format(timeToBus,timeToCluster))
            y+=squareWidth
        x+=squareWidth
    #print(squares)
    writeGeoDFToGis(squares, score_file)


if __name__ == "__main__":
    #house = Point(-937781.5,4894487.3)
    #getScore(house)

    getBestBySquare()