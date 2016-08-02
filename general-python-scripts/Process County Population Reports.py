# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 13:29:37 2016

@author: Michael Silva

This script quickly aggregates the county level corrections populations found
at http://www.mass.gov/msa/facilities/county-population-reports.html

"""

import pandas as pd
import glob as g

# Helper functions
def get_gender(header):
    global current_gender
    if header == 'Jurisdiction of Origin-Males':
        current_gender = 'Male'
    elif header == 'Jurisdiction of Origin-Females':
        current_gender = 'Female'
    elif header == 'Total Population by Classification':
        current_gender = 'Total'
    return(current_gender)
    

def get_month(p):
    m = int(p.lower().strip('p'))
    if m < 7:
        m = m + 6
    else:
        m = m - 6
    return(m)
    
def get_year(fy):
    y = int(fy.lower().strip('fy'))
    return(y)
    
def standardize_columns(column_names):
    clean = list()
    for item in column_names:
        item = item.replace('*','')
        clean.append(item)
    return(clean)
            
    
# Initialize variables
current_gender = None

# Step through all the files in the working directory
for filename in g.glob("*.xls"):
    print('Processing '+filename)
    # Read the file
    xl = pd.ExcelFile(filename)
    # Step through all the sheets
    for sheet_name in xl.sheet_names:
        # Skip the cases where the sheet name is Sheet1
        if sheet_name == 'Sheet1': continue
        # Read in the sheet into a data frame
        df = xl.parse(sheet_name)
        # Drop rows where the first column is null
        df = df[pd.notnull(df.iloc[:,0])]
        # Pull the column names from the first row
        column_names = df.iloc[0].values.tolist()
        # rename the columns
        df.columns = column_names
        # Add the location
        if sheet_name == 'Summary':
            df['Location'] = 'Massachusetts'
        else:
            df['Location'] = sheet_name
        # Add the gender based on the first column
        df['Gender'] = df.iloc[:,0].apply(get_gender)
        # Pull the year and month from the file name
        split = filename.split('-')
        df['Year'] = get_year(split[0])
        df['Month'] = get_month(split[1])
        # Set the text values for Total to nan
        df['Total'] = df['Total'].apply(pd.to_numeric, errors='coerce')
        # Drop all nan Totals
        df = df[pd.notnull(df['Total'])]
        # Drop any columns with no data
        df=df.dropna(axis=1,how='all')
        # Standardize the column names        
        column_names = df.columns.values.tolist()
        column_names[0] = 'Jurisdiction of Origin'
        df.columns = standardize_columns(column_names)
        
        # Concatinate all the df's togethe
        if 'mass_sheriffs_data' in locals():
            mass_sheriffs_data = mass_sheriffs_data.append(df, ignore_index=True)
        else:
            mass_sheriffs_data = df
        
# Reorder the columns
mass_sheriffs_data = mass_sheriffs_data[column_names]
        
print('Saving the file')
writer = pd.ExcelWriter('Total County Correction Population.xlsx', engine='xlsxwriter')
mass_sheriffs_data.to_excel(writer,'MA_Sheriffs_Association_Total_C', index=False)
writer.save()