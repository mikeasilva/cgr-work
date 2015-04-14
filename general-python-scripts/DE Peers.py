# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:35:46 2015

@author: Michael Silva
"""

import pandas as pd
from scipy.spatial.distance import cosine

df = pd.DataFrame.from_csv('DE.csv')

# Pull out Delaware's Record
de = df.loc['Delaware']

# Create the list that will hold the data
d = []

# Iterate through the data frame and calculate the cosine similarity
for index, row in df.iterrows():
    dist =  (1-cosine(de,row))
    d.append(dist)

# Add the new column
df['similarity'] = d

df = df.sort('similarity', ascending=0)

df.to_csv('DE-peers.csv')