# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 10:29:02 2017

@author: Michael Silva
"""
import pandas as pd
import sqlite3 as db

con = db.connect("2014 NY LEHD.sqlite")

print('Reading Crosswalk')
df = pd.read_csv('ny_xwalk.csv', low_memory=False)
print('Creating xwalk table')
df.to_sql('xwalk', con, if_exists='replace', index=False)
con.commit()

print('Reading LODES Main')
df = pd.read_csv('ny_od_main_JT00_2014.csv', low_memory=False)
print('Creating lodes table')
df.to_sql('lodes', con, if_exists='replace', index=False)
con.commit()

print('Reading LODES Aux')
df = pd.read_csv('ny_od_aux_JT00_2014.csv', low_memory=False)
print('Appending to lodes table')
df.to_sql('lodes', con, if_exists='append', index=False)
con.commit()

con.close()
print('Done')