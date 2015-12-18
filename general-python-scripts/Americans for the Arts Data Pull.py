# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 11:22:23 2015

@author: Michael Silva
"""
from bs4 import BeautifulSoup
import pandas as pd
import urllib, json
# Set this to True the first time through.  It will only download data for DE.
# Once you have done this open 'Local Arts Index.csv' and update the 
# rows_to_keep variable below.  Then set it to False and rerun the program.
first_run = True
rows_to_keep = range(19, 25) # Remember: range(19, 25) = 19-24
data_year = 2015
pop_est_vintage = 2014
pop_est_date = '7' # 7 = 2014

## You shouldn't have to edit below this line
data_filename = 'Local Arts Index.csv'
base_url = 'http://www.artsindexusa.org/where-i-live?c4='
data_url = 'http://www.artsindexusa.org/fetchCounty.php?selectedCounty='
census_api_key = 'PUT YOUR API KEY HERE'
pop_est_api = 'http://api.census.gov/data/'+str(pop_est_vintage)+'/pep/cty?get=POP,DATE&for=county:*&key='+census_api_key
final_file_name = 'H:/Data Warehouse/Americans for the Arts/Arts Spending-'+str(data_year)+'.xlsx'

states = ['AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']
if first_run:
    states=['DE']

## Step through each state
for st in states:
    print('Starting '+st)
    url = 'http://www.artsindexusa.org/fetchCounties.php?state='+st
    response = urllib.urlopen(url)
    json_data = json.loads(response.read())
    for county_data in json_data:
        county = county_data.split(':')
        county_fips = county[0]
        county_name = county[1]
        print('  Scraping '+county_name+', '+st+' data')
        # Get the measure descriptions
        measures = list()
        url = base_url + county_fips
        page = urllib.urlopen(url)
        soup = BeautifulSoup(page.read(), 'html.parser')
        for el in soup.find_all('div',class_='sub'):
            el = el.get_text() # get the text values 
            el = el.encode('ascii',errors='ignore') # Get rid of non ASCII characters
            measures.append(el)
        # Get the values
        url = data_url + county_fips
        df = pd.read_json(url)
        df.columns = ['value']
        df['row'] = df.index # add row numbers
        df['fips'] = county_fips # add county fips
        df['county_name'] = county_name # add county name
        df['state'] = st # add state name
        df['measures'] = measures # add the measures
        
        try:
            arts_data = arts_data.append(df, ignore_index=True)
        except NameError:
            arts_data = df

if first_run:
    pd.DataFrame.to_csv(arts_data, data_filename, index=False)
    print('Please open "'+data_filename+'" and update the row_to_keep variable (currently set to: '+str(rows_to_keep)+')')
else:
    arts_data = arts_data[arts_data['row'].isin(rows_to_keep)]
    arts_data['value'] = pd.to_numeric(arts_data['value'].str.replace(r'[$,]', ''), errors='coerce')
    arts_data = arts_data.pivot(index='fips',columns='measures', values='value')
    arts_data['FIPS Code'] = arts_data.index
    
    print('Getting Population Estimates Data')
    pop_est = pd.read_json(pop_est_api)
    ## Rename the columns to be the first row
    pop_est.columns = list(pop_est.ix[0])
    ## Drop first row
    pop_est = pop_est.ix[1:]
    pop_est = pop_est[pop_est.DATE == pop_est_date]
    pop_est['FIPS Code'] = pop_est['state'] + pop_est['county']
    pop_est['Population'] = pop_est['POP']
    pop_est = pop_est[['FIPS Code','Population']]
    
    final_data = pd.merge(arts_data, pop_est)
    fips = final_data['FIPS Code']
    final_data.drop(labels=['FIPS Code'], axis=1,inplace = True)
    final_data.insert(0, 'FIPS Code', fips)
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(final_file_name, engine='xlsxwriter')
    final_data.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()