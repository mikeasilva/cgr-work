# -*- coding: utf-8 -*-
"""Scrape the Feeding America Map API.
Created on Wed Nov  8 13:57:43 2017

@author: Michael Silva
"""

import requests
import pandas as pd
from sqlalchemy import create_engine

# This will hold the data scrapped from the API
scrapped_data = list()

for year in range(2013, 2016):
    url = "http://map.feedingamerica.org/api/v1/map/county."+str(year)+".overall.null.null.null?sideload[]=county&sideload[]=national&&sideload[]=states"
    response = requests.get(url)
    j = response.json()
    states = dict()
    for state in j['states']:
        print('Adding '+state['stateName']+' data for '+str(state['year']))
        states[state['id']] = state['stateName']
        scrapped_data.append(state)
    for county in j['counties']:
        name = county['countyName'] + ", "+states[county['state']]
        print('Adding '+name+' data for '+str(county['year']))
        scrapped_data.append(county)
    print('Adding National data for '+str(j['national'][0]['year']))
    # Add a fips code to the national data
    national_data = j['national'][0]
    national_data['fips'] = '0'
    scrapped_data.append(national_data) 

    
# Saving data to Data Hub
print('Saving data to hub...')
df = pd.DataFrame.from_records(scrapped_data)
engine = create_engine('mysql+pymysql://user:password@server/db')
df.to_sql(name='US_FoodInsecurityData_FeedingAmerica', con=engine, 
          if_exists = 'replace', index=False)
print('Done!')