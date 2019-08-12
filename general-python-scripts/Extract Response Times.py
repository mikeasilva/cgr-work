# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 14:24:43 2019

@author: Michael
"""

import re
import numpy as np
import pandas as pd

text_files = ["phillipstonresponsetimes.txt", "TFD5YRRESPONSETIME.txt"]
data = []

ignore = ["Templeton Police Department Page:", "Selective Search From:", "Call Number Time Call Reason Action Priority", "Location", "ID: ", "Primary Id:", "Vicinity of:", "CHAPMAN, WILLIAM", "SMITH, ERIC", "DRUDI, TRAVIS", "POTTINGER, BLAKELEY", "SARNO, JOSEPH"]

convert_me = set()

for txt in text_files:
    current_date = None
    current_dow = None
    current_record_id = None
    with open(txt) as f:
        for line in f:
            include = True
            
            for i in ignore:
                if i in line:
                    include = False
                    
            if len(line.strip()) < 1:
                include = False
            
    
            if include:
                if "For Date:" in line:
                    date_parts = line.split(":")[1].split("-")
                    current_date = date_parts[0].strip()
                    current_dow = date_parts[1].strip()
                elif line[:3] in ["14-", "15-", "16-", "17-", "18-", "19-"]:
                    if current_record_id is not None:
                        # Save record
                        data.append(record)
                    current_record_id = line.split(" ")[0]
                    unit_count = 0
                elif "Fire Unit:" in line or "EMS Unit:" in line:
                    if unit_count > 0:
                        data.append(record)
                    unit_count += 1
                    record = {"ID": current_record_id, "Unit": line.split(":")[1].strip(), "Unit Count": unit_count, "File": txt}
                else:
                    line = line.strip().replace(" @ ", "@")
                    for time_parts in line.split(" "):
                        t = time_parts.split("-")
                        if "@" in t[1]:
                            record[t[0]] = t[1]. replace("@", " ")
                        else:
                            record[t[0]] = current_date + " " + t[1]
                        convert_me.add(t[0])
                

df = pd.DataFrame(data)

for c in convert_me:
    df[c] = pd.to_datetime(df[c])
    
df["Response Time"] = None
df["First Responder"] = 0
seen = set()
df = df.sort_values(["File", "Arvd", "Unit Count"])

for i in df.index:
    if not pd.isnull(df.at[i, "Arvd"]):
        
        df.at[i, "Response Time"] = df.at[i, "Arvd"] - df.at[i, "Disp"]
        df.at[i, "Response Time"] = df.at[i, "Response Time"] / np.timedelta64(1, "m")
        k = df.at[i, "File"] + df.at[i,"ID"]
        if k not in seen:
            df.at[i, "First Responder"] = 1
            seen.add(k)


df = df.sort_values(["File", "Disp", "Unit Count"]).reset_index(drop=True)

df.to_excel("Response Times.xlsx", engine="xlsxwriter", index=False)