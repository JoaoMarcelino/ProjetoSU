import geopandas as gpd
import pandas as pd
import shapely
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
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

def main():
    bbox=(-9.50152,38.84014,-9.06988,38.67876)
    bbox1=(-1057675,4675615,-1009567,4698915) #LX swag
    crs="EPSG:3857"
    #crs1="EPSG:4326"
    poiBuffer=200 #meters
    
    waterFileDir="../Dados/BaseLayer/water.shp"
    roadsFileDir="../Dados/BaseLayer/roads.shp"
    buildingsDir="./datasets/buildings/CartografiaBase.shp"
    newBuildingsDir="./datasets/buildings/zoneamento.shp"
    categories=['Lazer','Industria','Educacao','Saude','Turismo','Comercio','Servicos']

    print("Loading buildings dataset: ",end="")
    buildings=readGeodatafromFile(buildingsDir,bbox=bbox,crs=crs)
    bbox1=list(buildings.total_bounds)
    print(bbox1)
    allPoints={}
    for cat in categories:
            catDir="./datasets/facebookPOIS/clusters/{}.shp".format(cat)
            points=readGeodatafromFile(catDir,bbox=bbox1,crs=crs)
            allPoints[cat]=points
    print("Done")
    
    #ax=plotBaseMap(roadsFileDir,waterFileDir,bbox,bbox1,crs=crs)
    #buildings.plot(ax=ax, color='coral', edgecolor='coral',alpha=0.6)
    #plt.show()

    newBuildings=gpd.GeoDataFrame({'geometry':[],'category':[]},crs=crs)

    for i in tqdm(range(len(buildings))):
        poly=buildings.loc[i,'geometry']
        for cat in categories:
            pois=allPoints[cat]
            pois=pois.loc[pois['clusterID']!=-1]
            pois=reorderDataframeIndex(pois)
            for k in range(len(pois)):
                poi=pois.loc[k,'geometry'].buffer(poiBuffer)
                if poi.intersects(poly):
                    newEntry=gpd.GeoDataFrame({'geometry':[poly],'category':[cat]},crs=crs)
                    newBuildings=pd.concat([newBuildings,newEntry])
                    break

    writeGeodataToGis(newBuildings, newBuildingsDir,crs=crs)

if __name__=='__main__':
    main()
    

