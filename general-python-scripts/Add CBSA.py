# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 16:04:27 2017

@author: Michael Silva
"""

from sqlalchemy import create_engine
from sqlalchemy import text
import csv

# Connect to CGR's Data Hub
engine = create_engine('mysql+pymysql://user:password@server/database')
conn = engine.connect()

# Read the BEA's Metropolitan list
with open('metrolist.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        try:
            print('Linking '+row['county_name']+' to '+row['name'])
            conn.execute(text("UPDATE CGR_GEOGRAPHY_INDEX SET WITHIN_CBSA = '"+row['fips']+"' WHERE CGR_GEO_ID = '"+row['county_fips']+"'"))
            print('Linking '+row['county_name']+' locations to '+row['name'])
            conn.execute(text("UPDATE CGR_GEOGRAPHY_INDEX SET WITHIN_CBSA = '"+row['fips']+"' WHERE WITHIN_COUNTY = '"+row['county_fips']+"'"))
        except:
            continue

# Read the BEA's Micropolitan list
with open('microlist.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        try:
            print('Linking '+row['county_name']+' to '+row['name'])
            conn.execute(text("UPDATE CGR_GEOGRAPHY_INDEX SET WITHIN_CBSA = '"+row['fips']+"' WHERE CGR_GEO_ID = '"+row['county_fips']+"'"))
            print('Linking '+row['county_name']+' locations to '+row['name'])
            conn.execute(text("UPDATE CGR_GEOGRAPHY_INDEX SET WITHIN_CBSA = '"+row['fips']+"' WHERE WITHIN_COUNTY = '"+row['county_fips']+"'"))
        except:
            continue

conn.close()
