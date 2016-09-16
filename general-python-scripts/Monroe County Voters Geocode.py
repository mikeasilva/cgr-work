# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 08:21:52 2016

@author: Michael
"""

import csv, sqlite3
import re
import requests
from pyproj import Proj, transform

in_proj = Proj(init='epsg:26918') # NAD83 North American Datum 1983
out_proj = Proj(init='epsg:4326') # WGS84 World Geodetic System

service_url = 'http://gisservices.dhses.ny.gov/arcgis/rest/services/Locators/Street_and_Address_Composite/GeocodeServer/findAddressCandidates'

# Set this flag if you want to create the database from scratch
create_db = False

con = sqlite3.connect('Monroe County Voters.sqlite')
cur = con.cursor()

if create_db:
    print('Creating fresh db')
    cur.execute('DROP TABLE `voters`;')
    cur.execute(""" CREATE TABLE `voters` (
	`LASTNAME`	TEXT,
	`FIRSTNAME`	TEXT,
	`MIDDLENAME`	TEXT,
	`NAMESUFFIX`	TEXT,
	`RADDNUMBER`	TEXT,
	`RHALFCODE`	TEXT,
	`RAPARTMENT`	TEXT,
	`RPREDIRECTION`	TEXT,
	`RSTREETNAME`	TEXT,
	`RPOSTDIRECTION`	TEXT,
	`RCITY`	TEXT,
	`RZIP5`	TEXT,
	`RZIP4`	TEXT,
	`MAILADD1`	TEXT,
	`MAILADD2`	TEXT,
	`MAILADD3`	TEXT,
	`MAILADD4`	TEXT,
	`DOB`	TEXT,
	`GENDER`	TEXT,
	`ENROLLMENT`	TEXT,
	`OTHERPARTY`	TEXT,
	`COUNTYCODE`	TEXT,
	`ED`	TEXT,
	`LD`	TEXT,
	`TOWNCITY`	TEXT,
	`WARD`	TEXT,
	`CD`	TEXT,
	`SD`	TEXT,
	`AD`	TEXT,
	`LASTVOTEDDATE`	TEXT,
	`PREVYEARVOTED`	TEXT,
	`PREVCOUNTY`	TEXT,
	`PREVADDRESS`	TEXT,
	`PREVNAME`	TEXT,
	`COUNTYVRNUMBER`	TEXT,
	`REGDATE`	TEXT,
	`VRSOURCE`	TEXT,
	`IDREQUIRED`	TEXT,
	`IDMET`	TEXT,
	`STATUS`	TEXT,
	`REASONCODE`	TEXT,
	`INACT_DATE`	TEXT,
	`PURGE_DATE`	TEXT,
	`SBOEID`	TEXT,
	`VoterHistory`	TEXT,
	`lat`	NUMERIC DEFAULT NULL,
	`lng`	NUMERIC DEFAULT NULL
);""")
    con.commit()
    
    print('Inserting data')
    reader = csv.reader(open('Monroe-County_04-28-2016.csv', encoding='utf-8'))
    for row in reader:
        cur.execute("INSERT INTO voters (LASTNAME, FIRSTNAME, MIDDLENAME, NAMESUFFIX, RADDNUMBER, RHALFCODE, RAPARTMENT, RPREDIRECTION, RSTREETNAME, RPOSTDIRECTION, RCITY, RZIP5, RZIP4, MAILADD1, MAILADD2, MAILADD3, MAILADD4, DOB, GENDER, ENROLLMENT, OTHERPARTY, COUNTYCODE, ED, LD, TOWNCITY, WARD, CD, SD, AD, LASTVOTEDDATE, PREVYEARVOTED, PREVCOUNTY, PREVADDRESS, PREVNAME, COUNTYVRNUMBER, REGDATE, VRSOURCE, IDREQUIRED, IDMET, STATUS, REASONCODE, INACT_DATE, PURGE_DATE, SBOEID, VoterHistory) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", row)
    con.commit()

print('Getting addresses to geocode')
result = cur.execute('SELECT DISTINCT RADDNUMBER, RHALFCODE, RPREDIRECTION, RSTREETNAME, RPOSTDIRECTION, RCITY, RZIP5, lat, lng FROM voters WHERE lat IS NULL')
rows = result.fetchall()
address_not_found = 0
i = 0
for row in rows:
    i = i+1
    progress = str(i)+' of '+str(len(rows))+': '
    # Build the address to geocode  
    address_to_geocode = row[0] + ' ' + row[1]  + ' ' + row[2] + ' ' + row[3] + ' ' + row[4] + ', ' + row[5] + ' NY' + ' ' + row[6]
    # Strip extra spaces 
    address_to_geocode = re.sub(' +',' ',address_to_geocode).replace(' ,',',')
    # Geocode the address
    payload = {'SingleLine': address_to_geocode, 'f':'pjson'}
    r = requests.get(service_url, params=payload)
    
    try:
        lat = r.json()['candidates'][0]['location']['y']
        lng = r.json()['candidates'][0]['location']['x']
        
        lng,lat = transform(in_proj,out_proj,lng,lat)
        print(progress+'Saving data '+address_to_geocode)
        sql = 'UPDATE voters SET lat=:lat, lng=:lng WHERE RADDNUMBER=:RADDNUMBER AND RHALFCODE=:RHALFCODE AND RPREDIRECTION=:RPREDIRECTION AND RSTREETNAME=:RSTREETNAME AND RPOSTDIRECTION=:RPOSTDIRECTION AND RCITY=:RCITY AND RZIP5=:RZIP5'
        cur.execute(sql, {'lat':lat, 'lng':lng, 'RADDNUMBER':row[0], 'RHALFCODE':row[1], 'RPREDIRECTION':row[2], 'RSTREETNAME':row[3], 'RPOSTDIRECTION':row[4], 'RCITY':row[5], 'RZIP5':row[6]})
        con.commit()
    except:
        address_not_found = address_not_found + 1
        print(progress+'Address not found '+address_to_geocode)
    
   
con.close()
print('There were '+str(address_not_found)+' addresses not found')