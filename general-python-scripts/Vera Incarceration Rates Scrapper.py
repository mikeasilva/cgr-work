# -*- coding: utf-8 -*-
"""Vera Institute of Justice Incarceration Rates Scrapper.
Created on Thu Nov  9 09:05:13 2017

@author: Michael Silva
"""

import requests
from sqlalchemy import create_engine
import pandas as pd

# This will hold the data
data = list()

# Connect to the data hub
engine = create_engine('mysql+pymysql://user:password@server/db')
conn = engine.connect()

# Get county level data
q = conn.execute("SELECT *  FROM `CGR_GeographyIndex` WHERE `TYPE` = 'County'").fetchall()

for row in q:
    i = int(row[0]) # This is the FIPS Code
    print('Trying to get data for '+row[1]) # This prints the name
    try:
        response = requests.get('http://trends.vera.org/data/county/'+str(i))
        j = response.json()
        fips = j['fips']
        name = j['name']
        yearly_data = dict()
        for key in j['yearlyData']:
            for year in j['yearlyData'][key]:
                yearly_data[year] = yearly_data.get(year, dict())
                yearly_data[year]['Name'] = name
                yearly_data[year]['FIPS'] = fips
                yearly_data[year][key] = j['yearlyData'][key][year]
                
        for year in yearly_data:
            row = yearly_data[year]
            row['year'] = int(year)
            row =  {k.lower(): v for k, v in row.items()}
            data.append(row)
    except: continue
        
# Get the state level data
q = conn.execute("SELECT *  FROM `CGR_GeographyIndex` WHERE `TYPE` = 'State'").fetchall()

for row in q:
    i = int(row[0]) # This is the FIPS Code
    print('Trying to get data for '+row[1]) # This prints the name
    try:
        response = requests.get('http://trends.vera.org/data/state/'+str(i))
        j = response.json()
        fips = j['fips']
        name = row[1]
        yearly_data = dict()
        for key in j['yearlyData']:
            for year in j['yearlyData'][key]:
                yearly_data[year] = yearly_data.get(year, dict())
                yearly_data[year]['Name'] = name
                yearly_data[year]['FIPS'] = fips
                yearly_data[year][key] = j['yearlyData'][key][year]
                
        for year in yearly_data:
            row = yearly_data[year]
            row['year'] = int(year)
            row =  {k.lower(): v for k, v in row.items()}
            data.append(row)
    except: continue
        
    
# Save data a spreadsheet
df = pd.DataFrame.from_records(data)
print('Saving spreadsheet')
writer = pd.ExcelWriter('Vera Incarceration Rates.xlsx')
df.to_excel(writer, 'US_IncarcerationRates_Vera', index=False)
writer.save()

print('Saving to data hub')
df.to_sql(name='US_IncarcerationRates_Vera_UPDATE', con=engine, 
            if_exists = 'replace', index=False)
