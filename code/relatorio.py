import geopandas as gpd
import shapely
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

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

def plotBaseMap():
    #roadsFile="C:/Users/franc/Desktop/SU/Tutoriais/portugal/roads.shp"
    #waterFile="C:/Users/franc/Desktop/SU/Tutoriais/portugal/water.shp"
    roadsFile="../DS01 QGISintro/portugal/roads.shp"
    waterFile="../DS01 QGISintro/portugal/water.shp"
    bbox = (-8.44896,40.17894,-8.38804,40.22520)
    bbox1=(-942000.6,4891166.6,-933027.4,4900545.5)
    crs="EPSG:3857"
    #crs="EPSG:4326"
    roads = readGeodatafromFile(roadsFile,bbox,crs)
    water=readGeodatafromFile(waterFile,bbox,crs)

    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    base=roads.plot(ax=ax,color='purple', edgecolor='purple',alpha=0.2)
    water.plot(ax=ax,color='yellowgreen', edgecolor='yellowgreen',alpha=0.2)
    ax.set_xlim(bbox1[0],bbox1[2])
    ax.set_ylim(bbox1[1],bbox1[3])
    return ax


def score():


    bbox = (-8.44896,40.17894,-8.38804,40.22520)
    bbox1=(-942000.6,4891166.6,-933027.4,4900545.5)
    crs="EPSG:3857"

    score2 = "./datasets/buildings/score/score2/"
    score = "./datasets/buildings/score/score/"

    path = "./datasets/pois/"
    rest = "/final/clustersDBSCAN400.shp"
    types =  ["comercio", "educacao", "infraestrutura", "lazer", "saude"]

    axis=plotBaseMap()

    comercio = readGeodatafromFile(score2 + "comercio.shp",bbox1,crs)
    infraestrutura = readGeodatafromFile(score2 + "infraestrutura.shp",bbox1,crs)
    educacao = readGeodatafromFile(score2 + "educacao.shp",bbox1,crs)
    lazer = readGeodatafromFile(score2 + "lazer.shp",bbox1,crs)
    saude = readGeodatafromFile(score2 + "saude.shp",bbox1,crs)

    comercio.plot(ax=axis, color='green',label="Commerce",alpha=0.6)
    infraestrutura.plot(ax=axis, color='red', label="Infraestructure",alpha=0.6)
    educacao.plot(ax=axis, color='blue', label="Education",alpha=0.6 )
    lazer.plot(ax=axis, color='yellow', label="Leisure" ,alpha=0.6)
    saude.plot(ax=axis, color='purple', label="Health" ,alpha=0.6)

    comercio = readGeodatafromFile(path + "comercio" + rest,bbox1,crs)
    infraestrutura = readGeodatafromFile(path + "infraestrutura" + rest,bbox1,crs)
    educacao = readGeodatafromFile(path + "educacao" + rest,bbox1,crs)
    lazer = readGeodatafromFile(path + "lazer" + rest,bbox1,crs)
    saude = readGeodatafromFile(path + "saude" + rest,bbox1,crs)

    comercio.plot(ax=axis,marker='.', color='green', markersize=70, label="Commerce" ,alpha=1)
    infraestrutura.plot(ax=axis,marker='.', color='red', markersize=70, label="Infraestructure" ,alpha=1)
    educacao.plot(ax=axis,marker='.', color='blue', markersize=70,label="Education" ,alpha=1)
    lazer.plot(ax=axis,marker='.', color='yellow', markersize=70,label="Leisure" ,alpha=1)
    saude.plot(ax=axis,marker='.', color='purple', markersize=70,label="Health",alpha=1)

    plt.legend(loc="upper right")
    plt.show()

