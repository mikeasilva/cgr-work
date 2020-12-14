# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 14:31:39 2019

@author: Michael Silva
"""
import pandas as pd
import sys
import requests

# Import modules located on H:/
sys.path.append(
    "H:/Data Warehouse/Community Indicators/Scripts to Create Community Indicators/"
)
import census
import presto

# Create the API "for string"
for_strings = {"geo_id": "&for=tract:*&in=state:42&in=county:011"}
# These are the names of the columns we want to keep
cols_to_keep = [
    "NAME",
    "CPovRate",
    "CPovRaw",
    "CPovStars",
    "PPovRate",
    "PPovRaw",
    "PovStars",
    "LangRate",
    "LangRaw",
    "LangStars",
    "SParRate",
    "SParRaw",
    "SParStars",
    "ForborRate",
    "ForborRaw",
    "ForborStars",
    "WrkPoorRate",
    "WrkPoorRaw",
    "WrkPoorStars",
    "VacantHURate",
    "VacantHURaw",
    "VacantHUStar",
    "MHI",
    "MHIStars",
    "HomeAfRate",
    "HomeAfStars",
    "RentAfRate",
    "RentAfStars",
    "HomeOwnRate",
    "HomeOwnStars",
    "DrvAloneRate",
    "DrvAloneRaw",
    "DrvAloneStars",
    "AvgTravel",
    "AvgTravelStars",
    "NoVehRate",
    "NoVehRaw",
    "NoVehStars",
]


def percent_indicator(acs_numerator, acs_denominator, scale_rate=True):
    """Creates a percentage indicator using ACS data

    Parameters:
    acs_numerator (list): Columns that should be aggregated to make the numerator
    acs_denominator (list): Columns that should be aggregated to make the denominator
    scale_rate (bool): Should the rate be multiplied by 100? (True by default)

    Returns:
    DataFrame: Returns data frame with count, count_moe, denominator, rate and reliability
    """
    acs_vars = presto.get_acs_vars(acs_numerator, acs_denominator)
    df = (
        api.reset()
        .set_api_endpoint("latest_acs_5_year")
        .set_api_variables(acs_vars)
        .get_data(asynchronous=False)
    )
    # Create the numerator
    temp = presto.aggregate_acs_data(df, acs_numerator, True)
    df["count"] = temp["est"]
    df["count_moe"] = temp["moe"]
    # Create the denominator
    temp = presto.aggregate_acs_data(df, acs_denominator, True)
    df["denominator"] = temp["est"]
    df["rate"] = df["count"] / df["denominator"]
    if scale_rate:
        df["rate"] = df["rate"] * 100
    df["reliability"] = presto.get_reliability(df)
    return df


def subset_cols(df, cols_to_keep):
    """Returns a data frame with a subset of the columns
    
    Parameters:
    df (DataFrame): Pandas data frame
    cols_to_keep (list): Columns you want to keep (doesn't have to be present)
    """
    return df[[x for x in list(df.columns) if x in cols_to_keep]].copy()


# Create Census API object
api = census.api()
# Get the API Settings
settings = api.settings()
# Set and forget
api.set_api_key(settings["api_key"]).set_for_strings(for_strings)


## CI_02010_US
print("CI_02010_US")
acs_numerator = [
    "B17001_004",
    "B17001_005",
    "B17001_006",
    "B17001_007",
    "B17001_008",
    "B17001_009",
    "B17001_018",
    "B17001_019",
    "B17001_020",
    "B17001_021",
    "B17001_022",
    "B17001_023",
]
acs_denominator = acs_numerator + [
    "B17001_033",
    "B17001_034",
    "B17001_035",
    "B17001_036",
    "B17001_037",
    "B17001_038",
    "B17001_047",
    "B17001_048",
    "B17001_049",
    "B17001_050",
    "B17001_051",
    "B17001_052",
]
df = percent_indicator(acs_numerator, acs_denominator)
df["CPovRaw"] = df["count"]
df["CPovRate"] = df["rate"]
df["CPovStars"] = df["reliability"]
df = subset_cols(df, cols_to_keep)

## CI_02020_US
print("CI_02020_US")
acs_numerator = ["B17010_011", "B17010_017", "B17010_031", "B17010_037"]
acs_denominator = acs_numerator + ["B17010_004", "B17010_024"]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["SParRate"] = temp["rate"]
temp["SParRaw"] = temp["count"]
temp["SParStars"] = temp["reliability"]
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_04009_US
print("CI_04009_US")
acs_numerator = ["B05002_013"]
acs_denominator = ["B05002_001"]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["ForborRate"] = temp["rate"]
temp["ForborRaw"] = temp["count"]
temp["ForborStars"] = temp["reliability"]
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_04010_US
print("CI_04010_US")
acs_numerator = [
    "B16004_004",
    "B16004_009",
    "B16004_014",
    "B16004_019",
    "B16004_026",
    "B16004_031",
    "B16004_036",
    "B16004_041",
    "B16004_048",
    "B16004_053",
    "B16004_058",
    "B16004_063",
]
acs_denominator = ["B16004_001"]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["LangRate"] = temp["rate"]
temp["LangRaw"] = temp["count"]
temp["LangStars"] = temp["reliability"]
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_08001_US
print("CI_08001_US")
acs_median = ["B19013_001"]
acs_vars = presto.get_acs_vars(acs_median)
temp = (
    api.reset()
    .set_api_endpoint("latest_acs_5_year")
    .set_api_variables(acs_vars)
    .get_data(asynchronous=False)
)
temp["count"] = temp[acs_vars[1]]
temp["count_moe"] = temp[acs_vars[2]]
temp["MHI"] = temp["count"]
temp["MHIStars"] = presto.get_reliability(temp)
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_08004_US
print("CI_08004_US")
acs_numerator = ["B17001_002"]
acs_denominator = ["B17001_001"]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["PPovRate"] = temp["rate"]
temp["PPovRaw"] = temp["count"]
temp["PovStars"] = temp["reliability"]
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_08009_US
print("CI_08009_US")
acs_numerator = ["B17005_005", "B17005_010"]
acs_denominator = ["B17005_001"]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["WrkPoorRate"] = temp["rate"]
temp["WrkPoorRaw"] = temp["count"]
temp["WrkPoorStars"] = temp["reliability"]
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_10025_US
print("CI_10025_US")
acs_numerator = ["B25002_003"]
acs_denominator = ["B25002_001"]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["VacantHURate"] = temp["rate"]
temp["VacantHURaw"] = temp["count"]
temp["VacantHUStar"] = temp["reliability"]
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_10002_US
print("CI_10002_US")
acs_numerator = ["B25003_002"]
acs_denominator = ["B25003_001"]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["HomeOwnRate"] = temp["rate"]
temp["HomeOwnStars"] = temp["reliability"]
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_10006_US
print("CI_10006_US")
acs_numerator = ["B25077_001"]
acs_denominator = ["B19013_001"]
temp = percent_indicator(acs_numerator, acs_denominator, False)
temp["HomeAfRate"] = temp["rate"]
temp["HomeAfStars"] = temp["reliability"]
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_10012_US
print("CI_10012_US")
acs_numerator = ["B25064_001"]
acs_denominator = ["B25119_003"]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["RentAfRate"] = ((temp["count"] * 12) / temp["denominator"]) * 100
temp["RentAfStars"] = temp["reliability"]
#temp.to_excel("CI_10012_US.xlsx")
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_13003_US
print("CI_13003_US")
acs_numerator = ["B08301_003"]
acs_denominator = [
    "B08301_002",
    "B08301_010",
    "B08301_016",
    "B08301_017",
    "B08301_018",
    "B08301_019",
    "B08301_020",
]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["DrvAloneRate"] = temp["rate"]
temp["DrvAloneRaw"] = temp["count"]
temp["DrvAloneStars"] = temp["reliability"]
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_13005_US
print("CI_13005_US")
acs_numerator = ["B08013_001"]
acs_denominator = ["B08134_001"]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["AvgTravel"] = temp["rate"] / 100
temp["AvgTravelStars"] = temp["reliability"]
#temp.to_csv("CI_13005_US.csv")
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

## CI_13006_US
print("CI_13006_US")
acs_numerator = ["B25044_003", "B25044_010"]
acs_denominator = ["B25044_001"]
temp = percent_indicator(acs_numerator, acs_denominator)
temp["NoVehRate"] = temp["rate"]
temp["NoVehRaw"] = temp["count"]
temp["NoVehStars"] = temp["reliability"]
temp = subset_cols(temp, cols_to_keep)
df = pd.merge(df, temp, on="NAME")

# Add in GEOID Vars
temp = requests.get("https://api.census.gov/data/2019/acs/acs5?get=NAME"+for_strings["geo_id"])
temp = temp.json()
cols = temp.pop(0)
temp = pd.DataFrame(temp, columns=cols)
temp["GEOID"] = temp["state"] + temp["county"] + temp["tract"]
temp = temp[["NAME", "GEOID"]]
df = pd.merge(df, temp, on="NAME")

df = df[cols_to_keep].rename(columns={"NAME": "Geography"})

df.to_excel("Census Tract Data.xlsx", index=False)

