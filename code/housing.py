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
    file_square = f"./datasets/zoning/predominantCategory.shp"
    price_file = f"./datasets/housing/prices_normalized1.shp"

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


def correlation_file():
    #Get housing values
    price_file = f"./datasets/housing/prices_normalized.shp"
    houses = readGeodatafromFile(price_file)

    #Get score values
    score1_file = f"./datasets/acessibility/score1.shp"
    score2_file = f"./datasets/acessibility/score2.shp"
    score3_file = f"./datasets/acessibility/score3.shp"
    score4_file = f"./datasets/acessibility/score4.shp"
    score1 = readGeodatafromFile(score1_file)
    score2 = readGeodatafromFile(score2_file)
    score3 = readGeodatafromFile(score3_file)
    score4 = readGeodatafromFile(score4_file)

    final_file = f"./datasets/housing/correlation_score.shp"

    types = ['Lazer', 'Industria', 'Educacao', 'Saude', 'Turismo', 'Comercio', 'Servicos']

    final_squares = gpd.GeoDataFrame({}, crs="EPSG:3857")

    #percorrer as casas
    for i in range(len(houses.geometry)):

        if houses.price[i] > 0:

            new_house = {}
            for j in range(len(score1.geometry)):

                
                zone = score1.geometry[j]
                centroid = houses.geometry[i].centroid
                #if centroid in zone
                if zone.contains(centroid):
                    

                    new_house['price'] = [houses.price[i]]
                    new_house['num_houses'] = [houses.num_houses[i]]
                    new_house['geometry'] = [houses.geometry[i]]
                    new_house['score1'] = [score1.score[j]]
                    new_house['score2'] = [score2.score[j]]
                    new_house['score3'] = [score3.score[j]]
                    new_house['score4'] = [score4.score[j]]


                    squareRow = gpd.GeoDataFrame(new_house, crs="EPSG:3857")
                    final_squares = pd.concat([final_squares, squareRow])
                    break

    writeGeodataToGis(final_squares, final_file)

def correlation():

    correlation_file = f"./datasets/housing/correlation_score.shp"
    house = readGeodatafromFile(correlation_file)
    plt.figure()
    plt.title("Correlation between Airbnb prices and Score 1")
    plt.scatter(house.price, house.score1)
    plt.xlabel("Airbnb Price")
    plt.ylabel("Score")
    plt.show()

    plt.figure()
    plt.title("Correlation between Airbnb prices and Score 2")
    plt.scatter(house.price, house.score2)
    plt.xlabel("Airbnb Price")
    plt.ylabel("Score")
    plt.show()

    plt.figure()
    plt.title("Correlation between Airbnb prices and Score 3")
    plt.scatter(house.price, house.score3)
    plt.xlabel("Airbnb Price")
    plt.ylabel("Score")
    plt.show()

    plt.figure()
    plt.title("Correlation between Airbnb prices and Score 4")
    plt.scatter(house.price, house.score4)
    plt.xlabel("Airbnb Price")
    plt.ylabel("Score")
    plt.show()




if __name__ == "__main__":
    #normalizeData()
    #getPrice()
    #correlation_file()
    correlation()

