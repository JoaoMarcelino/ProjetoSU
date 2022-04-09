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

def reorderDataframeIndex(df):
    df=df.reset_index()
    df=df.drop(columns=['index'])
    return df

def filterDataFrameByArea(dataframe,minX,minY,maxX,maxY):
    dataframe=dataframe[dataframe.X>minX]
    dataframe=dataframe[dataframe.Y>minY]
    dataframe=dataframe[dataframe.X<maxX]
    dataframe=dataframe[dataframe.Y<maxY]

    dataframe=reorderDataframeIndex(dataframe)
    return dataframe

def taxonomy():
    dicti={}
    dicti['infraestrutura']=['police','post_box','recycling','post_office','parking','telephone','post_office','fire_station','bank','fuel','information','toilet']
    dicti['saude']=['pharmacy','hospital']
    dicti['comercio']=['restaurant','cafe','pub','supermarket','fast_food','atm','bakery']
    dicti['educacao']=['school','library','kindergarten']
    dicti['lazer']=['theatre','museum','cinema','attraction','nightclub']

    return dicti

#dataframe:   dataframe
#taxonomy:  function that returns dictionary ex.: {'class1':['subclass1','subclass2'],'class2':['subclass1']}
#splitedDf:   dictionary of dataframes dataframe
def splitDataframByTaxonomy(dataframe,taxonomy):

    splitedDf={}
    for className in taxonomy().keys():
        df = pd.DataFrame(columns=['X', 'Y','category'])
        subclasses=taxonomy()[className]
        for subclass in subclasses:
            rows=dataframe.loc[dataframe.fclass==subclass].copy()
            rows.loc[:,'category']=className
            df=pd.concat([df,rows])

        df=reorderDataframeIndex(df)
        splitedDf[className]=df

    
    return splitedDf

#cluster:   list    ex.:["Column1","Column2"]
#centroid:  dataframe
def deleteColumns(df,columns):
    return df.drop(columns=columns)

#df:   dataframe
#column:  int
def getUniqueValuesColumn(df,column):
    values=[]
    for i in range(len(df)):
        value=df.iloc[i,column]
        if value not in values:
            values.append(value)

#cluster:   list    ex.:[[x,y],[x,y]]
#centroid:  list    ex.:[x,y]  
def getCentroid(cluster): 
    centroid = [MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y]
    return centroid

#df: dataframe with GIS columns X and Y 
#labeledPoints: list with numeric labels same size as initial number of rows [1,0,1,1,1,0,3,-1] -1 means outlier
#uniqueClusterLabels: unique set of numeric cluster labels  {1,2,3,4}
def dbScanOverDataframe(df,epsilonKm,minSamples):
    if len(df)==0:
        raise ValueError('Empty Dataframe')
        
    coords = df.loc[:,('X', 'Y')].to_numpy()
    coords=coords.astype(float)
    
    kms_per_radian = 6371.0088
    epsilon = epsilonKm / kms_per_radian
    
    #dbscan  
    db = DBSCAN(eps=epsilon, min_samples=minSamples, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    
    labeledPoints =db.labels_
    uniqueClusterLabels = set(labeledPoints)

    clustersDf = pd.DataFrame(columns=['X', 'Y','clusterID','nPoints'])
    for label in uniqueClusterLabels:
        if label==-1: #outliers are marked with clusterID=-1
            continue
        else:
            cds=coords[labeledPoints==label]
            centroid=getCentroid(cds)
            newDF=pd.DataFrame([[centroid[0],centroid[1],label,len(cds)]],columns=['X', 'Y','clusterID','nPoints'])
            clustersDf=pd.concat([clustersDf,newDF])

    df['clusterID']=labeledPoints.tolist()
    clustersDf=reorderDataframeIndex(clustersDf)
    return df,labeledPoints,uniqueClusterLabels,clustersDf
    
#df: dataframe with GIS columns X and Y
def writeDataFramToGis(df,targetFile):
    if len(df)==0:
        return 
    os.makedirs(os.path.dirname(targetFile), exist_ok=True)

    df=reorderDataframeIndex(df)
    df['geometry']= df.apply(lambda x: Point(float(x['X']),float(x['Y'])), axis=1)
    
    df = gpd.GeoDataFrame(df, geometry='geometry')
    df.crs= "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
    df.to_file(targetFile, driver='ESRI Shapefile')
    
    
if __name__=='__main__':
    minX=-8.44896
    minY=40.17894
    maxX=-8.38804
    maxY=40.22520

    epsilonKm=0.2
    minPoints=3

    poisFilename='./datasets/pois/pois.csv'
    pois=pd.read_csv(poisFilename)
    poisCoimbra=filterDataFrameByArea(pois, minX, minY, maxX, maxY)
    poisCoimbra=deleteColumns(poisCoimbra,['osm_id','lastchange','code','name' ])

    

    classes=getUniqueValuesColumn(poisCoimbra, 2)
    splitedPois=splitDataframByTaxonomy(poisCoimbra, taxonomy)

    
    allClusters={}
    for category in taxonomy().keys():
        splitedPois[category],_,_,clusters=dbScanOverDataframe(splitedPois[category], epsilonKm, minPoints)
        allClusters[category]=clusters
        print(clusters)

    for category in taxonomy().keys():
        df=splitedPois[category]
        pointsPath="./datasets/pois/{}/points/points.shp".format(category)
        writeDataFramToGis(df, pointsPath)

        df=allClusters[category]
        clustersPath="./datasets/pois/{}/clusters/clusters.shp".format(category)
        writeDataFramToGis(df, clustersPath)
        

    