def main():
    poisFile="./datasets/pois/pois.shp"
    poisComercioFile="./datasets/pois/comercio/points/points.shp"
    clustersFile="./datasets/pois/testesClustering/DBSCAN400.shp"
    centroidsFile="./datasets/pois/testesClustering/clustersDBSCAN400.shp"
    bbox = (-8.44896,40.17894,-8.38804,40.22520)
    bbox1=(-942000.6,4891166.6,-933027.4,4900545.5)
    crs="EPSG:3857"
    #crs="EPSG:4326"

    pois=readGeodatafromFile(poisFile,bbox,crs)
    poisComercio=readGeodatafromFile(poisComercioFile,bbox,crs)
    poisClusters=readGeodatafromFile(clustersFile,bbox1,crs)
    clusters=readGeodatafromFile(centroidsFile,bbox1,crs)

    test1=readGeodatafromFile("./datasets/pois/testesClustering/points4.shp",bbox1,crs)
    test1Clusters=readGeodatafromFile("./datasets/pois/testesClustering/clusters4.shp",bbox1,crs)
    
    test2=readGeodatafromFile("./datasets/pois/testesClustering/points2.shp",bbox1,crs)
    test2Clusters=readGeodatafromFile("./datasets/pois/testesClustering/clusters2.shp",bbox1,crs)

    test3=readGeodatafromFile("./datasets/pois/testesClustering/points3.shp",bbox1,crs)
    test3Clusters=readGeodatafromFile("./datasets/pois/testesClustering/clusters3.shp",bbox1,crs)
    """
    axis=plotBaseMap()
    pois.plot(ax=axis,marker='.', color='green', markersize=70,label="POI")
    plt.legend()
    plt.show()

    axis=plotBaseMap()
    poisComercio.plot(ax=axis,marker='.', color='green', markersize=70,label="Commerce POI")
    plt.legend()
    plt.show()
    
    
    axis=plotBaseMap()
    poisClusters.plot(column='clusterID', ax=axis, marker='.', markersize=70, cmap='Set1')
    clusters.plot(ax=axis, marker="*", markersize=150,color="Black")
    plt.show()

    axis=plotBaseMap()
    poisClusters.plot(column='clusterID', ax=axis, marker='.', markersize=70, cmap='Set1',label='Point of Interest')
    clusters.plot(ax=axis, marker="*", markersize=150,color="Black",label='Centroid')
    plt.legend()
    plt.show()
    
    axis=plotBaseMap()
    test1.plot(column='clusterID', ax=axis, marker='.', markersize=70, cmap='Set1',label='Point of Interest')
    test1Clusters.plot(ax=axis, marker="*", markersize=150,color="Black",label='Centroid')
    plt.legend()
    plt.show()
    
    axis=plotBaseMap()
    test2.plot(column='clusterID', ax=axis, marker='.', markersize=70, cmap='Set1',label='Point of Interest')
    test2Clusters.plot(ax=axis, marker="*", markersize=150,color="Black",label='Centroid')
    plt.legend()
    plt.show()

    axis=plotBaseMap()
    test3.plot(column='clusterID', ax=axis, marker='.', markersize=70, cmap='Set1',label='Point of Interest')
    test3Clusters.plot(ax=axis, marker="*", markersize=150,color="Black",label='Centroid')
    plt.legend()
    plt.show()
    
    classes=["comercio","educacao","infraestrutura","lazer","saude"]
    for name in classes:
        data=readGeodatafromFile("./datasets/pois/{}/points/points.shp".format(name),bbox,crs)
        print("{} {}".format(name,len(data)))
    

    buildings=readGeodatafromFile("./datasets/buildings/Coimbra/comercio/comercio.shp",bbox1,crs)
    axis=plotBaseMap()
    buildings.plot(ax=axis, color='coral', edgecolor='coral',alpha=0.5,legend=True,label='Commerce Zone Building')
    clusters.plot(ax=axis, marker="*", markersize=150,color="Black",label='Centroid')
    LegendElement = [
        mlines.Line2D([], [], color='black', marker='*', linestyle='None',markersize=10, label='Centroid'),
        mpatches.Patch(facecolor='coral', edgecolor='coral', label='Commerce Zone Building')]
    axis.legend(handles = LegendElement, loc='upper right')
    plt.show()
    

    stops=readGeodatafromFile("./datasets/bus/stops.shp",bbox,crs)
    axis=plotBaseMap()
    stops.plot(ax=axis,marker="^", color='blue', edgecolor='blue',label='Bus Stop',markersize=10)
    plt.legend()
    plt.show()
    
    print(len(stops))
    """
    travelTimes=readGeodatafromFile("./datasets/buildings/travelTimes/buildings.shp",bbox1,crs)
    travelTimes=travelTimes.loc[travelTimes['time']<10]
    axis=plotBaseMap()
    travelTimes.plot(column='time', ax=axis, cmap='afmhot',legend=True,alpha=0.6)
    plt.legend()
    plt.show()

if __name__=="__main__":
    score()
