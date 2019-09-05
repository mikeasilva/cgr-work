# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 08:09:44 2019

@author: Michael
"""

import csv
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def shp_to_geoseries(file, key):
    d = {}
    temp = gpd.read_file(file)
    for i in temp.index:
        d[temp.loc[i][key]] = temp.loc[i]["geometry"]
    return gpd.GeoSeries(d)


def first_or_none(l):
    if len(l) == 0:
        return None
    return l[0]

mcleg = shp_to_geoseries("MCLEG_WGS84.shp", "MCLEGDIST")
greece = shp_to_geoseries("GreeceWard_WGS84.shp", "CITCOD")
tract = shp_to_geoseries("Tracts_WGS84.shp", "GEOID10")
temp = gpd.read_file("Tracts_WGS84.shp")
tract_name = dict(zip(list(temp["GEOID10"]), list(temp["NAMELSAD10"])))

data = []

for row in csv.DictReader(open("../MCVoters.csv")):
    row = dict(row)
    try:
        point = Point(float(row["POINT_X"]), float(row["POINT_Y"]))
    except:
        # Some rows don't have coordinates so give them something
        point = Point(0, 0)
    row["MCLEG"] = first_or_none([key for key, polygon in mcleg.items() if point.within(polygon)])
    row["TRACT"] = t = first_or_none([key for key, polygon in tract.items() if point.within(polygon)])
    row["TRACT_NAME"] = tract_name.get(t, None)
    row["GREECE"] = first_or_none([key for key, polygon in greece.items() if point.within(polygon)])
    data.append(row)
    
df = pd.DataFrame(data)

df.to_csv("../MCVotersNew.csv")