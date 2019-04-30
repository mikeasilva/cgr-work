# This file creates the model JSON file from the excel spreadsheet

import pandas as pd
import json

df = pd.read_excel(
    "G:/2019 Projects/915-ASBO Economic Impact/Project Data/ASBO Model.xlsx",
    sheet_name="Construction_Model",
    converters={"BEDS Code":str}
)

model = dict()

for index, row in df.iterrows():
    model[row["BEDS Code"]] = dict(row)


with open("model.json", "w") as fp:
    json.dump(model, fp)
