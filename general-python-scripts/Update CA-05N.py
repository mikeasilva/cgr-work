# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 12:40:20 2015

@author: Michael Silva
"""

"""
This Python script explains the process undertaken to update the BEA_CA_05N 
table in the data warehouse.  This table is updated annually.  

Step 1: Load the Libraries

First we will load the libraries needed for the task:  
"""
import urllib
import zipfile
import pandas as pd
import os
"""
Step 2: Define Key Script Parameters

Next we define the parameters that are important to this script: 
"""
# What table are we going to get from the BEA?
bea_table_name = 'CA5N'
# Where should the zip file be saved?
zip_file = bea_table_name + '.zip'
# Which states do we want to include in the table?
states = ['FL', 'NY', 'TN', 'US']
# Once processed where should the data be saved?
raw_data_file_path = 'H:/Data Warehouse/Bureau of Economic Analysis (BEA)/CA-05N.xlsx'
# What is the table name in the data warehouse?
data_warehouse_table_name = 'BEA_CA_05N'
"""
Step 3: Download the Data

Now that these parameters are in place we are ready to download the data: 
"""
# Download the file
url = 'http://www.bea.gov/regional/zip/'+ bea_table_name +'.zip'
urllib.urlretrieve(url, zip_file)

"""
Step 4: Process the Data

Next we will loop through the list of states and process the data.  We will 
unzip the state specific csv file from the zip archive and read it in.  Next we 
will transform the data from a wide format to a long format.  Finaly we need to 
filter the data pulling only the years and columns that we want.  We rename the 
columns to be consistent with the data warehouse table and save the data to the 
bea_data data frame:  
"""
def float64_to_string(f):
    text = str(f)
    if '.0' in text:
        return text[:text.rfind('.0')]
    return text
    
for st in states:
    # Unzip the data
    filename = bea_table_name + '_2001_2014_' + st + '.csv'
    with zipfile.ZipFile(zip_file, 'r') as z:
        z.extract(filename)
    # Read the data
    temp = pd.read_csv(filename)
    # Delete the csv file
    os.remove(filename)
    # Transform data from wide to long
    temp = pd.melt(temp, id_vars=list(temp.columns.values[0:7]), value_vars=list(temp.columns.values[7:]))
    # change year type to integer
    temp['variable'] = pd.to_numeric(temp['variable'])
    # Change the line code type to match the data warehouse table
    temp['LineCode'] = temp['LineCode'].apply(float64_to_string)
    # Filter data from 1999 forward and select only certain columns
    temp = temp[temp['variable'] >=1999]
    temp = temp[['GeoFIPS', 'GeoName', 'LineCode', 'Description', 'value', 'variable']]
    # Special handeling of the US file
    if st == 'US':
        temp = temp[temp['GeoFIPS'] =='00000']
    # Rename columns to match the Data Warehouse Table
    temp.columns = ['GeoFips', 'GeoName', 'LineCode', 'Description', 'Estimate', 'Year']
    # Save cleaned data into bea_data
    try:
        bea_data = bea_data.append(temp)
    except NameError:
        bea_data = temp
os.remove(zip_file)
"""
Step 5: Save Processed Data

Now that we have the clean data we need to store it as an Excel file:  
"""
writer = pd.ExcelWriter(raw_data_file_path)
bea_data.to_excel(writer, data_warehouse_table_name+'_UPDATE', index=False)
writer.save()