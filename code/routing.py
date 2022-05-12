import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from utils import *

def main():
    bbox=(-9.50152,38.84014,-9.06988,38.67876)
    bbox1=(-1057675,4675615,-1009567,4698915) #LX swag
    gmaps = googlemaps.Client(key=getKeyFromFile("./keys.txt"))

    result = gmaps.distance_matrix((38.84014,-9.50152), (38.67876,-9.06988), mode='walking')
    print(result)

if __name__=="__main__":
    main()