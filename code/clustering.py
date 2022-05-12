import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from sklearn.cluster import DBSCAN,AgglomerativeClustering,KMeans
from shapely.geometry import *


def reorderDataframeIndex(df):
    df=df.reset_index()
    df=df.drop(columns=['index'])
    return df

def writeGeodataToGis(geodf,targetFile,crs="EPSG:3857"):
    if len(geodf)==0:
        return 
    os.makedirs(os.path.dirname(targetFile), exist_ok=True)
    geodf=geodf.to_crs(crs)
    geodf.to_file(targetFile, driver='ESRI Shapefile')

def readGeodatafromFile(targetFile,bbox=None,crs="EPSG:3857"):
    data=None 
    if bbox==None:
        data= gpd.read_file(targetFile)
    else:
        data= gpd.read_file(targetFile,bbox=bbox)

    data=data.to_crs(crs)
    return data

def plotBaseMap(roadsMapFileDir,waterMapFileDir,bbox,bbox1,crs):
    #bbox = (-8.44896,40.17894,-8.38804,40.22520)
    #bbox1=(-942000.6,4891166.6,-933027.4,4900545.5)
    #crs="EPSG:3857"
    #crs="EPSG:4326"
    roads = readGeodatafromFile(roadsMapFileDir,bbox,crs)
    water=readGeodatafromFile(waterMapFileDir,bbox,crs)

    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    base=roads.plot(ax=ax,color='#c0a4e3', edgecolor='#c0a4e3',alpha=0.2)
    water.plot(ax=ax,color='yellowgreen', edgecolor='yellowgreen',alpha=0.1)
    ax.set_xlim(bbox1[0],bbox1[2])
    ax.set_ylim(bbox1[1],bbox1[3])
    return ax

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

def clusterGeoDataframe(points,epsilonKm,minSamples):
    if len(points)==0:
        raise ValueError('Empty GeoDataframe')
        
    coords = np.array([[p.x,p.y] for p in points.loc[:,('geometry')]])
    
    #dbscan  
    db = DBSCAN(eps=epsilonKm, min_samples=minSamples).fit(coords)
    
    labeledPoints =db.labels_
    uniqueClusterLabels = set(labeledPoints)
    clustersDf = gpd.GeoDataFrame({"geometry":[],"clusterID":[],"nPoints":[]},crs="EPSG:3857")
    for label in uniqueClusterLabels:
        if label==-1: #outliers are marked with clusterID=-1
            continue
        else:
            cds=coords[labeledPoints==label]
            centroid=getCentroid(cds)
            point=Point(centroid[0],centroid[1])

            newDF=gpd.GeoDataFrame({'geometry':[point],'clusterID':[label],'nPoints':[len(cds)]},crs="EPSG:3857")
            clustersDf=pd.concat([clustersDf,newDF])
            

    points['clusterID']=labeledPoints.tolist()
    clustersDf=reorderDataframeIndex(clustersDf)
    return points,clustersDf

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

def main1(type):
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

def main2():
    bbox=(-9.50152,38.84014,-9.06988,38.67876)
    bbox1=(-1057675,4675615,-1009567,4698915) #LX swag
    crs="EPSG:3857"
    #crs1="EPSG:4326"
    epsilon=700
    minPoints=3

    waterFileDir="../Dados/BaseLayer/water.shp"
    roadsFileDir="../Dados/BaseLayer/roads.shp"
    poisFileDir="./datasets/facebookPOIS/pois/pois.shp"
    
    #ax=plotBaseMap(roadsFileDir,waterFileDir,bbox,bbox1)
    #plt.show()

    pois=readGeodatafromFile(poisFileDir,bbox1,crs)

    categories=['Lazer','Industria','Educacao','Saude','Turismo','Comercio','Servicos']
    for cat in categories:
        pointsFileDir="./datasets/facebookPOIS/pois/{}.shp".format(cat)
        newPointsFileDir="./datasets/facebookPOIS/clusters/{}.shp".format(cat)
        clustersFileDir="./datasets/facebookPOIS/clusters/clusters{}.shp".format(cat)

        points=readGeodatafromFile(pointsFileDir,bbox1,crs)
        newPoints,clusters=clusterGeoDataframe(points, epsilon, minPoints)
        writeGeodataToGis(newPoints, newPointsFileDir)
        writeGeodataToGis(clusters, clustersFileDir)
        print("{} {} {} {}".format(cat,len(points),len(newPoints),len(clusters)))

if __name__=='__main__':
    main2()
    
        

    


