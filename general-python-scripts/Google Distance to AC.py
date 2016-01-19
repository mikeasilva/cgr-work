# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 09:36:02 2016

@author: Michael
"""
import requests
from pandas import ExcelWriter
import pandas as pd

api_key = 'ENTER API KEY HERE'
use_lat_lng = True

# Holds the results
distance_text = list()
distance_value = list()
duration_text = list()
duration_value = list()
lat_list = list()
lng_list = list()
fips = list()

# Read in the 2010 Geography Headers
df_2010 = pd.read_csv('DEC_10_SF1_G001_with_ann.csv')
df_2010 = df_2010.ix[1:]
df_2010 = df_2010[['GEO.id2', 'GEO.display-label', 'VD074','VD075']]
df_2010.columns = ['fips', 'label', 'lat','lng']

# Iterate through the data frame
for index, row in df_2010.iterrows():
    lat = row['lat']
    lng = row['lng']
    if use_lat_lng:
        origin = lat+','+lng
    else:
        origin = row['label'].replace(' ','+')
    api_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins='+origin+'&destinations=Atlantic+City+NJ&units=imperial&key='+api_key
    r = requests.get(api_url)
    show_error = True
    if r.status_code == requests.codes.ok:
        data = r.json()
        try:
            data = data['rows'][0]['elements'][0]
            distance = data['distance']
            duration = data['duration']
            # Append the results     
            distance_text.append(distance['text'])
            distance_value.append(distance['value'])
            duration_text.append(duration['text'])
            duration_value.append(duration['value'])
            lat_list.append(lat)
            lng_list.append(lng)
            fips.append(row['fips'])
            show_error = False
        except:
            pass
    if show_error:
        print('ERROR: No data for '+row['label']+'.')
    else:
        print('Got data for '+row['label']+'.')

# Create a dataframe
raw_data = {'fips':fips, 'lat':lat_list, 'lng':lng_list, 'distance_text':distance_text, 'distance':distance_value, 'duration_text':duration_text, 'duration':duration_value}
df = pd.DataFrame(raw_data, columns = ['fips', 'lat', 'lng', 'distance_text', 'distance', 'duration_text','duration'])
# Write the output
writer = ExcelWriter('distance matrix.xlsx')
df.to_excel(writer,'Sheet1')
writer.save()