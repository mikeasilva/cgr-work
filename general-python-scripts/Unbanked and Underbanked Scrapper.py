# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 15:41:15 2017

@author: Michael Silva
"""

import requests
from sqlalchemy import create_engine
import pandas as pd

year = 2015

engine = create_engine('mysql+pymysql://user:password@server/db')
conn = engine.connect()
query = conn.execute('''SELECT *  FROM `DW_Geography` 
                 WHERE `type` IN ('State', 'County')''').fetchall()

data = list()

for row in query:
    i = str(row[0])
    name = row[1]
    print('Getting data for '+name)
    url = 'http://scorecard.prosperitynow.org/rest/place/'+i
    response = requests.get(url)
    j = response.json()
    underbanked = j['data']['underbanked']
    unbanked = j['data']['unbanked']
    d = {'ID':i, 'Name':name, 'unbanked':unbanked, 
         'underbanked':underbanked, 'year':year}
    data.append(d)

conn.close()

# Save data a spreadsheet
df = pd.DataFrame.from_records(data)
writer = pd.ExcelWriter(str(year)+' data.xlsx')
df.to_excel(writer, str(year), index = False)
writer.save()

