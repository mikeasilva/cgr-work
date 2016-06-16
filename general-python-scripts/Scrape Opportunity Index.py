# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 16:18:24 2016

@author: Michael
"""
import requests
import pandas as pd

opportunity_index_data = list()

# Loop through the list of fips codes
for line in open('fips.csv', 'r', encoding='latin-1'):
    csv_row = line.split(',') 
    # Pull the name
    pos = line.find('"')
    if pos > 0:
        name = line[pos:].strip().replace('"','')
    else:
        name = csv_row[2].strip()
    print('Getting data for '+name)
    # Pull the FIPS code
    fips = csv_row[1]
    # Request the data
    url = 'http://opportunityindex.org/'
    if len(fips) < 5:
        url = url + 'data/state?fips=' + fips
    else:
        url = url + 'data/county?fips=' + fips
    r = requests.get(url).json()
    # Add the data to the list
    for row in r['data']:
        row.update({'name':name, 'fips':fips})
        opportunity_index_data.append(row)
        
# Turn list into data frame
df = pd.DataFrame(opportunity_index_data)

# Convert string values to numeric
print('Converting Data')
numeric_columns = list(df.columns.values)
numeric_columns.remove('fips')
numeric_columns.remove('name')
numeric_columns.remove('opp_grade')
numeric_columns.remove('opp_str')
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='ignore')

# Save it as an Excel file
print('Writing Data')
writer = pd.ExcelWriter('Opportunity Index.xlsx', engine='xlsxwriter')
df.to_excel(writer,'Sheet1', index=False)
writer.save()
    