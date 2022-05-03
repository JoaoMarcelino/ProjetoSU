import numpy as np
import pandas as pd
import geopandas as gpd
import scipy
import shapely
import matplotlib.pyplot as plt
import os

from sklearn.cluster import DBSCAN,AgglomerativeClustering,KMeans
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


def dbScanGeoDataframe(gdf,epsilonKm,minSamples):
    if len(gdf)==0:
        raise ValueError('Empty GeoDataframe')
        
    coords = np.array([[p.x,p.y] for p in gdf.loc[:,('geometry')]])
    
    #dbscan  
    db = DBSCAN(eps=epsilonKm, min_samples=minSamples).fit(coords)
    
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
            

    gdf['clusterID']=labeledPoints.tolist()
    clustersDf=reorderDataframeIndex(clustersDf)
    return gdf,labeledPoints,uniqueClusterLabels,clustersDf

def aglomerativeGeoDataframe(gdf,nClusters):
    if len(gdf)==0:
        raise ValueError('Empty GeoDataframe')
    
    coords = []
    for geom in gdf.loc[:,('geometry')]:
        x=geom.x
        y=geom.y
        coords.append([x,y])
    coords=np.array(coords).astype(float)

    #aglomerative clustering 
    db = AgglomerativeClustering(n_clusters=nClusters).fit(coords)

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
            

    gdf['clusterID']=labeledPoints.tolist()
    clustersDf=reorderDataframeIndex(clustersDf)
    return gdf,labeledPoints,uniqueClusterLabels,clustersDf

def KMeansGeoDataframe(gdf,nClusters):
    if len(gdf)==0:
        raise ValueError('Empty GeoDataframe')
    
    coords = []
    for geom in gdf.loc[:,('geometry')]:
        x=geom.x
        y=geom.y
        coords.append([x,y])
    coords=np.array(coords).astype(float)

    #aglomerative clustering 
    db = KMeans(n_clusters=nClusters).fit(coords)

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
            

    gdf['clusterID']=labeledPoints.tolist()
    clustersDf=reorderDataframeIndex(clustersDf)
    return gdf,labeledPoints,uniqueClusterLabels,clustersDf

#df: dataframe with GIS columns X and Y
def writeDataFramToGis(df,targetFile,crs):
    if len(df)==0:
        print("here")
        return 
    os.makedirs(os.path.dirname(targetFile), exist_ok=True)

    df=reorderDataframeIndex(df)
    df['geometry']= df.apply(lambda x: Point(float(x['X']),float(x['Y'])), axis=1)
    
    df = gpd.GeoDataFrame(df, geometry='geometry')
    df.crs= crs
    df.to_file(targetFile, driver='ESRI Shapefile')

def readGEODFToGis(targetFile,bbox=False):
    if bbox!=False:
        gdf = gpd.read_file(targetFile,bbox=bbox)
        return gdf
    else:
        gdf=gpd.read_file(targetFile)
        return gdf

def writeGeoDFToGis(geodf,targetFile):
    if len(geodf)==0:
        return 
    os.makedirs(os.path.dirname(targetFile), exist_ok=True)

    geodf.to_file(targetFile, driver='ESRI Shapefile')
def main1(): #split datatset of POIS into large categories and cluster each category with dbscan
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

def main2(type):#cluster comercio pois with dbscan
    minX=-8.44896
    minY=40.17894
    maxX=-8.38804
    maxY=40.22520
    epsilon=400
    nPoints=2
    ficheiro=f"./datasets/pois/{type}/points/points.shp"
    ficheiroPois=f"./datasets/pois/{type}/final/DBSCAN400.shp"
    ficheiroClusters=f"./datasets/pois/{type}/final/clustersDBSCAN400.shp"

    pois=readGEODFToGis(ficheiro)
    pois=pois.to_crs(epsg=3857)

    pois,_,_,clusters=dbScanGeoDataframe(pois, epsilon, nPoints)

    print(clusters)

    writeGeoDFToGis(pois, ficheiroPois)
    writeDataFramToGis(clusters, ficheiroClusters,"EPSG:3857")

if __name__=='__main__':
    """
    minX=-8.44896
    minY=40.17894
    maxX=-8.38804
    maxY=40.22520

    for i,epsilon in enumerate([200,300,500]):
        ficheiroComercio="./datasets/pois/comercio/points/points.shp"
        poisComercio=readGEODFToGis(ficheiroComercio)
        poisComercio=poisComercio.to_crs(epsg=3857)

        ficheiroComercioPois="./datasets/pois/testesClustering/points{}.shp".format(i)
        ficheiroComercioClusters="./datasets/pois/testesClustering/clusters{}.shp".format(i)
        poisComercio,_,_,clusters=dbScanGeoDataframe(poisComercio, epsilon, 3)

        writeGeoDFToGis(poisComercio, ficheiroComercioPois)
        writeDataFramToGis(clusters, ficheiroComercioClusters,"EPSG:3857")

    for i,nClusters in enumerate([5,10,20]):
        ficheiroComercio="./datasets/pois/comercio/points/points.shp"
        poisComercio=readGEODFToGis(ficheiroComercio)
        poisComercio=poisComercio.to_crs(epsg=3857)

        ficheiroComercioPois="./datasets/pois/testesClustering/points{}.shp".format(i+3)
        ficheiroComercioClusters="./datasets/pois/testesClustering/clusters{}.shp".format(i+3)
        poisComercio,_,_,clusters=aglomerativeGeoDataframe(poisComercio, nClusters)

        writeGeoDFToGis(poisComercio, ficheiroComercioPois)
        writeDataFramToGis(clusters, ficheiroComercioClusters,"EPSG:3857")

    for i,nClusters in enumerate([10]):
        ficheiroComercio="./datasets/pois/comercio/points/points.shp"
        poisComercio=readGEODFToGis(ficheiroComercio)
        poisComercio=poisComercio.to_crs(epsg=3857)

        ficheiroComercioPois="./datasets/pois/testesClustering/points{}.shp".format(i+6)
        ficheiroComercioClusters="./datasets/pois/testesClustering/clusters{}.shp".format(i+6)
        poisComercio,_,_,clusters=KMeansGeoDataframe(poisComercio, nClusters)

        writeGeoDFToGis(poisComercio, ficheiroComercioPois)
        writeDataFramToGis(clusters, ficheiroComercioClusters,"EPSG:3857")
    """

    types = ["comercio", "educacao", "infraestrutura", "lazer", "saude"]
    for type in types:
        pass
    main2("saude")
    

    
        

    


