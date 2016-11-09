# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 11:22:02 2016

@author: Michael Silva
"""

import glob
import pandas as pd
import sqlite3 as db

con = db.connect("data.sqlite")

all_files = glob.glob("*.csv")

for file_ in all_files:
    print("Processing "+file_)
    df = pd.read_csv(file_)
    df.to_sql('data', con, if_exists='append', index=False)
    
con.commit()
con.close()
print("Done")