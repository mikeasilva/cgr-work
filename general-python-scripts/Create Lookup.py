# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 11:18:42 2016

@author: Michael
"""
from fuzzywuzzy import fuzz
import pandas as pd

haystack = pd.read_csv('web_list.csv')
haystack = haystack['Libraries'].values.tolist()

needles = pd.read_csv('excel_list.csv')
needles = needles['Library'].values.tolist()

best_matches = []

# Look for best match 
for needle in needles:
    print('Searching for: '+needle)
    best_match_needle = ''
    best_match_hay = ''
    best_match_ratio = 0
    search_for_match = True
    while search_for_match:
        for hay in haystack:
            match_score = fuzz.partial_ratio(needle, hay)
            if match_score > best_match_ratio:
                best_match_ratio = match_score
                best_match_needle = needle
                best_match_hay = hay
            if match_score == 100:
                search_for_match = False
        # Looped through haystack so stop searching
        search_for_match = False
    # Append best match search results
    row = {'Searched':best_match_needle, 'Found':best_match_hay, 'Ratio':best_match_ratio}
    best_matches.append(row)


df = pd.DataFrame(best_matches)
writer = pd.ExcelWriter('Best Matches.xlsx', engine='xlsxwriter')
df.to_excel(writer,'Sheet1', index=False)
writer.save()
