# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 11:52:51 2019

@author: Michael
"""

import pandas as pd
import zipfile
import os

def unzip(zip_file):
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(".")
        
keep_me = [
            "07308",
            "07309",
            "07310",
            "07311",
            "07312",
            "07314",
            "07315",
            "07316",
            "07317",
            "07318",
        ]

chunksize = 10000

data = []

unzip("csv_pca.zip")

for chunk in pd.read_csv("psam_p06.csv", low_memory = False, chunksize = chunksize):
    p_vars = [
        "SERIALNO",
        "AGEP",
        "ESR",
        "HISP",
        "POVPIP",
        "PUMA",
        "RAC1P",
        "SCH",
        "SCHL",
        "PWGTP",
        "PWGTP1",
        "PWGTP2",
        "PWGTP3",
        "PWGTP4",
        "PWGTP5",
        "PWGTP6",
        "PWGTP7",
        "PWGTP8",
        "PWGTP9",
        "PWGTP10",
        "PWGTP11",
        "PWGTP12",
        "PWGTP13",
        "PWGTP14",
        "PWGTP15",
        "PWGTP16",
        "PWGTP17",
        "PWGTP18",
        "PWGTP19",
        "PWGTP20",
        "PWGTP21",
        "PWGTP22",
        "PWGTP23",
        "PWGTP24",
        "PWGTP25",
        "PWGTP26",
        "PWGTP27",
        "PWGTP28",
        "PWGTP29",
        "PWGTP30",
        "PWGTP31",
        "PWGTP32",
        "PWGTP33",
        "PWGTP34",
        "PWGTP35",
        "PWGTP36",
        "PWGTP37",
        "PWGTP38",
        "PWGTP39",
        "PWGTP40",
        "PWGTP41",
        "PWGTP42",
        "PWGTP43",
        "PWGTP44",
        "PWGTP45",
        "PWGTP46",
        "PWGTP47",
        "PWGTP48",
        "PWGTP49",
        "PWGTP50",
        "PWGTP51",
        "PWGTP52",
        "PWGTP53",
        "PWGTP54",
        "PWGTP55",
        "PWGTP56",
        "PWGTP57",
        "PWGTP58",
        "PWGTP59",
        "PWGTP60",
        "PWGTP61",
        "PWGTP62",
        "PWGTP63",
        "PWGTP64",
        "PWGTP65",
        "PWGTP66",
        "PWGTP67",
        "PWGTP68",
        "PWGTP69",
        "PWGTP70",
        "PWGTP71",
        "PWGTP72",
        "PWGTP73",
        "PWGTP74",
        "PWGTP75",
        "PWGTP76",
        "PWGTP77",
        "PWGTP78",
        "PWGTP79",
        "PWGTP80",
    ]

    chunk = chunk[p_vars]
    chunk = chunk[chunk["PUMA"].isin(keep_me)]
    data.append(chunk)
    
df = pd.concat(data)
df.to_csv("psam_p06_small.csv", index=False)

with zipfile.ZipFile("csv_pca_small.zip", "w") as z:
   z.write("psam_p06_small.csv")
   z.write("ACS2013_2017_PUMS_README.pdf")
   
os.remove("psam_p06.csv")
os.remove("ACS2013_2017_PUMS_README.pdf")