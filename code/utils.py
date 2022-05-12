import geopandas as gpd
import matplotlib.pyplot as plt
import os
from shapely.geometry import *
from shapely.ops import nearest_points

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

"""
#Old Taxonomy
def taxonomy():
    dicti={}
    dicti['infraestrutura']=['police','post_box','recycling','post_office','parking','telephone','post_office','fire_station','bank','fuel','information','toilet']
    dicti['saude']=['pharmacy','hospital']
    dicti['comercio']=['restaurant','cafe','pub','supermarket','fast_food','atm','bakery']
    dicti['educacao']=['school','library','kindergarten']
    dicti['lazer']=['theatre','museum','cinema','attraction','nightclub']

    return dicti
"""

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
    bbox=(-9.50152,38.84014,-9.06988,38.67876)
    bbox1=(-1057675,4675615,-1009567,4698915) #LX swag
    
    return bbox,bbox1

def getUsualCRS():
    crs="EPSG:3857"
    crs1="EPSG:4326"

    return crs,crs1


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
    result = gmaps.distance_matrix(pointA, pointB, mode=mode)
    distance=result['rows'][0]['elements'][0]['distance']['value']
    time=result['rows'][0]['elements'][0]['duration']['value']
    return distance,time