# -*- coding: utf-8 -*-
"""
A little Python script to pull out data from a text file

Created on Thu Jun 18 10:47:23 2015

@author: Michael Silva
"""

f = open('Non County Title Deployment.txt')

# FEATURE IDENTIFIERS
# There are some lines that have features.  They are identified by the 
# following strings:
title_identifier = '* TITLE NO.: '
page_identifier = 'PAGE '

# SKIP LINES
# There are some lines we don't want to pull into the final .csv file.  They
# are identified by the following strings:
skip_words = [' PEM11','DEPT DEPARTMENT', 'TOTAL ']

# INITIALIZE LIST
# This list will hold the data pulled from the text file
data = [['Title','Department','Filled','Vacant','Total','Page']]

# STEP THROUGH LINE BY LINE
for line in iter(f):
    # FEATURE SEARCH
    if line.count(title_identifier):
        title = line.replace(title_identifier,'').replace(' *','')
    elif line.count(page_identifier):
        page = line.replace(page_identifier,'')
    # SKIP LINE CHECK
    elif any(word in line for word in skip_words):
        continue
    # LINES THAT MIGHT HAVE DATA
    else:
        items = line.split()            
        num_items = len(items)
        if num_items > 3:
            # There is data here so build a row to append to the data
            counts = items[num_items-3:num_items]
            dept = line.replace(" ".join(counts),'')
            row = [title.strip(), dept.strip(), counts[0], counts[1], counts[2], page.strip()]
            data.append(row)
f.close()

# WRITE THE OUTPUT
# Now that we have pulled the data we need to create a .csv with all the data
import csv

with open("output.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(data)