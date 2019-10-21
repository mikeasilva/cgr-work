# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 09:57:50 2018

@author: Michael Silva
"""

import requests
import zipfile
import os
import csv
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sqlalchemy import create_engine
import pymysql
import sqlite3
import subprocess


db = sqlite3.connect('uspto.db')
c = db.cursor()


cursor = ['|','/','-','\\']
#cursor = ['*==', '=*==', '==*=', '===*']
cursor_idx = 0

def next_cursor(cursor_idx):
    cursor_idx = cursor_idx + 1
    if cursor_idx > 3:
        cursor_idx = 0
    return(cursor_idx)

running_localy = input('Is this running from a non-network location (y or n)? ')
if running_localy != 'y':
    print('Please copy this file to a non-network location and run it again')
    exit()

download_data = True

print('STEP 1: DOWNLOAD NEEDED DATA')

if download_data:
    def download_file(url):
        local_filename = url.split('/')[-1]
        print(' '+local_filename + ' Downloading', end="\r", flush=True)
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return local_filename
    
    
    def unzip_file(file_name):
        zip_ref = zipfile.ZipFile(file_name, 'r')
        zip_ref.extractall('.')
        zip_ref.close()
    
    
    urls = ['http://data.patentsview.org/20190820/download/location.tsv.zip',
            'http://data.patentsview.org/20190820/download/location_inventor.tsv.zip',
            'http://data.patentsview.org/20190820/download/patent.tsv.zip',
            'http://www2.census.gov/geo/tiger/GENZ2010/gz_2010_us_050_00_500k.zip']
            
    for url in urls:
        zip_file_name = download_file(url)
        unzip_file(zip_file_name)
        os.unlink(zip_file_name)
        print(' '+zip_file_name + ' Downloading  [DONE]')	 

print('STEP 2: WRANGLE DATA')

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.

try:
    c.execute('SELECT * FROM location')
    locations_list = c.fetchall()
    gdf = pd.DataFrame(locations_list)
    gdf.columns = ['location_id', 'state_fips', 'county_fips']
except:
    locations_list = list()
    print(' Reading location.tsv', end="\r", flush=True)
    with open('location.tsv', encoding="utf8") as f:
        for row in csv.DictReader(f, delimiter='\t'):
            try:
                locations_list.append({'location_id':row['id'], 
                                       'latitude': float(row['latitude']), 
                                       'longitude': float(row['longitude'])})
            except:
                continue
    print(' Reading location.tsv [DONE]')
    
    # Now that we have our locations in the USA let's create a geopandas df
    print(' Creating locations data frame', end="\r", flush=True)
    locations_df = pd.DataFrame(locations_list)
    geom = locations_df.apply(lambda x: Point([x['longitude'], x['latitude']]), axis=1)
    locations_df = gpd.GeoDataFrame(locations_df, geometry=geom)
    locations_df = locations_df[['location_id', 'geometry']]
    locations_df.crs = {'init': 'epsg:4326'}
    print(' Creating locations data frame [DONE]')
    
    # Read in the County boundaries
    print(' Reading county shapefile', end="\r", flush=True)
    counties_df = gpd.read_file('gz_2010_us_050_00_500k.shp')
    counties_df = counties_df.to_crs(locations_df.crs)
    counties_df['county_fips'] = counties_df['STATE'] + counties_df['COUNTY']
    counties_df['state_fips'] = counties_df['STATE']
    counties_df = counties_df[['county_fips', 'state_fips', 'geometry']]
    print(' Reading county shapefile [DONE]')

    print(' Preforming spatial join', end="\r", flush=True)
    gdf = gpd.sjoin(locations_df, counties_df, op='within')
    gdf.reset_index(inplace=True)
    gdf = gdf[['location_id', 'state_fips', 'county_fips']]
    gdf.to_sql('location', con=db, index=False)
    print(' Preforming spatial join [DONE]')

locations = gdf.set_index('location_id').to_dict('index')

# Get the list of location ids we need to search for
location_ids = list(gdf.location_id)

try:
    c.execute('SELECT * FROM patent_location LIMIT 1')
except:
    c.execute('CREATE TABLE patent_location (patent_id text, location_id text)')
    values_to_insert = list()
    
    print(' Reading location_inventor.tsv (This will take a while)', end="\r", flush=True)
    with open('location_inventor.tsv', encoding="utf8") as f:
        for row in csv.DictReader(f, delimiter='\t'):
            print(' Reading location_inventor.tsv (This will take a while) '+cursor[cursor_idx], end="\r", flush=True)
            cursor_idx = next_cursor(cursor_idx)
            # We want to use the first named inventor as the location criteria
            inventor_num = row['inventor_id'].split('-')[1]
            if row['location_id'] in location_ids and inventor_num == "1":
                patent_id = row['inventor_id'].split('-')[0]
                values_to_insert.append((patent_id, row['location_id']))
    print(' Reading location_inventor.tsv (This will take a while) [DONE]')
    c.executemany('INSERT INTO patent_location VALUES (?,?)', values_to_insert)
    db.commit()

try:
    c.execute('SELECT * FROM patent LIMIT 1')
except:
    c.execute('CREATE TABLE "patent" ( `id` TEXT NOT NULL, `type` TEXT, `number` BIGINT NOT NULL, `country` TEXT, `date` DATETIME, `abstract` TEXT, `title` TEXT, `kind` TEXT, `num_claims` BIGINT NOT NULL, `filename` TEXT, PRIMARY KEY(`id`) )')
    db.commit()
    print(' Loading patent.tsv (This will take a while)', end="\r", flush=True)
    subprocess.call(["sqlite3", "uspto.db", ".mode tabs", ".import patent.tsv patent"])
    c.execute("DELETE FROM patent WHERE id == 'id'")
    db.commit()
    print(' Loading patent.tsv (This will take a while) [DONE]')

sql = '''SELECT location.state_fips, location.county_fips, SUBSTR(patent.date, 1, 4) AS `year`, SUM(1) as `total`
FROM location, patent_location, patent
WHERE patent_location.location_id = location.location_id AND patent.id = patent_location.patent_id AND patent.type == 'utility'
GROUP BY state_fips, county_fips, `year`'''

print('STEP 3: BUILDING TABLE')
print(' Running query (This will take hours)', end="\r", flush=True)
start = pd.read_sql_query(sql , db)
print(' Running query (This will take hours)  [DONE]')

start['Patents Issued'] = start['total'].astype('int')
start['Year'] = start['year'].astype('int')
start = start[start['Year']>1999]

df = start[['county_fips','Patents Issued','Year']]
df.columns = ['CGR_GEOGRAPHY_ID','Patents Issued','Year']

states = start[['state_fips','Patents Issued','Year']]
states.columns = ['CGR_GEOGRAPHY_ID','Patents Issued','Year']
states = states.groupby(['CGR_GEOGRAPHY_ID','Year'])['Patents Issued'].sum().reset_index()

usa = states.groupby(['Year'])['Patents Issued'].sum().reset_index()
usa['CGR_GEOGRAPHY_ID'] = "00"
usa = usa[['CGR_GEOGRAPHY_ID','Patents Issued','Year']]

df = df.append(states, ignore_index=True, sort=True).append(usa, ignore_index=True, sort=True).reset_index(drop=True)


print(' Getting local data')
engine = create_engine('mysql+pymysql://dba:cgr1915@data.cgr.org/hub')
connection = engine.connect()
results = connection.execute("""SELECT CGR_GeographyIndex.CGR_GEO_ID, CGR_GeographyIndex.NAME, CGR_GeographyIndex.patentsview_location_id
FROM ((CGR_GeographyIndex INNER JOIN CI_ClientGeography ON CGR_GeographyIndex.CGR_GEO_ID = CI_ClientGeography.CGR_GEO_ID) INNER JOIN CI_Client ON CI_ClientGeography.CI_Client_id = CI_Client.id) INNER JOIN CI_ClientIndicators ON CI_Client.id = CI_ClientIndicators.CI_Client_id
WHERE CGR_GeographyIndex.CI_GEO=1 AND CI_ClientIndicators.CI_Indicator_id="CI_12002_US"
GROUP BY CGR_GeographyIndex.CGR_GEO_ID, CGR_GeographyIndex.NAME, CGR_GeographyIndex.patentsview_location_id
HAVING CGR_GeographyIndex.patentsview_location_id Is Not Null;""")

data = list()

for row in results:
    print('  Getting data for '+row[1])
    cgr_geo_id = row[0]
    url = 'http://www.patentsview.org/api/locations/query?q={%22location_id%22:%22'+row[2]+'%22}&f=[%22patent_year%22]'
    response = requests.get(url)
    response_json = response.json()
    counts = dict()
    for record in response_json['locations'][0]['patents']:
        year = int(record['patent_year'])
        counts[year] = counts.get(year, 0) + 1
    for year,count in counts.items():
        if year > 1999:
            data.append({'CGR_GEOGRAPHY_ID':row[0],
                         'Patents Issued':count,
                         'Year':year})

temp = pd.DataFrame(data)	
df = df.append(temp, ignore_index=True, sort=True).reset_index(drop=True)

print('STEP 3: SAVING TO HUB')
df.to_sql(name='US_PatentData_USPTO_UPDATE', con=engine, 
          if_exists = 'replace', index=False)