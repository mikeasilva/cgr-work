# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 11:22:02 2016

@author: Michael Silva
"""

import glob
import pandas as pd
import requests
from sqlalchemy import create_engine
import zipfile

# Download the raw data
print('Downloading OSC data')
zip_file_name = "all_classes_years.zip"
response = requests.get("http://www.osc.state.ny.us/localgov/datanstat/findata/level3zip/all_classes_years.zip")
zip_file = open(zip_file_name, "wb")
zip_file.write(response.content)
zip_file.close()

# Extract the zip
print('Unzipping file')
with zipfile.ZipFile(zip_file_name,"r") as zip_ref:
    zip_ref.extractall(".")

unlink(zip_file_name)
	
# Connect to CGR's Data Hub
engine = create_engine('mysql+pymysql://user:password@server/database')
conn = engine.connect()
print ("Connected to CGR's Data Hub successfully")

# Drop old data
conn.execute("DROP TABLE IF EXISTS RAW_NY_OSC_DETAILED_ACCOUNT_LEVEL_DATA")
conn.execute("CREATE TABLE `RAW_NY_OSC_DETAILED_ACCOUNT_LEVEL_DATA` (`CALENDAR_YEAR` int(11) DEFAULT NULL, `MUNICIPAL_CODE` varchar(255) DEFAULT NULL, `ENTITY_NAME` varchar(255) DEFAULT NULL, `CLASS_DESCRIPTION` varchar(255) DEFAULT NULL, `COUNTY` varchar(255) DEFAULT NULL, `FISCAL_YEAR_END` varchar(255) DEFAULT NULL, `ACCOUNT_CODE` varchar(255) DEFAULT NULL, `ACCOUNT_CODE_NARRATIVE` varchar(255) DEFAULT NULL, `FINANCIAL_STATEMENT` varchar(255) DEFAULT NULL, `FINANCIAL_STATEMENT_SEGMENT` varchar(255) DEFAULT NULL, `LEVEL_1_CATEGORY` varchar(255) DEFAULT NULL, `LEVEL_2_CATEGORY` varchar(255) DEFAULT NULL, `OBJECT_OF_EXPENDITURE` varchar(255) DEFAULT NULL, `AMOUNT` double DEFAULT NULL, `SNAPSHOT_DATE` varchar(255) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8;")
conn.execute("ALTER TABLE `RAW_NY_OSC_DETAILED_ACCOUNT_LEVEL_DATA` ADD KEY `MUNICIPAL_CODE` (`MUNICIPAL_CODE`), ADD KEY `ACCOUNT_CODE` (`ACCOUNT_CODE`), ADD KEY `FINANCIAL_STATEMENT` (`FINANCIAL_STATEMENT`), ADD KEY `CALENDAR_YEAR` (`CALENDAR_YEAR`);")
                       
# Identify all the CSV files
all_files = glob.glob("*.csv")

# Loop through them
for file_ in all_files:
    print("Processing "+file_)
    # Read them into a pandas data frame
    df = pd.read_csv(file_)
    # Write them to the Data Hub
    df.to_sql('RAW_NY_OSC_DETAILED_ACCOUNT_LEVEL_DATA', engine, if_exists='append', index=False)
    unlink(file_)

# Add in a primary key
print('Creating primary key index')
conn.execute("ALTER TABLE `RAW_NY_OSC_DETAILED_ACCOUNT_LEVEL_DATA` ADD `id` BIGINT(20) NOT NULL AUTO_INCREMENT FIRST, ADD PRIMARY KEY (`id`);")

conn.close()

print("Done")