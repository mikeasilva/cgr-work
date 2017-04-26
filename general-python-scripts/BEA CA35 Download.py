# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 15:38:26 2017

@author: Michael Silva
"""

import urllib
import zipfile
import pandas as pd
from sqlalchemy import create_engine


zip_url = 'https://www.bea.gov/regional/zip/CA35.zip'

print ("Downloading Zip from BEA")
response = urllib.request.urlopen(zip_url)
with open('CA35.zip', 'wb') as out_file:
    out_file.write(response.read())

# Connect to CGR's Data Hub
print ("Connecting to CGR's Data Hub")
engine = create_engine('mysql+pymysql://username:password@server/database')
conn = engine.connect()


z = zipfile.ZipFile('CA35.zip')

print ("Reading zip file")
for file_name in z.namelist():
    if 'ALL_AREAS' in file_name:
        df = pd.read_csv(z.open(file_name), encoding="ISO-8859-1", dtype={'GeoFIPS': object, 'Region': object, 'LineCode': object, 'IndustryClassification': object}, na_values=['(L)', '(NA)', '...'])

print ("Wrangling data")
df_vars = list(df.columns)

df = pd.melt(df, id_vars=df_vars[:6], value_vars=df_vars[7:], var_name='year', value_name='Measure')
cols = df_vars[:6]
cols.append('Measure')
cols.append('year')
df = df[cols]

df[['Measure','year']] = df[['Measure','year']].apply(pd.to_numeric)

print ("Writing to CGR's Data Hub")
df.to_sql(name='UPDATE_BEA_PERSONAL_CURRENT_TRANSFER_RECEIPTS_CA35', con=conn, if_exists='replace', index=False)

conn.close()