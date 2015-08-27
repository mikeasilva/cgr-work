# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 12:55:23 2015

@author: Michael
"""
# Load libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd

# Initiate variables
metros = dict()
cost_of_living_index = list()
avg_prices = list()

# Request calculator
page = requests.get('https://www.coli.org/calculator/calculator.asp?guid={80C33227-3056-4F17-A547-8B0CE11B356C}')
soup = BeautifulSoup(page.text)

# Step through options
for opt in soup.find_all('option'):
    metros[opt.get('value')] = opt.text

# Fake a form post
for key, value in metros.iteritems() :
    print key, value
    data = {'salary': 100000,
    'selectMovingFrom':int(key),
    'selectMovingTo':56,
    'Submit':'calculate',
    'hidMovingFromVal':int(key),
    'hidMovingFrom':value,
    'hidMovingToVal':56,
    'hidMovingTo':'DE Dover',
    'strGUID':'{80C33227-3056-4F17-A547-8B0CE11B356C}'
    }
    page = requests.post('https://www.coli.org/calculator/calculator.asp?action=compute', data=data)
    soup = BeautifulSoup(page.text)
    
    note = soup.find("span",{"class":"comment"}).text
    
    # Cost of Living Index Values
    table = soup.find("table", {"class":"indexTable"})
    for row in table.findAll("tr"):
        indexCategory = row.find("td",{"class":"indexCategory"}).text
        indexData = row.find("td",{"class":"indexData"}).text
        new_row = {"Metro":value, "Category":indexCategory, "Index":indexData, "Notes":note}
        cost_of_living_index.append(new_row)
        
    # Average Prices
    table = soup.find("table",{"class":"avgTable"})
    for row in table.findAll("tr"):
        avgCategory = row.find("td",{"class":"avgCategory"}).text
        # Added wiggle for metros that don't have average price data
        avgData = row.find("td",{"class":"avgData"})
        if(str(avgData)=='None'):
            avgData = None
        else:
            avgData = row.find("td",{"class":"avgData"}).text
        new_row = {"Metro":value, "Category":avgCategory, "Avg Price":avgData, "Notes":note}
        avg_prices.append(new_row)

# Save data as csv files
cost_of_living_index_df = pd.DataFrame(cost_of_living_index)
cost_of_living_index_df.to_csv("cost_of_living_index.csv", encoding='utf-8', index=False)

avg_prices_df = pd.DataFrame(avg_prices)
avg_prices_df.to_csv("avg_prices.csv", encoding='utf-8', index=False)

print "Done"