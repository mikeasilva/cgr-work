# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:45:10 2017

@author: Michael Silva
"""

import requests, io
from bs4 import BeautifulSoup

import pandas as pd
from sqlalchemy import create_engine

start_year = 2000
end_year = 2018

state_codes = {'Alabama' : '01', 
'Alaska' : '02', 
'Arizona' : '04', 
'Arkansas' : '05', 
'California' : '06', 
'Colorado' : '08', 
'Connecticut' : '09', 
'Delaware' : '10', 
'District of Columbia' : '11', 
'Florida' : '12', 
'Georgia' : '13', 
'Hawaii' : '15', 
'Idaho' : '16', 
'Illinois' : '17', 
'Indiana' : '18', 
'Iowa' : '19', 
'Kansas' : '20', 
'Kentucky' : '21', 
'Louisiana' : '22', 
'Maine' : '23', 
'Maryland' : '24', 
'Massachusetts' : '25', 
'Michigan' : '26', 
'Minnesota' : '27', 
'Mississippi' : '28', 
'Missouri' : '29', 
'Montana' : '30', 
'Nebraska' : '31', 
'Nevada' : '32', 
'New Hampshire' : '33', 
'New Jersey' : '34', 
'New Mexico' : '35', 
'New York' : '36', 
'North Carolina' : '37', 
'North Dakota' : '38', 
'Ohio' : '39', 
'Oklahoma' : '40', 
'Oregon' : '41', 
'Pennsylvania' : '42', 
'Rhode Island' : '44', 
'South Carolina' : '45', 
'South Dakota' : '46', 
'Tennessee' : '47', 
'Texas' : '48', 
'Utah' : '49', 
'Vermont' : '50', 
'Virginia' : '51', 
'Washington' : '53', 
'West Virginia' : '54', 
'Wisconsin' : '55', 
'Wyoming' : '56'}#, 
#'Puerto Rico' : '72', 
#'Virgin Islands' : '78'}

# Connect to CGR's Data Hub
engine = create_engine('mysql+pymysql://username:password@server/database')
conn = engine.connect()
print ("Connected to CGR's Data Hub successfully")

# Drop/create database tables
conn.execute("DROP TABLE IF EXISTS TEMP_US_AirQualityIndexReport_EPA")
#conn.execute("CREATE TABLE TEMP_US_AirQualityIndexReport_EPA SELECT * FROM US_AirQualityIndexReport_EPA WHERE 1=0")

def clean_item(item):
    item = item.replace('#','Number').replace('%','Percent').replace('2.5', '25').replace('  ',' ').replace('County','Location').replace('CBSA', 'Location')
    return item
       

for state_name, code in state_codes.items():
    print('Getting data for',state_name)
    for year in range(start_year, end_year + 1):
        # Pull data from the report
        print(' Pulling the '+str(year)+' data')
        # Get the county level data
        try:
            url = 'https://www3.epa.gov/cgi-bin/broker?_service=data&_debug=0&_program=dataprog.ad_rep_aqi_drupal.sas&querytext=&areaname=&areacontacts=&areasearchurl=&typeofsearch=epa&result_template=2col.ftl&year='+str(year)+'&state='+code+'&cbsa=-1&county=-1&sumlevel=groupbycounty'
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'lxml')
            for a in soup.findAll('a', href=True, text='Download CSV (spreadsheet)'):
                csv = requests.get(a['href']).content
                df = pd.read_csv(io.StringIO(csv.decode('utf-8')), na_values = '.', dtype={'County Code': object})
                df['year'] = year
                # Rename columns
                new_columns = list()
                for item in list(df.columns):
                    new_columns.append(clean_item(item))
                df.columns = new_columns
                # Write to data hub
                df.to_sql(name='TEMP_US_AirQualityIndexReport_EPA', con=conn, if_exists='append', index=False)
        except: 
            print("Failed to save county level data")
            continue
        # Get the metro level data
        try:
            url = 'https://www3.epa.gov/cgi-bin/broker?_service=data&_debug=0&_program=dataprog.ad_rep_aqi_drupal.sas&querytext=&areaname=&areacontacts=&areasearchurl=&typeofsearch=epa&result_template=2col.ftl&year='+str(year)+'&state='+code+'&cbsa=-1&county=-1&sumlevel=groupbycbsa'
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'lxml')
            for a in soup.findAll('a', href=True, text='Download CSV (spreadsheet)'):
                csv = requests.get(a['href']).content
                df = pd.read_csv(io.StringIO(csv.decode('utf-8')), na_values = '.', dtype={'CBSA Code': object})
                df['year'] = year
                # Rename columns
                new_columns = list()
                for item in list(df.columns):
                    new_columns.append(clean_item(item))
                df.columns = new_columns
                # Write to data hub
                df.to_sql(name='TEMP_US_AirQualityIndexReport_EPA', con=conn, if_exists='append', index=False)
        except: 
            print("Failed to save metro level data")
            continue

print('Removing duplicates and dropping temp table')
conn.execute("CREATE TABLE US_AirQualityIndexReport_EPA_UPDATE SELECT * FROM US_AirQualityIndexReport_EPA WHERE 1=0")
conn.execute("INSERT INTO `US_AirQualityIndexReport_EPA_UPDATE` SELECT DISTINCT * FROM `TEMP_US_AirQualityIndexReport_EPA`")
conn.execute("DROP TABLE TEMP_US_AirQualityIndexReport_EPA;")
conn.close()

print("Done")
