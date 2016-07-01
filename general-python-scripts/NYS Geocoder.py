# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 13:15:28 2016

@author: Michael Silva
"""
import pandas as pd
import requests

data = list()
service_url = 'http://gisservices.dhses.ny.gov/arcgis/rest/services/Locators/Street_and_Address_Composite/GeocodeServer/findAddressCandidates'

locations = pd.read_excel('Event Locations.xlsx')
#addressess = ['1 South Washington Street, Rochester, NY','115 south ave rochester ny','rt 96 and county line, victor ny']
addressess = locations['geocode_me'].tolist()
i=0
for address in addressess:
    i=i+1
    print(str(i)+' of '+str(len(addressess)))
    full_address = address + ', Victor NY'
    payload = {'SingleLine': full_address, 'f': 'pjson'}
    r = requests.get(service_url, params=payload)
    js = r.json()
    if len(js['candidates'])>0:
        # Pull the best candidate's data
        clean_address = js['candidates'][0]['address']
        x = js['candidates'][0]['location']['x']
        y = js['candidates'][0]['location']['y']
        score = js['candidates'][0]['score']
        row = [address, clean_address, x, y, score]
    else:
        row = [address, None, None, None, None]
    data.append(row)
df = pd.DataFrame(data)
df.columns = ['address','clean_address','x','y','score']

writer = pd.ExcelWriter('Gecode Results.xlsx', engine='xlsxwriter')
df.to_excel(writer,'Gecode Results', index=False)
writer.save()
