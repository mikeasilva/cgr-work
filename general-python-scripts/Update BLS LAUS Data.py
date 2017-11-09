# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 14:14:43 2017

@author: Michael
"""

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
import csv

max_year = 2016
min_year = max_year - 10


def download_with_progress_bar(url, file_name):
    response = requests.get(url, stream=True)
    total_length = response.headers.get('content-length')
    if total_length is not None:
        fh = open(file_name, 'wb')
        dl = 0
        total_length = int(total_length)
        for data in response.iter_content(chunk_size=4096):
            dl += len(data)
            done = int(50 * dl / total_length)
            print("\r[%s%s]" % ('=' * done, ' ' * (50-done)), end='')
            if not data:
                break
            else:
                fh.write(data)
        fh.close()
        print('')
      
Base = declarative_base()

class Laus(Base):
    __tablename__ = 'US_LAUSData_BLS_UPDATE'
    
    series_id = Column(String, primary_key=True)
    year = Column(Integer, primary_key=True)
    period = Column(String, primary_key=True)
    value = Column(Float)
    footnote_codes = Column(String)

# This will hold the data that has been loaded into the hub
loaded_laus_data = list()

base_url = 'https://download.bls.gov/pub/time.series/la/'
files_to_load = ['la.data.2.AllStatesU', 'la.data.10.Arkansas',
                 'la.data.14.Delaware', 'la.data.16.Florida',
                 'la.data.28.Massachusetts', 'la.data.39.NewYork',
                 'la.data.42.Ohio', 'la.data.45.Pennsylvania',
                 'la.data.47.RhodeIsland', 'la.data.50.Tennessee',
                 'la.data.51.Texas', 'la.data.60.Metro']
#files_to_load = ['la.data.2.AllStatesU']

"""
================================== PROCESS FLOW ===============================
"""

# Connect to CGR's Data Warehouse
print("Connecting to CGR's Data Hub")
engine = create_engine('mysql+pymysql://user:password@server/db')
conn = engine.connect()

Session = sessionmaker(bind=engine)
session = Session()

# Drop old data table and create placeholder
conn.execute('DROP TABLE IF EXISTS `US_LAUSData_BLS_UPDATE`')
# Create and update table
conn.execute('CREATE TABLE `US_LAUSData_BLS_UPDATE` LIKE `US_LAUSData_BLS`')

for file_to_load in files_to_load:
    url = base_url + file_to_load
    file_name = 'LAUS Text Files/' + file_to_load + '.txt'
    print('Requesting '+file_to_load)
    download_with_progress_bar(url, file_name)
    with open(file_name) as csvfile:
        print('Searching '+ file_to_load +' ...')
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            try:
                # Here's the data we are pulling
                series = row[0].strip()
                year = int(row[1])
                period = row[2]
                value = float(row[3])
                footnote_codes = row[4]
                # Add in the annual data that fall in the year range
                if period == 'M13' and year >= min_year and year <= max_year:
                    key = series + str(year) + period
                    if key not in loaded_laus_data:
                        # Load it into the LAUS
                        new = Laus(series_id=series, year=year, period=period,
                                   value=value, footnote_codes=footnote_codes)
                        session.add(new)
                        loaded_laus_data.append(key)
            except: continue
        print('Saving '+ file_to_load +' ...')
        session.commit()

session.commit()
session.close()
    
    
    