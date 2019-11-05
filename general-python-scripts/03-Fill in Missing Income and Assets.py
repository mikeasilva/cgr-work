# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:24:26 2019

@author: Michael Silva
"""
import requests
import pandas as pd
import json


def extract_from_xml(x):
    x = x.replace("</", ">")
    x = x.split(">")
    return x[1]


def handle_990(row, xml):
    data = {"EIN": row["EIN"], "FORM_TYPE": row["FormType"], "URL": row["URL"]}
    for line in r.text.splitlines():
        if "<TaxYear>" in line or "<TaxYr>" in line:
            data["TAX_YEAR"] = int(extract_from_xml(line))
        if "<TotalRevenueCurrentYear>" in line or "<CYTotalRevenueAmt>" in line:
            data["TOTAL_REV"] = int(extract_from_xml(line))
        if "<TotalExpensesCurrentYear>" in line or "<CYTotalExpensesAmt>" in line:
            data["TOTAL_EXP"] = int(extract_from_xml(line))
        if (
            "<SalariesEtcCurrentYear>" in line
            or "<CYSalariesCompEmpBnftPaidAmt>" in line
        ):
            data["TOTAL_SALARIES"] = int(extract_from_xml(line))
        if "<TotalNbrEmployees>" in line or "<TotalEmployeeCnt>" in line:
            data["TOTAL_EMPLOYEES"] = int(extract_from_xml(line))
        if "<TotalNbrVolunteers>" in line or "<TotalVolunteersCnt>" in line:
            data["TOTAL_VOLUNTEERS"] = int(extract_from_xml(line))
        if "<TotalAssetsEOY>" in line or "<TotalAssetsEOYAmt>" in line:
            data["TOTAL_EOY_ASSETS"] = int(extract_from_xml(line))
        if "<TaxPeriodBeginDate>" in line or "<TaxPeriodBeginDt>" in line:
            data["TAX_PERIOD_START_DATE"] = extract_from_xml(line)
        if "<TaxPeriodEndDate>" in line or "<TaxPeriodEndDt>" in line:
            data["TAX_PERIOD_END_DATE"] = extract_from_xml(line)
    return data


def handle_990EZ(row, xml):
    data = {"EIN": row["EIN"], "FORM_TYPE": row["FormType"], "URL": row["URL"]}
    look_for_assets = False
    for line in r.text.splitlines():
        if "<Form990TotalAssetsGrp>" in line:
            look_for_assets = True
        if "<TaxYear>" in line or "<TaxYr>" in line:
            data["TAX_YEAR"] = int(extract_from_xml(line))
        if "<TotalRevenue>" in line or "<TotalRevenueAmt>" in line:
            data["TOTAL_REV"] = int(extract_from_xml(line))
        if "<TotalExpenses>" in line or "<TotalExpensesAmt>" in line:
            data["TOTAL_EXP"] = int(extract_from_xml(line))
        if (
            "<SalariesOtherCompEmplBenefits>" in line
            or "<SalariesOtherCompEmplBnftAmt>" in line
        ):
            data["TOTAL_SALARIES"] = int(extract_from_xml(line))
        if "<TotalAssets EOY>" in line or (look_for_assets and "<EOYAmt>" in line):
            data["TOTAL_EOY_ASSETS"] = int(extract_from_xml(line))
            look_for_assets = False
        if "<TaxPeriodBeginDate>" in line or "<TaxPeriodBeginDt>" in line:
            data["TAX_PERIOD_START_DATE"] = extract_from_xml(line)
        if "<TaxPeriodEndDate>" in line or "<TaxPeriodEndDt>" in line:
            data["TAX_PERIOD_END_DATE"] = extract_from_xml(line)
    return data


def handle_990PF(row, xml):
    data = {"EIN": row["EIN"], "FORM_TYPE": row["FormType"], "URL": row["URL"]}
    for line in r.text.splitlines():
        if "<TaxYr>" in line or "<TaxYear>" in line:
            data["TAX_YEAR"] = int(extract_from_xml(line))
        if (
            "<TotalIncomeProducingActyAmt>" in line
            or "<TotalRevenueAndExpenses>" in line
        ):
            data["TOTAL_REV"] = int(extract_from_xml(line))
        if (
            "<TotalExpensesRevAndExpnssAmt>" in line
            or "<TotalExpensesRevAndExpnss>" in line
        ):
            data["TOTAL_EXP"] = int(extract_from_xml(line))
        if "<TotalAssetsEOYAmt>" in line or "<TotalAssetsEOY>" in line:
            data["TOTAL_EOY_ASSETS"] = int(extract_from_xml(line))
        if "<TaxPeriodBeginDate>" in line or "<TaxPeriodBeginDt>" in line:
            data["TAX_PERIOD_START_DATE"] = extract_from_xml(line)
        if "<TaxPeriodEndDate>" in line or "<TaxPeriodEndDt>" in line:
            data["TAX_PERIOD_END_DATE"] = extract_from_xml(line)
    return data


holes = list()
filler = []

df = pd.read_excel("Select Non-Profits List.xlsx", dtype={"EIN": object})
for index, row in df.iterrows():
    if row["FILER"] == "N":
        holes.append(row["EIN"])
print("There are " + str(len(holes)) + " holes to fill...")

for year in range(2019, 2012, -1):
    url = "https://s3.amazonaws.com/irs-form-990/index_" + str(year) + ".json"
    print("Downloading " + str(year) + " index...")
    r = requests.get(url)
    print("Searching data...")
    data = json.loads(r.text)
    key = list(data.keys())[0]
    for row in data[key]:
        if row["EIN"] in holes:
            print("Scrapping " + row["URL"] + "...")
            r = requests.get(row["URL"])
            form_type = row["FormType"]
            if form_type == "990":
                filler.append(handle_990(row, r.content))
            elif form_type == "990EZ":
                filler.append(handle_990EZ(row, r.content))
            else:
                filler.append(handle_990PF(row, r.content))
            holes.remove(row["EIN"])
            print("There are " + str(len(holes)) + " holes left to fill...")

df = pd.DataFrame(filler)
df.to_excel("holes.xlsx", index=False)