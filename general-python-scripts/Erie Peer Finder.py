# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 11:01:27 2017

@author: Michael Silva

This script is used to determine what counties are like Erie, PA.

"""
import csv
import pandas as pd
import numpy as np
import math

def cosine_similarity(a, b):
    return sum([i*j for i,j in zip(a, b)])/(math.sqrt(sum([i*i for i in a]))* math.sqrt(sum([i*i for i in b])))
    
data = dict()
names = dict()
include_geography = True
number_of_models = 400
minimum_model_variables = 2
run_lots_of_small_models = True

erie_pa_fips = '42049'

print('Building the data sets')

# 2010 and 2015 pop estimates + names
with open('PEP_2015_PEPANNRES_with_ann.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        if row['GEO.id2'] != 'Id2':
            names[row['GEO.id2']] = row['GEO.display-label']
            data[row['GEO.id2']] = {'pop_2010':int(row['resbase42010']), 'pop_2015':int(row['respop72015'])}

# Educational attainment
with open('ACS_15_5YR_S1501_with_ann.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        try:
            total = int(row['HC01_EST_VC08'])
            college_degree_holder = int(row['HC01_EST_VC14'])
            data[row['GEO.id2']]['college_degree_holder'] = (college_degree_holder / total)
        except: continue
    
# People in Poverty
with open('ACS_15_5YR_S1701_with_ann.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        try:
            total = int(row['HC01_EST_VC01'])
            data[row['GEO.id2']]['people_in_poverty'] =  people_in_poverty = int(row['HC02_EST_VC01'])
            data[row['GEO.id2']]['share_in_poverty'] = (people_in_poverty / total)
        except: continue

# The share of the 2010 population living in "urban" areas
with open('DEC_10_SF1_P2_with_ann.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        try:
            total = int(row['D001'])
            urban = int(row['D002'])            
            data[row['GEO.id2']]['urban_pop_share_2010'] = (urban/total)
        except: continue

# Current share of mfg jobs
jobs_2015 = dict()
with open('CA25N_2001_2015__ALL_AREAS.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        try:
            data[row['GeoFIPS']]
            if row['LineCode'] == "90":
                data[row['GeoFIPS']]['private_jobs_2015'] = jobs_2015[row['GeoFIPS']] = int(row['2015'])
            if row['LineCode'] == "500":
                data[row['GeoFIPS']]['mfg_jobs_2015'] = int(row['2015'])
                data[row['GeoFIPS']]['mfg_jobs_share_2015'] = int(row['2015']) / jobs_2015[row['GeoFIPS']]
        except: continue

# Historic share of mfg jobs + change in private sector non-ag jobs
jobs = dict()
with open('CA25_1969_2000__ALL_AREAS.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        try:
            data[row['GeoFIPS']]
            if row['LineCode'] == "90":
                data[row['GeoFIPS']]['private_jobs_1970'] = jobs[row['GeoFIPS']] = int(row['1970'])
            if row['LineCode'] == "400":
                data[row['GeoFIPS']]['mfg_jobs_1970'] = int(row['1970'])
                data[row['GeoFIPS']]['mfg_jobs_share_1970'] = int(row['1970']) / jobs[row['GeoFIPS']]
                data[row['GeoFIPS']]['private_jobs_change_1970_2015'] = (jobs_2015[row['GeoFIPS']] / jobs[row['GeoFIPS']])-1
        except: continue

# Number of colleges and fte enrollment (for scale of institutions)
enrollment = dict()
counts = dict()
with open('IPEDS_Data_2-22-2017---198.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        try:
            enrollment[row['Fips County code (HD2015)']] = enrollment.get(row['Fips County code (HD2015)'],0) + int(row['Full-time equivalent fall enrollment (DRVEF2015)'])
            counts[row['Fips County code (HD2015)']] = counts.get(row['Fips County code (HD2015)'], 0) + 1
            data[row['Fips County code (HD2015)']]['fte_college_enrollment_2015'] = enrollment[row['Fips County code (HD2015)']]
            data[row['Fips County code (HD2015)']]['college_count_2015'] = counts[row['Fips County code (HD2015)']]
        except: continue

# Number of school districts and enrollment
enrollment = dict()
counts = dict()
with open('ELSI_csv_export_6362379782510259565867.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        try:
            enrollment[row['County Number [Public School] 2013-14']] = enrollment.get(row['County Number [Public School] 2013-14'],0) + int(row['Total Students All Grades (Excludes AE) [Public School] 2013-14'])
            counts[row['County Number [Public School] 2013-14']] = counts.get(row['County Number [Public School] 2013-14'], 0) + 1
            data[row['County Number [Public School] 2013-14']]['school_district_enrollment_2013_14'] = enrollment[row['County Number [Public School] 2013-14']]
            data[row['County Number [Public School] 2013-14']]['school_district_count_2013_14'] = counts[row['County Number [Public School] 2013-14']]
        except: continue


# Geographic Components
if include_geography:
    with open('DEC_10_SF1_G001_with_ann.csv') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            try:
                data[row['GEO.id2']]['GEO_land_area'] = int(row['VD067'])
                data[row['GEO.id2']]['GEO_water_area'] = int(row['VD068'])
                data[row['GEO.id2']]['GEO_latitude'] = float(row['VD074'])
                data[row['GEO.id2']]['GEO_longitude'] = float(row['VD075'])
            except: continue

# Create a dataframe from the dictionary    
df = pd.DataFrame.from_dict(data, orient='index')
fields = list(df.columns)
fields.sort()
df = df[fields]

# Update the data dictionary
data = df.to_dict(orient='index')

print('Running models')
# Set random number seed
np.random.seed(1234567890)

total_variables = len(fields)
model_details = dict()
model_results = dict()
for i in range(0, number_of_models):
    print('  Running model #'+str(i))
    if run_lots_of_small_models:
        number_of_variables = 2
    else:
        number_of_variables = np.random.randint(minimum_model_variables, total_variables+1) 
    fields_index = np.random.choice(total_variables, number_of_variables, replace=False)
    model_variables = [fields[key] for key in fields_index]
    # Note what was selected by the script
    for var in model_variables:
        try: model_details[i]
        except:
            model_details[i] = var
        else:
            model_details[i] = model_details[i] + ' and '+var
    # Get the model data 
    model_data = df[model_variables].to_dict(orient='index')
    model_results[i] = dict()
    a = list(model_data[erie_pa_fips].values())
    
    centered_a = [a_val / a_val for a_val in a]
    
    for key, data in model_data.items():
        b = list(model_data[key].values())
        
        centered_b = [b_val / a_val for b_val,a_val in zip(b, a)]
        model_results[i][key] = cosine_similarity(centered_a, centered_b)
    
df_names = pd.DataFrame.from_dict(names, orient='index')

df_results = pd.DataFrame.from_dict(model_results)
df_results.fillna(0, inplace=True)
df_results['average'] = df_results.mean(numeric_only=True, axis=1)

#df_peers = pd.merge(df_results['average'], df_names)

df_details = pd.DataFrame.from_dict(model_details, orient='index')

# Save the data to excel
print('Saving the results')

writer = pd.ExcelWriter('data.xlsx', engine='xlsxwriter')
df.to_excel(writer)
df_names.to_excel(writer, sheet_name='Names', header=False)
df_results.to_excel(writer, sheet_name='Model Results')
df_details.to_excel(writer, sheet_name='Model Details', header=False)
writer.save()