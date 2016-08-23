# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:52:56 2016

@author: Michael Silva
"""
import pysal as ps
import pandas as pd
import os

# Thanks Ryan Hill
# https://gist.github.com/ryan-hill/f90b1c68f60d12baea81/
def dbf2DF(dbfile, upper=True): #Reads in DBF files and returns Pandas DF
    db = ps.open(dbfile) #Pysal to open DBF
    d = {col: db.by_col(col) for col in db.header} #Convert dbf to dictionary
    #pandasDF = pd.DataFrame(db[:]) #Convert to Pandas DF
    pandasDF = pd.DataFrame(d) #Convert to Pandas DF
    if upper == True: #Make columns uppercase if wanted
        pandasDF.columns = map(str.upper, db.header)
    db.close()
    return pandasDF

for file_name in os.listdir("."):
    if file_name.endswith('.dbf'):
        new_file_name = file_name.replace('.dbf','.xlsx')
        print("Converting "+file_name+" to "+new_file_name)
        df = dbf2DF(file_name)
        writer = pd.ExcelWriter(new_file_name, engine='xlsxwriter')
        df.to_excel(writer, file_name.replace('.dbf',''), index=False)
        writer.save()
