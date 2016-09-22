# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 11:07:40 2016

@author: Michael Silva
"""
from bs4 import BeautifulSoup
import requests as re
import pandas as pd

base_url = 'http://www.artsindexusa.org/where-i-live?c4='
data_url = 'http://www.artsindexusa.org/fetchCounty.php?selectedCounty='
data = list()
states = ['AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']

for st in states:
    # Get the list of counties
    url = 'http://www.artsindexusa.org/fetchCounties.php?state='+st
    county_fips = re.get(url).json()
    for fips in county_fips:
        fips = fips.split(':')
        print('Getting data for: '+fips[1]+', '+st)
        # Get the headers and identify which rows we want in the data
        page = re.get(base_url + fips[0])
        soup = BeautifulSoup(page.content, 'lxml')
        headers = dict()
        i = 0
        for div in soup.find_all('div',{'class':'sub'}):
            text = div.text
            text = text.replace('\xa0','')
            if 'Overall participation in arts and culture activities' in text:
                headers[i] = text
            i=i+1
        # Pull the data for the rows identified above
        response = re.get(data_url + fips[0])
        i = 0
        for val in response.json():
            if i in headers:
                soup = BeautifulSoup(val, 'lxml')
                value = soup.get_text()
                if value != 'N/D':
                    data.append({'county fips':fips[0], 'county name':fips[1], 'state':st, 'measure':headers[i], 'value':soup.get_text()})
            i=i+1

# Build a data frame from the list of dicts
df = pd.DataFrame(data)

# Save it as an Excel file
print('Writing Data')
writer = pd.ExcelWriter('Local Arts Index Cultural Participation.xlsx', engine='xlsxwriter')
df.to_excel(writer,'AFA_Cultural_Participation', index=False)
writer.save()