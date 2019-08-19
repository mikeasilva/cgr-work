# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 09:16:52 2019

@author: Michael
"""

import pandas as pd
import numpy as np
import zipfile
import os


def get_estimates_and_errors(df, weight):
    """Calculates the estimate, standard error and margin of error of PUMS data

    Args:
        df (DataFrame): the pandas data frame of PUMS data.
        weight (str): the weighting column name (WGTP or PWGTP).
    Returns:
        estimate (int): The point estimate.
        se (int): The standard error of the estimate.
        moe (int): The margin of error of the estimate.
    """
    # Translate the weight into standard error weights
    # i.e. 'WGPT' to ['WGTP1', ..., 'WGTP80']
    se_weights = [weight + str(i) for i in range(1, 81)]
    # Calculate the point estimate
    estimate = df[[weight]].sum()[weight]
    # Calculate the standard error
    se = ((4 / 80) * ((df[se_weights].sum() - estimate) ** 2).sum()) ** 0.5
    # Calculate the margin of error
    moe = 1.645 * se
    # Convert to integers
    estimate = int(estimate)
    se = int(round(se, 0))
    moe = int(round(moe, 0))
    # Return the values
    return estimate, se, moe


def unzip(zip_file):
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(".")
        
        
def recode_hisp(val):
        if val == 1:
            return False
        else:
            return True
    
    
def recode_rac1p(val):
    if val == 1:
        return "White"
    elif val == 2:
        return "Black"
    elif val == 3 or val == 4 or val == 5:
        return "American Indian"
    elif val == 6:
        return "Asian"
    elif val == 7:
        return "Pacific Islander"
    elif val == 8:
        return "Some Other Race"
    elif val == 9:
        return "Two or More Races"
    else:
        return "Unknown"

def in_laborforce(val):
    return val in [1, 2, 3]

        
settings = {
    "Baltimore": {
        "puma": ["00801", "00802", "00803", "00804", "00805"],
        "zip_file": "csv_pmd.zip",
        "file_name": "psam_p24.csv",
    },
    "Boston": {
        "puma": ["03301", "03302", "03303", "03304", "03305"],
        "zip_file": "csv_pma.zip",
        "file_name": "psam_p25.csv",
    },
    "Buffalo": {
        "puma": ["01205", "01206"],
        "zip_file": "csv_pny.zip",
        "file_name": "psam_p36.csv",
    },
    "Clevland": {
        "puma": ["00906"],
        "zip_file": "csv_poh.zip",
        "file_name": "psam_p39.csv",
    },
    "Hartford": {
        "puma": ["00302"],
        "zip_file": "csv_pct.zip",
        "file_name": "psam_p09.csv",
    },
    "Indianapolis": {
        "puma": ["02301", "03202", "03203", "03204", "03205", "03206", "03207"],
        "zip_file": "csv_pin.zip",
        "file_name": "psam_p18.csv",
    },
    "San Diego": {
        "puma": [
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
        ],
        "zip_file": "csv_pca_small.zip",
        "file_name": "psam_p06_small.csv",
    },
    "Seatle": {
        "puma": ["11601", "11602", "11603", "11604", "11605"],
        "zip_file": "csv_pwa.zip",
        "file_name": "psam_p53.csv",
    },
    "Philadelphia": {
        "puma": [
            "03201",
            "03202",
            "03203",
            "03204",
            "03205",
            "03206",
            "03207",
            "03208",
            "03209",
            "03210",
            "03211",
        ],
        "zip_file": "csv_ppa.zip",
        "file_name": "psam_p42.csv",
    },
    "Connecticut": {
        "puma": None,
        "zip_file": "csv_pct.zip",
        "file_name": "psam_p09.csv",
    },
    "Indiana": {"puma": None, "zip_file": "csv_pin.zip", "file_name": "psam_p18.csv"},
    "Maryland": {"puma": None, "zip_file": "csv_pmd.zip", "file_name": "psam_p24.csv"},
    "Massachusetts": {
        "puma": None,
        "zip_file": "csv_pma.zip",
        "file_name": "psam_p25.csv",
    },
    "New York": {"puma": None, "zip_file": "csv_pny.zip", "file_name": "psam_p36.csv"},
    "Ohio": {"puma": None, "zip_file": "csv_poh.zip", "file_name": "psam_p39.csv"},
    "Pennsylvania": {
        "puma": None,
        "zip_file": "csv_ppa.zip",
        "file_name": "psam_p42.csv",
    },
    "Washington": {
        "puma": None,
        "zip_file": "csv_pwa.zip",
        "file_name": "psam_p53.csv",
    },
}
    
data= []

for place in list(settings.keys()): #["Buffalo"]:

    row = {"Place": place}

    s = settings[place]
    unzip(s["zip_file"])
    df = pd.read_csv(s["file_name"], low_memory=False)

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

    df = df[p_vars]

    if s["puma"] is not None:
        df = df[df["PUMA"].isin(s["puma"])]

    df["is_youth"] = np.logical_and(df.AGEP > 13, df.AGEP < 22)
    df["lt_hs"] = np.logical_and(np.logical_and(df.SCHL > 0, df.SCHL < 16), df.SCH == 1)
    #df["hs_plus"] = df.SCHL > 15
    df["school_denominator"] = np.logical_and(df.SCHL > 0, df.SCH == 1)
    df["in_poverty"] = np.logical_and(df.POVPIP > 0, df.POVPIP < 101)
    df["in_poverty_denominator"] = df.POVPIP > 0
    df["hispanic"] = df.HISP.apply(recode_hisp, 0)
    df["race"] = df.RAC1P.apply(recode_rac1p, 0)
    df["in_laborforce"] = df.ESR.apply(in_laborforce, 0)
    df["is_unemployed"] = df.ESR == 3

    estimate, se, moe = get_estimates_and_errors(df, "PWGTP")
    row["Population: Total"] = estimate
    print(place + " Total Population: " + str(estimate) + " +/- " + str(moe))

    estimate, se, moe = get_estimates_and_errors(df[df.is_youth], "PWGTP")
    row["Population: Youth"] = estimate
    print(place + " Youth Population: " + str(estimate) + " +/- " + str(moe))
    
    # Schooling
    estimate, se, moe = get_estimates_and_errors(df[df.lt_hs], "PWGTP")
    row["Less Than High School: Count - Total"] = estimate
    lt_hs = estimate
    print(place + " Less Than High School: " + str(estimate) + " +/- " + str(moe))
    estimate, se, moe = get_estimates_and_errors(df[df.school_denominator], "PWGTP")
    row["Less Than High School: Denominator - Total"] = estimate
    print(place + " Schooling Denominator: " + str(estimate) + " +/- " + str(moe))
    if estimate > 0:
        rate = lt_hs / estimate
    else:
        rate = None
    row["Less Than High School: Rate - Total"] = rate
    print(place + " Less Than High School Rate: " + str(rate))
    
    estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df.lt_hs, df.is_youth)], "PWGTP")
    row["Less Than High School: Count - Youth"] = estimate
    lt_hs = estimate
    print(place + " Less Than High School: " + str(estimate) + " +/- " + str(moe))
    estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df.school_denominator, df.is_youth)], "PWGTP")
    row["Less Than High School: Denominator - Youth"] = estimate
    print(place + " Youth Schooling Denominator: " + str(estimate) + " +/- " + str(moe))
    if estimate > 0:
        rate = lt_hs / estimate
    else:
        rate = None
    row["Less Than High School: Rate - Total"] = rate
    print(place + " Less Than High School Rate: " + str(rate))

    estimate, se, moe = get_estimates_and_errors(df[df.in_poverty], "PWGTP")
    row["Poverty: Count - Total"] = estimate
    pip = estimate
    print(
        place + " Living in Poverty: " + str(estimate) + " +/- " + str(moe)
    )
    estimate, se, moe = get_estimates_and_errors(df[df.in_poverty_denominator], "PWGTP")
    row["Poverty: Denominator - Total"] = estimate
    if estimate > 0:
        pov_rate = pip / estimate
    else:
        pov_rate = None
        
    print(
        place + " Living in Poverty Denominator: " + str(estimate) + " +/- " + str(moe)
    )
    print(place + " Poverty Rate: " + str(pov_rate))
    row["Poverty: Rate - Total"] = pov_rate

    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.in_poverty, df.is_youth)], "PWGTP"
    )
    row["Poverty: Count - Youth"] = estimate
    pip = estimate
    print(place + " Youth Living in Poverty: " + str(estimate) + " +/- " + str(moe))
    
    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.in_poverty_denominator, df.is_youth)], "PWGTP"
    )
    row["Poverty: Denominator - Youth"] = estimate
    if estimate > 0:
        pov_rate = pip / estimate
    else:
        pov_rate = None
    row["Poverty: Rate - Youth"] = pov_rate
    print(place + " Youth Living in Poverty Denominator: " + str(estimate) + " +/- " + str(moe))
    print(place + " Youth Poverty Rate: " + str(pov_rate))

    estimate, se, moe = get_estimates_and_errors(df[df.in_laborforce], "PWGTP")
    row["Unemployment: Labor Force - Total"] = estimate
    labor_force = estimate
    print(place + " in Labor Force: " + str(estimate) + " +/- " + str(moe))
    print(place + " Youth Poverty Rate: " + str(pov_rate))

    estimate, se, moe = get_estimates_and_errors(df[df.is_unemployed], "PWGTP")
    unemployment_rate = estimate / labor_force
    row["Unemployment: Count - Total"] = estimate
    row["Unemployment: Rate - Total"] = unemployment_rate
    print(place + " Unemployed: " + str(estimate) + " +/- " + str(moe))
    print(place + " Unemployment Rate: " + str(unemployment_rate))

    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.in_laborforce, df.is_youth)], "PWGTP"
    )
    row["Unemployment: Labor Force - Youth"] = estimate
    labor_force = estimate
    print(place + " Youth in Labor Force: " + str(estimate) + " +/- " + str(moe))

    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.is_unemployed, df.is_youth)], "PWGTP"
    )
    unemployment_rate = estimate / labor_force
    row["Unemployment: Count - Youth"] = estimate
    row["Unemployment: Rate - Youth"] = unemployment_rate
    print(place + " Youth Unemployed: " + str(estimate) + " +/- " + str(moe))
    print(place + " Youth Unemployment Rate: " + str(unemployment_rate))

    breakout = df.race.unique()
    breakout.sort()
    for b in breakout:
        df_filter = df["race"] == b
        # Population
        estimate, se, moe = get_estimates_and_errors(df[df_filter], "PWGTP")
        row["Population: Total - " + b] = estimate
        print(place + " " + b + " Population: " + str(estimate) + " +/- " + str(moe))

        estimate, se, moe = get_estimates_and_errors(
            df[np.logical_and(df_filter, df.is_youth)], "PWGTP"
        )
        row["Population: Youth - " + b] = estimate
        print(
            place + " " + b + " Youth Population: " + str(estimate) + " +/- " + str(moe)
        )

        # Poverty
        estimate, se, moe = get_estimates_and_errors(
            df[np.logical_and(df_filter, df.in_poverty)], "PWGTP"
        )
        row["Poverty: Count - Total - "+b] = estimate
        pip = estimate
        print(
            place
            + " "
            + b
            + " Living in Poverty: "
            + str(estimate)
            + " +/- "
            + str(moe)
        )
        
        estimate, se, moe = get_estimates_and_errors(
            df[np.logical_and(df_filter, df.in_poverty_denominator)], "PWGTP"
        )
        row["Poverty: Denominator - Total - "+b] = estimate
        if estimate > 0:
            pov_rate = pip / estimate
        else:
            pov_rate = None
            
        print(
            place
            + " "
            + b
            + " Living in Poverty Denominator: "
            + str(estimate)
            + " +/- "
            + str(moe)
        )
        row["Poverty: Rate - Total - "+b] = pov_rate
        print(place
            + " "
            + b
            + " Living in Poverty Rate: "
            + str(pov_rate))

        estimate, se, moe = get_estimates_and_errors(
            df[np.logical_and(df_filter, np.logical_and(df.in_poverty, df.is_youth))], "PWGTP"
        )
        row["Poverty: Count - Youth - "+b] = estimate
        pip = estimate
        print(
            place
            + " "
            + b
            + " Youth Living in Poverty: "
            + str(estimate)
            + " +/- "
            + str(moe)
        )
        
        estimate, se, moe = get_estimates_and_errors(
            df[np.logical_and(df_filter, np.logical_and(df.in_poverty_denominator, df.is_youth))], "PWGTP"
        )
        row["Poverty: Denominator - Youth - "+b] = estimate
        if estimate > 0:
            pov_rate = pip / estimate
        else:
            pov_rate = None
        print(
            place
            + " "
            + b
            + " Youth Living in Poverty Denominator: "
            + str(estimate)
            + " +/- "
            + str(moe)
        )
        row["Poverty: Rate - Youth - "+b] = pov_rate
        print(place
            + " "
            + b
            + " Youth Living in Poverty Rate: "
            + str(pov_rate))

        # Unemployment Rate
        estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df_filter, df.in_laborforce)], "PWGTP")
        row["Unemployment: Labor Force - Total - "+b] = estimate
        labor_force = estimate
        print(place + " " + b + " in Labor Force: " + str(estimate) + " +/- " + str(moe))
        print(place + " " + b + " Youth Poverty Rate: " + str(pov_rate))
    
        estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df_filter, df.is_unemployed)], "PWGTP")
        if labor_force > 0:
            unemployment_rate = estimate / labor_force
        else:
            unemployment_rate = None
        row["Unemployment: Count - Total - "+b] = estimate
        row["Unemployment: Rate - Total - "+b] = unemployment_rate
        print(place + " " + b + " Unemployed: " + str(estimate) + " +/- " + str(moe))
        print(place + " " + b + " Unemployment Rate: " + str(unemployment_rate))
    
        estimate, se, moe = get_estimates_and_errors(
            df[np.logical_and(df_filter, np.logical_and(df.in_laborforce, df.is_youth))], "PWGTP"
        )
        row["Unemployment: Labor Force - Youth - "+b] = estimate
        labor_force = estimate
        print(place + " " + b + " Youth in Labor Force: " + str(estimate) + " +/- " + str(moe))
    
        estimate, se, moe = get_estimates_and_errors(
            df[np.logical_and(df_filter, np.logical_and(df.is_unemployed, df.is_youth))], "PWGTP"
        )
        if labor_force > 0:
            unemployment_rate = estimate / labor_force
        else:
            unemployment_rate = None
        row["Unemployment: Count - Youth - "+b] = estimate
        row["Unemployment: Rate - Youth - "+b] = unemployment_rate
        print(place + " " + b + " Youth Unemployed: " + str(estimate) + " +/- " + str(moe))
        print(place + " " + b + " Youth Unemployment Rate: " + str(unemployment_rate))
        
        # Schooling
        estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df_filter, df.lt_hs)], "PWGTP")
        row["Less Than High School: Count - Total - "+b] = estimate
        lt_hs = estimate
        print(place + " " + b +" Less Than High School: " + str(estimate) + " +/- " + str(moe))
        estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df_filter, df.school_denominator)], "PWGTP")
        row["Less Than High School: Denominator - Total - "+b] = estimate
        print(place + " " + b +" Schooling Denominator: " + str(estimate) + " +/- " + str(moe))
        if estimate > 0:
            rate = lt_hs / estimate
        else:
            rate = None
        row["Less Than High School: Rate - Total - " + b] = rate
        print(place + " " + b +" Less Than High School Rate: " + str(rate))
        
        estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df_filter, np.logical_and(df.lt_hs, df.is_youth))], "PWGTP")
        row["Less Than High School: Count - Youth - "+b] = estimate
        lt_hs = estimate
        print(place + " " + b + " Less Than High School: " + str(estimate) + " +/- " + str(moe))
        estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df_filter, np.logical_and(df.school_denominator, df.is_youth))], "PWGTP")
        row["Less Than High School: Denominator - Youth - "+b] = estimate
        print(place + " " + b + " Youth Schooling Denominator: " + str(estimate) + " +/- " + str(moe))
        if estimate > 0:
            rate = lt_hs / estimate
        else:
            rate = None
        row["Less Than High School: Rate - Youth - "+b] = rate
        print(place + " " + b + " Youth Less Than High School Rate: " + str(rate))


    estimate, se, moe = get_estimates_and_errors(df[df.hispanic], "PWGTP")
    row["Population: Total - Hispanic"] = estimate
    print(place + " Hispanic Population: " + str(estimate) + " +/- " + str(moe))
    
    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.hispanic, df.is_youth)], "PWGTP"
    )
    row["Population: Youth - Hispanic"] = estimate
    print(place + " Hispanic Youth Population: " + str(estimate) + " +/- " + str(moe))

    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.hispanic, df.in_poverty)], "PWGTP"
    )
    
    row["Poverty: Count - Total - Hispanic"] = estimate
    pip = estimate
    print(place + " Hispanic Living in Poverty: " + str(estimate) + " +/- " + str(moe))
    
    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.hispanic, df.in_poverty_denominator)], "PWGTP"
    )
    if estimate > 0:
        pov_rate = pip / estimate
    else:
        pov_rate = None
    row["Poverty: Denominator - Total - Hispanic"] = estimate
    print(place + " Hispanic Living in Poverty Denominator: " + str(estimate) + " +/- " + str(moe))
    row["Poverty: Rate - Total - Hispanic"] = pov_rate

    

    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.hispanic, np.logical_and(df.in_poverty, df.is_youth))], "PWGTP"
    )
    row["Poverty: Count - Youth - Hispanic"] = estimate
    pip = estimate
    print(
        place
        + " Hispanic Youth Living in Poverty: "
        + str(estimate)
        + " +/- "
        + str(moe)
    )
    
    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.hispanic, np.logical_and(df.in_poverty_denominator, df.is_youth))], "PWGTP"
    )
    row["Poverty: Denominator - Youth - Hispanic"] = estimate
    if estimate > 0:
        pov_rate = pip / estimate
    else:
        pov_rate = None
    print(
        place
        + " Hispanic Youth Living in Poverty Denominator: "
        + str(estimate)
        + " +/- "
        + str(moe)
    )
    row["Poverty: Rate - Youth - Hispanic"] = pov_rate

    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.hispanic, df.in_laborforce)], "PWGTP"
    )
    row["Unemployment: Labor Force - Total - Hispanic"] = estimate
    labor_force = estimate
    print(place + " Hispanic in Labor Force: " + str(estimate) + " +/- " + str(moe))

    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.hispanic, df.is_unemployed)], "PWGTP"
    )
    if labor_force > 0:
        unemployment_rate = estimate / labor_force
    else:
        unemployment_rate = None
    row["Unemployment: Count - Total - Hispanic"] = estimate
    row["Unemployment: Rate - Total - Hispanic"] = unemployment_rate
    print(place + " Hispanic Unemployed: " + str(estimate) + " +/- " + str(moe))
    print(place + " Hispanic Unemployment Rate: " + str(unemployment_rate))

    ## Youth Unemployment Rates
    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.hispanic, np.logical_and(df.in_laborforce, df.is_youth))], "PWGTP"
    )
    row["Unemployment: Labor Force - Youth - Hispanic"] = estimate
    labor_force = estimate
    print(
        place + " Hispanic Youth in Labor Force: " + str(estimate) + " +/- " + str(moe)
    )

    estimate, se, moe = get_estimates_and_errors(
        df[np.logical_and(df.hispanic, np.logical_and(df.is_unemployed, df.is_youth))], "PWGTP"
    )
    if labor_force > 0:
        unemployment_rate = estimate / labor_force
    else:
        unemployment_rate = None
    row["Unemployment: Count - Youth - Hispanic"] = estimate
    row["Unemployment: Rate - Youth - Hispanic"] = unemployment_rate
    print(place + " Hispanic Youth Unemployed: " + str(estimate) + " +/- " + str(moe))
    print(place + " Hispanic Youth Unemployment Rate: " + str(unemployment_rate))
    
    
    
    estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df.hispanic, df.lt_hs)], "PWGTP")
    row["Less Than High School: Count - Total - Hispanic"] = estimate
    lt_hs = estimate
    print(place + " Hispanic Less Than High School: " + str(estimate) + " +/- " + str(moe))
    estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df.hispanic, df.school_denominator)], "PWGTP")
    row["Less Than High School: Denominator - Total - Hispanic"] = estimate
    print(place + " Hispanic Schooling Denominator: " + str(estimate) + " +/- " + str(moe))
    if estimate > 0:
        rate = lt_hs / estimate
    else:
        rate = None
    row["Less Than High School: Rate - Total - Hispanic"] = rate
    print(place + " Hispanic Less Than High School Rate: " + str(rate))
    
    estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df.hispanic, np.logical_and(df.lt_hs, df.is_youth))], "PWGTP")
    row["Less Than High School: Count - Youth - Hispanic"] = estimate
    lt_hs = estimate
    print(place + " Less Than High School: " + str(estimate) + " +/- " + str(moe))
    estimate, se, moe = get_estimates_and_errors(df[np.logical_and(df.hispanic, np.logical_and(df.school_denominator, df.is_youth))], "PWGTP")
    row["Less Than High School: Denominator - Youth - Hispanic"] = estimate
    print(place + " Hispanic Youth Schooling Denominator: " + str(estimate) + " +/- " + str(moe))
    if estimate > 0:
        rate = lt_hs / estimate
    else:
        rate = None
    row["Less Than High School: Rate - Youth - Hispanic"] = rate
    print(place + " Hispanic Less Than High School Rate: " + str(rate))
        

    os.remove(s["file_name"])
    os.remove("ACS2013_2017_PUMS_README.pdf")

    data.append(row)
    
    
df = pd.DataFrame(data)
cols = list(df.columns)
cols.remove("Place")
cols.sort()
cols = ["Place"] + cols
df = df[cols]
df.to_excel("data.xlsx", engine="xlsxwriter", index=False)
