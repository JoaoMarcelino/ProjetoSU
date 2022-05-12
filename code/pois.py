import geopandas as gpd
import matplotlib.pyplot as plt
import os
from sklearn.cluster import DBSCAN,AgglomerativeClustering,KMeans
from shapely.geometry import *
from utils import *


#dataframe:   dataframe
#taxonomy:  function that returns dictionary ex.: {'class1':['subclass1','subclass2'],'class2':['subclass1']}
#splitedDf:   dictionary of dataframes dataframe
def splitDataframByTaxonomy(geodf,taxonomy,categoryCol):

    splitedDf={}
    for category in taxonomy().keys():
        subcategories=taxonomy()[category]
        entries=geodf.loc[geodf[categoryCol].isin(subcategories)].copy()
        splitedDf[category]=entries

    return splitedDf

def buidTaxonomy(categories,subcategories):
    dicti={}
    for subcategory in subcategories:
        number=input("{}:".format(subcategory))
        number=int(number)
        if number==-1:
            continue
        else:
            category=categories[number]
            dicti[category]=dicti.get(category,[])+[subcategory]
    return dicti

def main1():
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

def main2():

    bbox=(-9.50152,38.84014,-9.06988,38.67876)
    bbox1=(-1057675,4675615,-1009567,4698915) #LX swag
    crs="EPSG:3857"
    #crs1="EPSG:4326"

    waterFileDir="../Dados/BaseLayer/water.shp"
    roadsFileDir="../Dados/BaseLayer/roads.shp"
    poisFileDir="./datasets/facebookPOIS/pois/pois.shp"

    pois=readGeodatafromFile(poisFileDir,bbox1,crs)
    """
    ax=plotBaseMap(roadsFileDir, waterFileDir, bbox, bbox1,crs)
    pois.plot(ax=ax, marker='.', markersize=20,color="#e8718d",alpha=0.6,label='Point of Interest')
    plt.legend()
    plt.show()

      
    subcategories=getUniqueValuesColumn(pois, "macro_cate")
    print(subcategories)
    
    categories=["Lazer","Educacao","Saude","Comercio","Industria/Empresas","Utilitarios/Servicos","Turismo"]
    taxonomy=buidTaxonomy(categories, subcategories)
    print(taxonomy)
       """
    categories=taxonomy1()
    print(categories)
   
    splittedPOIS=splitDataframByTaxonomy(pois, taxonomy1, "macro_cate")
    for cat in categories:
        geodf=splittedPOIS[cat]
        fileDir="./datasets/facebookPOIS/pois/{}.shp".format(cat)
        print("{}: {}".format(cat,len(geodf)))
        writeGeodataToGis(geodf, fileDir)
    
if __name__=='__main__':
    main2()
    
        

    


