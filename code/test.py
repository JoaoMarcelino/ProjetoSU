import numpy as np
import pandas as pd
import geopandas as gpd
import scipy
import shapely
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from shapely.geometry import MultiPoint,Point,Polygon,MultiPoint,MultiPolygon
from shapely.ops import nearest_points

from travelTimes import getBuildings
from pois import main2
from score import getScore


def main():
    squares = ["comercio", "educacao", "infraestrutura", "lazer", "saude"]
    house = Point(-937781.5,4894487.3)
    
    for type in squares:
        getBuildings(type)

    
    getScore(house)


if __name__ == "__main__":
    main()