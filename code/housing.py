import json
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from shapely.geometry import *
from shapely.ops import nearest_points
from utils import writeGeodataToGis, readGeodatafromFile

def getPrice():

    file_houses = f"./datasets/housing/normalized.shp"
    file_square = f"./datasets/facebookPOIS/richPOIS/richPOIS.shp"
    price_file = f"./datasets/housing/prices_normalized.shp"

    squares = readGeodatafromFile(file_square)
    houses = readGeodatafromFile(file_houses)

    squaresDic = {}
    final_squares = gpd.GeoDataFrame(squaresDic, crs="EPSG:3857")

    #Percorrer Squares
    for i in range(len(squares.geometry)):
        #print(squares.geometry[i])
        square = squares.geometry[i]

        average_price = 0
        number_houses = 0
        dictionary = {}
        #Percorrer houses
        for j in range(len(houses.geometry)):

            house = houses.geometry[j]
            if square.contains(house):
                number_houses +=1 
                average_price += houses.price[i]

        if number_houses:
            average_price = average_price / number_houses
        dictionary['price'] = average_price
        dictionary['num_houses'] = number_houses
        dictionary['geometry'] = [square]

        squareRow = gpd.GeoDataFrame(dictionary, crs="EPSG:3857")
        final_squares = pd.concat([final_squares, squareRow])
    
    writeGeodataToGis(final_squares, price_file)

    return None


def normalizeData():

    price_file = f"./datasets/housing/airbnb.shp"
    normalized_file = f"./datasets/housing/normalized.shp"
    houses = readGeodatafromFile(price_file)

    average = np.average(houses.price)
    median = np.median(houses.price)
    print(average, median)

    plt.hist(houses.price)
    plt.show()

    print(len(houses))
    #remove outliers
    for i, price in enumerate(houses.price):
        if price == 0 or (price > 20 * average and price > 20 * median):
            print("passes here")
            houses = houses.drop([i])

    print(len(houses))
    #normalize_data
    max_value = np.max(houses.price)
    min_value = np.min(houses.price)

    average = np.average(houses.price)
    median = np.median(houses.price)

    print(average, median, max_value, min_value)

    for i, price in enumerate(houses.price): 
        if price != None:
            houses.price[i] = (price - min_value) / (max_value - min_value)

    average = np.average(houses.price)
    median = np.median(houses.price)

    print(average, median)
    plt.hist(houses.price)
    plt.show()
    
    writeGeodataToGis(houses, normalized_file)

if __name__ == "__main__":
    #normalizeData()
    getPrice()