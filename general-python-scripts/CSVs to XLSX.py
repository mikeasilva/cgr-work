# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 11:22:02 2016

@author: Michael Silva
"""

import glob
import pandas as pd
import numpy as np

all_files = glob.glob("*.csv")

np_array_list = []
for file_ in all_files:
    print("Processing "+file_)
    df = pd.read_csv(file_)
    np_array_list.append(df.as_matrix())
    
print('Creating Big Data Frame')
comb_np_array = np.vstack(np_array_list)
del(np_array_list)
big_frame = pd.DataFrame(comb_np_array)
del(comb_np_array)
big_frame.columns = df.columns

print('Writting file')
writer = pd.ExcelWriter('output.xlsx')
big_frame.to_excel(writer,'Sheet1')
writer.save()

print('Done')