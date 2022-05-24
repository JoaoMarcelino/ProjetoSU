import base64
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pip import main
from shapely.geometry import *
from shapely.ops import nearest_points
import config
import requests
import urllib
import json
import base64
from pyproj import Proj, transform

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

def deleteColumns(df,columns):
    return df.drop(columns=columns)

def getUniqueValuesColumn(df,columnName):
    values=[]
    for i in range(len(df)):
        value=df.loc[i,columnName]
        if value not in values:
            values.append(value)

    return values

def getCentroid(cluster): 
    centroid = [MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y]
    return centroid


def taxonomy():
    dicti={ 'Lazer': [ 'Sports & Recreation', 'Sports Club', 'Country Club / Clubhouse', 'Social Club', 'Performance Art', 'Art'], 
            'Industria': ['Media/News Company', 'Commercial & Industrial'], 
            'Educacao': ['Education','Campus Building'],
            'Saude': ['Medical & Health'],
            'Turismo': ['Landmark & Historical Place', 'Hotel & Lodging'],
            'Comercio': ['Food & Beverage', 'Shopping & Retail', 'Beauty, Cosmetic & Personal Care'], 
            'Servicos': ['Local Service', 'Public & Government Service']
            }
    return dicti

def getNearestGeometry(point, gdf, value_column="geometry"):
    """Find the nearest point and return the corresponding value from specified value column."""
    # Create an union of the other GeoDataFrame's geometries:
    other_points = gdf["geometry"].unary_union
    # Find the nearest points
    nearest_geoms = nearest_points(point, other_points)

    return gdf.loc[gdf['geometry']==nearest_geoms[1]]

def getNNearestPoints(point,gdf,n):
    visited=[]
    geomVisited=[]
    for i in range(n):
        gdf=gdf.loc[~gdf['geometry'].isin(geomVisited)]
        nearestGeom=getNearestGeometry(point, gdf)
        visited.append(nearestGeom)
        geomVisited.append(nearestGeom.iloc[0]['geometry'])
    return visited
    
def getUsualBbox():
    bboxDegrees=(-9.50152,38.84014,-9.06988,38.67876)
    bboxEuclidean=(-1057675,4675615,-1009567,4698915) #LX swag
    
    return bboxEuclidean,bboxDegrees

def getUsualCRS():
    crsEuclidean="EPSG:3857"
    crsDegrees="EPSG:4326"

    return crsEuclidean,crsDegrees


def getSquaresFromBounds(boundsList,squareWidth,crs):
    dicti={"geometry":[]}

    for bbox in boundsList:
        x=bbox[0]
        while x<bbox[2]:
            y=bbox[1]
            while y<bbox[3]:
                square=Polygon([(x,y),(x+squareWidth,y),(x+squareWidth,y+squareWidth),(x,y+squareWidth)])
                dicti['geometry']=dicti.get('geometry',[])+[square]
                y+=squareWidth
            x+=squareWidth
    return gpd.GeoDataFrame(data=dicti,crs=crs)

def getPointsFromGridSearch(bbox,distanceIncrement,crs):
    dicti={"geometry":[]}

    x=bbox[0]
    while x<bbox[2]:
        y=bbox[1]
        while y<bbox[3]:
            square=Polygon([(x,y),(x+distanceIncrement,y),(x+distanceIncrement,y+distanceIncrement),(x,y+distanceIncrement)])
            dicti['geometry']=dicti.get('geometry',[])+[square]
            y+=distanceIncrement
        x+=distanceIncrement
    return gpd.GeoDataFrame(data=dicti,crs=crs)


def getKeyFromFile(keyDir):
    f=open(keyDir,'r')
    key=f.readlines()[0]
    key=key.strip("\n")
    return key

def getRoute(googleClient,pointA,pointB,mode='driving'):
    result = googleClient.distance_matrix(pointA, pointB, mode=mode)
    distance=result['rows'][0]['elements'][0]['distance']['value']
    time=result['rows'][0]['elements'][0]['duration']['value']
    return distance,time


