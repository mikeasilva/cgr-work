# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 10:34:51 2019

@author: Michael
"""

import requests
import json

def get_url(address):
    # Convert spaces to plus signs
    address = address.replace(' ', '+')
    # Convert comma to %2C
    address = address.replace(',', '%2C')
    url = 'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address='+address+'&benchmark=9&format=json'
    return url

address = '1600 Pennsylvania Avenue NW, Washington, DC 20500'

response = requests.get(get_url(address))

data = requests.get(get_url(address)).text

data = json.loads(data)

coordinates = data['result']['addressMatches'][0]['coordinates']

lat = coordinates['y']
lng = coordinates['x']