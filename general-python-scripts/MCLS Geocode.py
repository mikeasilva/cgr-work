# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 11:39:14 2016

@author: Michael Silva

Use the NYS GIS Geocoder to geocode
"""

import requests
import sqlite3
from pyproj import Proj, transform

in_proj = Proj(init='epsg:26918') # NAD83 North American Datum 1983
out_proj = Proj(init='epsg:4326') # WGS84 World Geodetic System

service_url = 'http://gisservices.dhses.ny.gov/arcgis/rest/services/Locators/Street_and_Address_Composite/GeocodeServer/findAddressCandidates'

conn = sqlite3.connect('2012_MCLS.sqlite')
cur = conn.cursor()
result = cur.execute('SELECT DISTINCT STREET1, CITY1, clean_zip, lat, lng FROM patrons WHERE lat IS NULL')
rows = result.fetchall()
address_not_found = 0
i = 0
for row in rows:
    i = i+1
    progress = str(i)+' of '+str(len(rows))+': '
    address_to_geocode = row[0]+', '+row[1]+' NY  '+row[2]
    # Skip the rows that are geocoded
    if row[3]!= None: 
        print(progress+'Already geocoded '+address_to_geocode)
        continue
    payload = {'Street':row[0], 'City':row[1], 'State':'NY', 'ZIP':row[2], 'f':'pjson'}
    r = requests.get(service_url, params=payload)
    
    try:
        lat = r.json()['candidates'][0]['location']['y']
        lng = r.json()['candidates'][0]['location']['x']
        
        lng,lat = transform(in_proj,out_proj,lng,lat)
        print(progress+'Saving data '+address_to_geocode)
        sql = 'UPDATE patrons SET lat=:lat, lng=:lng WHERE STREET1=:street AND CITY1=:city AND clean_zip=:zip'
        cur.execute(sql, {'lat':lat, 'lng':lng, 'street':row[0], 'city':row[1], 'zip':row[2]})
        conn.commit()
    except:
        address_not_found = address_not_found + 1
        print(progress+'Address not found '+address_to_geocode)

conn.close()
print('There were '+str(address_not_found)+' addresses not found')