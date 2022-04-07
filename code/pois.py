import numpy as np
import pandas as pd
import geopandas as gpd
import scipy
import shapely
import matplotlib.pyplot as plt
import os

from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint,Point


#import pysal
#import bokeh
#import cartopy
#import statsmodels
#import sklearn
#import geoplot
#import osmnx
#import folium
#import dash
#import rasterio
#import rasterstats

def filterDataFrameByArea(dataframe,minX,minY,maxX,maxY):
    dataframe=dataframe[dataframe.X>minX]
    dataframe=dataframe[dataframe.Y>minY]
    dataframe=dataframe[dataframe.X<maxX]
    dataframe=dataframe[dataframe.Y<maxY]
    return dataframe

def taxonomy():
    dicti={}
    dicti['infraestrutura']=['police','post_box','recycling','post_office','parking','telephone','post_office','fire_station','bank','fuel','information','toilet']
    dicti['saude']=['pharmacy','hospital']
    dicti['comercio']=['restaurant','cafe','pub','supermarket','fast_food','atm','bakery']
    dicti['educacao']=['school','library','kindergarten']
    dicti['lazer']=['theatre','museum','cinema','attraction','nightclub']

    return dicti

def splitDataframByTaxonomy(dataframe,taxonomy):
    splitedPois={}
    for poiClass in taxonomy().keys():
        df = pd.DataFrame(columns=['X', 'Y','className'])
        subclasses=taxonomy()[poiClass]
        for subclass in subclasses:
            rows=poisCoimbra.loc[poisCoimbra.fclass==subclass].copy()
            rows.loc[:,'className']=poiClass
            df=pd.concat([df,rows])
        splitedPois[poiClass]=df
    return splitedPois

def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    return centroid


if __name__=='__main__':
    minX=-8.44896
    minY=40.17894
    maxX=-8.38804
    maxY=40.22520

    poisFilename='./datasets/pois/pois.csv'
    pois=pd.read_csv(poisFilename)
    poisCoimbra=filterDataFrameByArea(pois, minX, minY, maxX, maxY)
    poisCoimbra=poisCoimbra.drop(columns=['osm_id','lastchange','code','name' ])

    classes=[]
    for i in range(len(poisCoimbra)):
        poiClass=poisCoimbra.iloc[i,2]
        if poiClass not in classes:
            classes.append(poiClass)

    splitedPois=splitDataframByTaxonomy(poisCoimbra, taxonomy)
    clustersAllPOIS={}
    for category in taxonomy().keys():
        epsilonKm=0.5
        minSamples=2
        df=splitedPois[category]
        coords = df.loc[:,('X', 'Y')].to_numpy()
        coords=coords.astype(float)

        #dbscan
        kms_per_radian = 6371.0088
        epsilon = epsilonKm / kms_per_radian  
        db = DBSCAN(eps=epsilon, min_samples=minSamples, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
        
        cluster_labels =db.labels_
        uniqueCluster_labels = set(cluster_labels)

        #get centroids for each cluster for each category
        clustersDf = pd.DataFrame(columns=['X', 'Y','className','clusterID','nPoints'])
        clusters={}
        for cluster_label in uniqueCluster_labels:
            if cluster_label==-1: #outliers are marked with clusterID=-1
                continue
            else:
                clusters[cluster_label]=coords[cluster_labels==cluster_label]
                centroid=get_centermost_point(clusters[cluster_label])
                row={'X':[centroid[0]],'Y':[centroid[1]],'className':[category],'clusterID':[cluster_label],'nPoints':[len(clusters[cluster_label])]}
                newDF=pd.DataFrame(data=row)
                clustersDf=pd.concat([clustersDf,newDF])

        clustersAllPOIS[category]=clustersDf

    for category in taxonomy().keys():
        points=splitedPois[category]
        clusters=clustersAllPOIS[category]

        points['geometry']=None
        points=points.reset_index()
        points=points.drop(columns=['index'])
        for i in range(len(points)):
            x=points.iloc[i,0]
            y=points.iloc[i,1]
            points.loc[i,"geometry"]=Point(float(x),float(y))

        clusters['geometry']=None
        clusters=clusters.reset_index()
        clusters=clusters.drop(columns=['index'])
        for i in range(len(clusters)):
            x=clusters.iloc[i,0]
            y=clusters.iloc[i,1]
            clusters.loc[i,"geometry"]=Point(float(x),float(y))

        points = gpd.GeoDataFrame(points, geometry='geometry')
        clusters = gpd.GeoDataFrame(clusters, geometry='geometry')
        points.crs= "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
        clusters.crs= "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
        try:
            os.mkdir("./datasets/pois/{}".format(category))
        except:
            pass
        points.to_file("./datasets/pois/{}/points.shp".format(category), driver='ESRI Shapefile')
        clusters.to_file("./datasets/pois/{}/clusters.shp".format(category), driver='ESRI Shapefile')


    