def loadClusters(folderDir,crs,categories):
    clusters={}
    pois={}
    for cat in categories:
        clusters[cat]=readGeodatafromFile("{}clusters{}.shp".format(folderDir,cat),crs=crs)
        pois[cat]=readGeodatafromFile("{}{}.shp".format(folderDir,cat),crs=crs)

    return pois,clusters

def getCellWithValue(geoDataFrame,columnOfValue,value,columnToSelect):
    value=geoDataFrame.loc[geoDataFrame[columnOfValue]==value,columnToSelect].tolist()[0]
    return value


class bbox:
    def __init__(self,north,south,east,west):
        self.north=north
        self.south=south
        self.east=east
        self.west=west

    def convertToXY(self):
        inProj  = Proj("EPSG:4326")
        outProj = Proj("EPSG:3857")
        pointA=transform(inProj,outProj,self.north,self.west)
        pointB=transform(inProj,outProj,self.south,self.east)
        print((pointA[1],pointB[1],pointA[0],pointB[0]))
        return bbox(pointA[1],pointB[1],pointA[0],pointB[0])

def convertPointToDegrees(point):
    outProj  = Proj("EPSG:4326")
    inProj = Proj("EPSG:3857")
    pointB=transform(inProj,outProj,point[0],point[1])
    return pointB[1],pointB[0]


def auth_idealista():

    url = "https://api.idealista.com/oauth/token"    
    apikey= config.API_KEY #sent by idealista
    secret= config.API_SECRET #sent by idealista

    message = apikey + ":" + secret
    auth = "Basic " + base64.b64encode(message.encode("ascii")).decode("ascii")

    headers_dic = {"Authorization" : auth, 
                "Content-Type" : "application/x-www-form-urlencoded;charset=UTF-8"}

    params_dic = {"grant_type" : "client_credentials",
                "scope" : "read"}

    response = requests.post("https://api.idealista.com/oauth/token", 
                    headers = headers_dic, 
                    params = params_dic)
    response = json.loads(response.text)
    access_token = response["access_token"]

    return access_token

def get_houses_idealista(token, url):
    
    headers = {'Content-Type': 'Content-Type: multipart/form-data;', 'Authorization' : 'Bearer ' + token}
    content = requests.post(url, headers = headers)
    print(content)
    result = json.loads(content.text)
    return result

def search_houses_idealista(at, center, distance, iterations):

    idealista_file='./datasets/housing/idealista.shp'

    country = 'pt' #values: es, it, pt
    locale = 'pt' #values: es, it, pt, en, ca
    language = 'pt' #
    max_items = '50'
    operation = 'sale' 
    property_type = 'homes'
    order = 'priceDown' 
    sort = 'desc'
    bankOffer = 'false'

    center = f"{center[0]},{center[1]}"

    df_tot = gpd.GeoDataFrame()

    for i in range(1,iterations):
        url = ('https://api.idealista.com/3.5/'+country+'/search?operation='+operation+#"&locale="+locale+
            '&maxItems='+max_items+
            '&order='+order+
            '&center='+center+
            '&distance='+distance+
            '&propertyType='+property_type+
            '&sort='+sort+ 
            '&numPage=%s'+
            '&language='+language) %(i)  
        a = get_houses_idealista(at, url)
        #print(len(a['elementList']))

        for i, house in enumerate(a['elementList']):
            lat = house['latitude']
            lon = house['longitude']
            
            house.pop('parkingSpace', None)
            house.pop('detailedType', None)
            house.pop('labels', None)

            house['geometry'] = Point(lon, lat)

            df = gpd.GeoDataFrame(house, crs="EPSG:3857")
            df_tot = pd.concat([df_tot,df])

    #print(df_tot)
    writeGeodataToGis(df_tot, idealista_file)
    df_tot = df_tot.reset_index()


if __name__ == "__main__":
    at = auth_idealista()
    print(at)
    Lisbon= np.array([38.8076, 38.6952, -9.0929, -9.2694])
    center= (np.average(Lisbon[0:2]),np.average(Lisbon[2:4]))
    distance = '30000'
    search_houses_idealista(at, center, distance, 20)