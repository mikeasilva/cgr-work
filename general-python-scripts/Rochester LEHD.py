# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 10:46:41 2017

@author: Michael Silva
"""
import numpy as np
import pandas as pd
import sqlite3 as db

con = db.connect("2014 NY LEHD.sqlite")

print('Reading in census tract centroids')
# Get the census tract centroids
def get_census_tract_id(geo_id):
    temp = geo_id.split('S')
    return np.int64(temp[1])

centroids = pd.read_csv('NY Tract Centroids.csv')
centroids['trct'] = centroids['GEO_ID'].apply(get_census_tract_id).astype('str')
centroids = centroids[['trct','X','Y']]

#print('Pulling crosswalk data (this may take a while)')
#df_xwalk = pd.read_sql_query("SELECT * FROM xwalk", con)
#df_xwalk = pd.merge(df_xwalk, centroids, on='trct', how='inner')

print('Pulling LODES data (this may take a while)')
df = pd.read_sql_query("""SELECT lodes.* FROM lodes 
JOIN xwalk ON xwalk.tabblk2010 = lodes.h_geocode
WHERE xwalk.stplcname = 'Rochester city, NY'""", con)

con.close()

print('Wrangling the data')
# Aggregate the data up to the tract level.  w_geocode and h_geocode are block 
# group ids.  The tracts are the first 11 characters
df['temp'] = df['h_geocode'].astype('str')
df['home'] = df.temp.str[:11]

df['temp'] = df['w_geocode'].astype('str')
df['work'] = df.temp.str[:11]
df['workers'] = df['S000']

# Subset the columns
df = df[['home', 'work', 'workers']]

# Join the xwalk

# Aggregate the data
agg_df = df.groupby(['home','work'])['workers'].sum().reset_index()

h_df = df.groupby(['home'])['workers'].sum().reset_index()
h_df['density'] = h_df.workers / h_df.workers.sum()

w_df = df.groupby(['work'])['workers'].sum().reset_index()
w_df['density'] = w_df.workers / w_df.workers.sum()

# Join census tract centroids to aggregated data 
temp = centroids.rename(columns={'trct': 'home', 'X':'home_longitude', 'Y':'home_latitude'})
agg_df = pd.merge(agg_df, temp, on='home', how='inner')
h_df = pd.merge(h_df, temp, on='home', how='inner')

temp = centroids.rename(columns={'trct': 'work', 'X':'work_longitude', 'Y':'work_latitude'})
agg_df = pd.merge(agg_df, temp, on='work', how='inner')
w_df = pd.merge(w_df, temp, on='work', how='inner')

# Save the data 
print('Saving data')
writer = pd.ExcelWriter('LEHD Data.xlsx')
agg_df.to_excel(writer,'LODES', index = False)
h_df.to_excel(writer,'Home', index = False)
w_df.to_excel(writer,'Work', index = False)
writer.save()

print('Done')