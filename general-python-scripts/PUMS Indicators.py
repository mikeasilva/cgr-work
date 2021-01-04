# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 08:25:00 2020

@author: Michael
"""

import requests
import json
import pandas as pd

# ACS Year
acs_year = "2018"

file_name = "PUMS Data.xlsx"

# Geography codes and filters
geos = {
    "US": False,
    "NYS": "0400000US36",
    "Rochester": "7950000US3600902,7950000US3600903",
    "Monroe": "7950000US3600902,7950000US3600903,7950000US3600904,7950000US3600905",
    "Livingston Wyoming": "7950000US3601300",
    "Genesee Orleans": "7950000US3601000",
    "Ontario Yates": "7950000US3601400",
    "Wayne Seneca": "7950000US3600800",
    "Bronx": "7950000US3603701,7950000US3603702,7950000US3603703,7950000US3603704,7950000US3603705,7950000US3603706,7950000US3603707,7950000US3603708,7950000US3603709,7950000US3603710",
    "Manhattan": "7950000US3603801,7950000US3603802,7950000US3603803,7950000US3603804,7950000US3603805,7950000US3603806,7950000US3603807,7950000US3603808,7950000US3603809,7950000US3603810",
    "Kings": "7950000US3604001,7950000US3604002,7950000US3604003,7950000US3604004,7950000US3604005,7950000US3604006,7950000US3604007,7950000US3604008,7950000US3604009,7950000US3604010,7950000US3604011,7950000US3604012,7950000US3604013,7950000US3604014,7950000US3604015,7950000US3604016,7950000US3604017,7950000US3604018",
    "Queens": "7950000US3604101,7950000US3604102,7950000US3604103,7950000US3604104,7950000US3604105,7950000US3604106,7950000US3604107,7950000US3604108,7950000US3604109,7950000US3604110,7950000US3604111,7950000US3604112,7950000US3604113,7950000US3604114",
    "Richmond": "7950000US3603901,7950000US3603902,7950000US3603903",    
    #"ROS": "7950000US3600100,7950000US3600200,7950000US3600300,7950000US3600401,7950000US3600402,7950000US3600403,7950000US3600500,7950000US3600600,7950000US3600701,7950000US3600702,7950000US3600703,7950000US3600704,7950000US3600800,7950000US3600901,7950000US3600902,7950000US3600903,7950000US3600904,7950000US3600905,7950000US3600906,7950000US3601000,7950000US3601101,7950000US3601102,7950000US3601201,7950000US3601202,7950000US3601203,7950000US3601204,7950000US3601205,7950000US3601206,7950000US3601207,7950000US3601300,7950000US3601400,7950000US3601500,7950000US3601600,7950000US3601700,7950000US3601801,7950000US3601802,7950000US3601900,7950000US3602001,7950000US3602002,7950000US3602100,7950000US3602201,7950000US3602202,7950000US3602203,7950000US3602300,7950000US3602401,7950000US3602402,7950000US3602500,7950000US3602600,7950000US3602701,7950000US3602702,7950000US3602801,7950000US3602802,7950000US3602901,7950000US3602902,7950000US3602903,7950000US3603001,7950000US3603002,7950000US3603003,7950000US3603101,7950000US3603102,7950000US3603103,7950000US3603104,7950000US3603105,7950000US3603106,7950000US3603107,7950000US3603201,7950000US3603202,7950000US3603203,7950000US3603204,7950000US3603205,7950000US3603206,7950000US3603207,7950000US3603208,7950000US3603209,7950000US3603210,7950000US3603211,7950000US3603212,7950000US3603301,7950000US3603302,7950000US3603303,7950000US3603304,7950000US3603305,7950000US3603306,7950000US3603307,7950000US3603308,7950000US3603309,7950000US3603310,7950000US3603311,7950000US3603312,7950000US3603313"
}


def get_income_by_race_ethnicity(acs_year, ucgid=False, renters=False):
    # Income Labels
    labels = pd.DataFrame(
        [
            ["1", "A - Less than $10,000"],
            ["2", "B - $10,000 to $14,999"],
            ["3", "C - $15,000 to $19,999"],
            ["4", "D - $20,000 to $24,999"],
            ["5", "E - $25,000 to $29,999"],
            ["6", "F - $30,000 to $34,999"],
            ["7", "G - $35,000 to $39,999"],
            ["8", "H - $40,000 to $44,999"],
            ["9", "I - $45,000 to $49,999"],
            ["10", "J - $50,000 to $59,999"],
            ["11", "K - $60,000 to $74,999"],
            ["12", "L - $75,000 to $99,999"],
            ["13", "M - $100,000 to $124,999"],
            ["14", "N - $125,000 to $149,999"],
            ["15", "O - $150,000 to $199,999"],
            ["16", "P - $200,000 or more"],
            ["17", "Z - Not Elsewhere Classified (nec.)"],
        ],
        columns=[0, "Label"],
    )
    # Get Income by Race
    # Example at https://data.census.gov/mdat/#/search?ds=ACSPUMS5Y2018&vv=HINCP&cv=HISP_RC1&rv=HINCP_RC1&nv=HISP(02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24)&wt=WGTP&HISP_RC1=%7B%22S%22%3A%22Recoded%20detailed%20Hispanic%20origin%20recode%22%2C%22R%22%3A%22HISP%22%2C%22W%22%3A%22PWGTP%22%2C%22V%22%3A%5B%5B%2202%2C03%2C04%2C05%2C06%2C07%2C08%2C09%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%22%2C%22D%20-%20Hispanic%22%5D%5D%7D&HINCP_RC1=%7B%22S%22%3A%22Household%20income%20%2528past%2012%20months%2C%20use%20ADJINC%20to%20adjust%20HINCP%20to%20constant%20dollars%2529%20recode%22%2C%22R%22%3A%22HINCP%22%2C%22W%22%3A%22WGTP%22%2C%22V%22%3A%5B%5B%22-59998%3A-1%2C1%3A9999%2C-59999%2C0%22%2C%22A%20-%20Less%20than%20%2410%2C000%22%5D%2C%5B%2210000%3A14999%22%2C%22B%20-%20%2410%2C000%20to%20%2414%2C999%22%5D%2C%5B%2215000%3A19999%22%2C%22C%20-%20%2415%2C000%20to%20%2419%2C999%22%5D%2C%5B%2220000%3A24999%22%2C%22D%20-%20%2420%2C000%20to%20%2424%2C999%22%5D%2C%5B%2225000%3A29999%22%2C%22E%20-%20%2425%2C000%20to%20%2429%2C999%22%5D%2C%5B%2230000%3A34999%22%2C%22F%20-%20%2430%2C000%20to%20%2434%2C999%22%5D%2C%5B%2235000%3A39999%22%2C%22G%20-%20%2435%2C000%20to%20%2439%2C999%22%5D%2C%5B%2240000%3A44999%22%2C%22H%20-%20%2440%2C000%20to%20%2444%2C999%22%5D%2C%5B%2245000%3A49999%22%2C%22I%20-%20%2445%2C000%20to%20%2449%2C999%22%5D%2C%5B%2250000%3A59999%22%2C%22J%20-%20%2450%2C000%20to%20%2459%2C999%22%5D%2C%5B%2260000%3A74999%22%2C%22K%20-%20%2460%2C000%20to%20%2474%2C999%22%5D%2C%5B%2275000%3A99999%22%2C%22L%20-%20%2475%2C000%20to%20%2499%2C999%22%5D%2C%5B%22100000%3A124999%22%2C%22M%20-%20%24100%2C000%20to%20%24124%2C999%22%5D%2C%5B%22125000%3A149999%22%2C%22N%20-%20%24125%2C000%20to%20%24149%2C999%22%5D%2C%5B%22150000%3A199999%22%2C%22O%20-%20%24150%2C000%20to%20%24199%2C999%22%5D%2C%5B%22200000%3A99999999%22%2C%22P%20-%20%24200%2C000%20or%20more%22%5D%2C%5B%22-60000%22%2C%22Z%20-%20Not%20Elsewhere%20Classified%20%2528nec.%2529%22%5D%5D%7D
    api_url = (
        "https://api.census.gov/data/"
        + acs_year
        + "/acs/acs5/pums?tabulate=weight(WGTP)&col+RAC1P_RC1&row+HINCP_RC1"
    )
    if ucgid is not False:
        api_url += "&ucgid=" + ucgid
    if renters is not False:
        api_url += "&TEN=3&TEN=4&"
    api_url += "&recode+RAC1P_RC1=%7B%22b%22:%22RAC1P%22,%22d%22:%5B%5B%221%22%5D,%5B%222%22%5D,%5B%226%22%5D%5D%7D&recode+HINCP_RC1=%7B%22b%22:%22HINCP%22,%22d%22:%5B%5B%7B%22mn%22:-59998,%22mx%22:-1%7D,%7B%22mn%22:1,%22mx%22:9999%7D,%22-59999%22,%220%22%5D,%5B%7B%22mn%22:10000,%22mx%22:14999%7D%5D,%5B%7B%22mn%22:15000,%22mx%22:19999%7D%5D,%5B%7B%22mn%22:20000,%22mx%22:24999%7D%5D,%5B%7B%22mn%22:25000,%22mx%22:29999%7D%5D,%5B%7B%22mn%22:30000,%22mx%22:34999%7D%5D,%5B%7B%22mn%22:35000,%22mx%22:39999%7D%5D,%5B%7B%22mn%22:40000,%22mx%22:44999%7D%5D,%5B%7B%22mn%22:45000,%22mx%22:49999%7D%5D,%5B%7B%22mn%22:50000,%22mx%22:59999%7D%5D,%5B%7B%22mn%22:60000,%22mx%22:74999%7D%5D,%5B%7B%22mn%22:75000,%22mx%22:99999%7D%5D,%5B%7B%22mn%22:100000,%22mx%22:124999%7D%5D,%5B%7B%22mn%22:125000,%22mx%22:149999%7D%5D,%5B%7B%22mn%22:150000,%22mx%22:199999%7D%5D,%5B%7B%22mn%22:200000,%22mx%22:99999999%7D%5D,%5B%22-60000%22%5D%5D%7D"
    # Request the data
    response = requests.get(api_url)
    # Read the JSON
    j = json.loads(response.content)
    # Remove the header
    j.pop(0)
    # Create a data frame
    race_df = pd.DataFrame(j)
    race_df.columns = ["A - White alone", "B - Black alone", "C - Asian alone", 0]
    race_df = pd.merge(labels, race_df).reset_index(drop=True)
    # Get Income by Ethnicity
    # Example at https://data.census.gov/mdat/#/search?ds=ACSPUMS5Y2018&vv=HINCP&cv=HISP_RC1&rv=HINCP_RC1&nv=HISP(02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24)&wt=WGTP&HISP_RC1=%7B%22S%22%3A%22Recoded%20detailed%20Hispanic%20origin%20recode%22%2C%22R%22%3A%22HISP%22%2C%22W%22%3A%22PWGTP%22%2C%22V%22%3A%5B%5B%2202%2C03%2C04%2C05%2C06%2C07%2C08%2C09%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%22%2C%22D%20-%20Hispanic%22%5D%5D%7D&HINCP_RC1=%7B%22S%22%3A%22Household%20income%20%2528past%2012%20months%2C%20use%20ADJINC%20to%20adjust%20HINCP%20to%20constant%20dollars%2529%20recode%22%2C%22R%22%3A%22HINCP%22%2C%22W%22%3A%22WGTP%22%2C%22V%22%3A%5B%5B%22-59998%3A-1%2C1%3A9999%2C-59999%2C0%22%2C%22A%20-%20Less%20than%20%2410%2C000%22%5D%2C%5B%2210000%3A14999%22%2C%22B%20-%20%2410%2C000%20to%20%2414%2C999%22%5D%2C%5B%2215000%3A19999%22%2C%22C%20-%20%2415%2C000%20to%20%2419%2C999%22%5D%2C%5B%2220000%3A24999%22%2C%22D%20-%20%2420%2C000%20to%20%2424%2C999%22%5D%2C%5B%2225000%3A29999%22%2C%22E%20-%20%2425%2C000%20to%20%2429%2C999%22%5D%2C%5B%2230000%3A34999%22%2C%22F%20-%20%2430%2C000%20to%20%2434%2C999%22%5D%2C%5B%2235000%3A39999%22%2C%22G%20-%20%2435%2C000%20to%20%2439%2C999%22%5D%2C%5B%2240000%3A44999%22%2C%22H%20-%20%2440%2C000%20to%20%2444%2C999%22%5D%2C%5B%2245000%3A49999%22%2C%22I%20-%20%2445%2C000%20to%20%2449%2C999%22%5D%2C%5B%2250000%3A59999%22%2C%22J%20-%20%2450%2C000%20to%20%2459%2C999%22%5D%2C%5B%2260000%3A74999%22%2C%22K%20-%20%2460%2C000%20to%20%2474%2C999%22%5D%2C%5B%2275000%3A99999%22%2C%22L%20-%20%2475%2C000%20to%20%2499%2C999%22%5D%2C%5B%22100000%3A124999%22%2C%22M%20-%20%24100%2C000%20to%20%24124%2C999%22%5D%2C%5B%22125000%3A149999%22%2C%22N%20-%20%24125%2C000%20to%20%24149%2C999%22%5D%2C%5B%22150000%3A199999%22%2C%22O%20-%20%24150%2C000%20to%20%24199%2C999%22%5D%2C%5B%22200000%3A99999999%22%2C%22P%20-%20%24200%2C000%20or%20more%22%5D%2C%5B%22-60000%22%2C%22Z%20-%20Not%20Elsewhere%20Classified%20%2528nec.%2529%22%5D%5D%7D
    api_url = (
        "https://api.census.gov/data/"
        + acs_year
        + "/acs/acs5/pums?tabulate=weight(WGTP)&col+HISP_RC1&row+HINCP_RC1"
    )
    if ucgid is not False:
        api_url += "&ucgid=" + ucgid
    if renters is not False:
        api_url += "&TEN=3&TEN=4&"
    api_url += "&HISP=02&HISP=03&HISP=04&HISP=05&HISP=06&HISP=07&HISP=08&HISP=09&HISP=10&HISP=11&HISP=12&HISP=13&HISP=14&HISP=15&HISP=16&HISP=17&HISP=18&HISP=19&HISP=20&HISP=21&HISP=22&HISP=23&HISP=24&recode+HISP_RC1=%7B%22b%22:%22HISP%22,%22d%22:%5B%5B%2202%22,%2203%22,%2204%22,%2205%22,%2206%22,%2207%22,%2208%22,%2209%22,%2210%22,%2211%22,%2212%22,%2213%22,%2214%22,%2215%22,%2216%22,%2217%22,%2218%22,%2219%22,%2220%22,%2221%22,%2222%22,%2223%22,%2224%22%5D%5D%7D&recode+HINCP_RC1=%7B%22b%22:%22HINCP%22,%22d%22:%5B%5B%7B%22mn%22:-59998,%22mx%22:-1%7D,%7B%22mn%22:1,%22mx%22:9999%7D,%22-59999%22,%220%22%5D,%5B%7B%22mn%22:10000,%22mx%22:14999%7D%5D,%5B%7B%22mn%22:15000,%22mx%22:19999%7D%5D,%5B%7B%22mn%22:20000,%22mx%22:24999%7D%5D,%5B%7B%22mn%22:25000,%22mx%22:29999%7D%5D,%5B%7B%22mn%22:30000,%22mx%22:34999%7D%5D,%5B%7B%22mn%22:35000,%22mx%22:39999%7D%5D,%5B%7B%22mn%22:40000,%22mx%22:44999%7D%5D,%5B%7B%22mn%22:45000,%22mx%22:49999%7D%5D,%5B%7B%22mn%22:50000,%22mx%22:59999%7D%5D,%5B%7B%22mn%22:60000,%22mx%22:74999%7D%5D,%5B%7B%22mn%22:75000,%22mx%22:99999%7D%5D,%5B%7B%22mn%22:100000,%22mx%22:124999%7D%5D,%5B%7B%22mn%22:125000,%22mx%22:149999%7D%5D,%5B%7B%22mn%22:150000,%22mx%22:199999%7D%5D,%5B%7B%22mn%22:200000,%22mx%22:99999999%7D%5D,%5B%22-60000%22%5D%5D%7D"
    response = requests.get(api_url)
    # Read the JSON
    j = json.loads(response.content)
    # Remove the header
    j.pop(0)
    # Create a data frame
    ethn_df = pd.DataFrame(j)
    ethn_df.columns = ["D - Hispanic", 0]
    ethn_df = pd.merge(labels, ethn_df).reset_index(drop=True)
    # Put them all together
    df = pd.merge(race_df, ethn_df).drop([0], axis=1)
    return df

def get_rent_by_race_ethnicity(acs_year, ucgid=False):
    # Rent Labels
    labels = pd.DataFrame(
        [
            ["1", "A - Less than $100"],
            ["2", "B - $100 to $149"],
            ["3", "C - $150 to $199"],
            ["4", "D - $200 to $249"],
            ["5", "E - $250 to $299"],
            ["6", "F - $300 to $349"],
            ["7", "G - $350 to $399"],
            ["8", "H - $400 to $449"],
            ["9", "I - $450 to $499"],
            ["10", "J - $500 to $549"],
            ["11", "K - $550 to $599"],
            ["12", "L - $600 to $649"],
            ["13", "M - $650 to $699"],
            ["14", "N - $700 to $749"],
            ["15", "O - $750 to $799"],
            ["16", "P - $800 to $899"],
            ["17", "Q - $900 to $999"],
            ["18", "R - $1,000 to $1,249"],
            ["19", "S - $1,250 to $1,499"],
            ["20", "T - $1,500 to $1,999"],
            ["21", "U - $2,000 or more"],
            ["22", "Z - Not Elsewhere Classified (nec.)"]
        ],
        columns=[0, "Label"],
    )
    # Get Rent by Race
    # Example at https://data.census.gov/mdat/#/search?ds=ACSPUMS5Y2018&vv=HINCP&cv=HISP_RC1&rv=HINCP_RC1&nv=HISP(02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24)&wt=WGTP&HISP_RC1=%7B%22S%22%3A%22Recoded%20detailed%20Hispanic%20origin%20recode%22%2C%22R%22%3A%22HISP%22%2C%22W%22%3A%22PWGTP%22%2C%22V%22%3A%5B%5B%2202%2C03%2C04%2C05%2C06%2C07%2C08%2C09%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%22%2C%22D%20-%20Hispanic%22%5D%5D%7D&HINCP_RC1=%7B%22S%22%3A%22Household%20income%20%2528past%2012%20months%2C%20use%20ADJINC%20to%20adjust%20HINCP%20to%20constant%20dollars%2529%20recode%22%2C%22R%22%3A%22HINCP%22%2C%22W%22%3A%22WGTP%22%2C%22V%22%3A%5B%5B%22-59998%3A-1%2C1%3A9999%2C-59999%2C0%22%2C%22A%20-%20Less%20than%20%2410%2C000%22%5D%2C%5B%2210000%3A14999%22%2C%22B%20-%20%2410%2C000%20to%20%2414%2C999%22%5D%2C%5B%2215000%3A19999%22%2C%22C%20-%20%2415%2C000%20to%20%2419%2C999%22%5D%2C%5B%2220000%3A24999%22%2C%22D%20-%20%2420%2C000%20to%20%2424%2C999%22%5D%2C%5B%2225000%3A29999%22%2C%22E%20-%20%2425%2C000%20to%20%2429%2C999%22%5D%2C%5B%2230000%3A34999%22%2C%22F%20-%20%2430%2C000%20to%20%2434%2C999%22%5D%2C%5B%2235000%3A39999%22%2C%22G%20-%20%2435%2C000%20to%20%2439%2C999%22%5D%2C%5B%2240000%3A44999%22%2C%22H%20-%20%2440%2C000%20to%20%2444%2C999%22%5D%2C%5B%2245000%3A49999%22%2C%22I%20-%20%2445%2C000%20to%20%2449%2C999%22%5D%2C%5B%2250000%3A59999%22%2C%22J%20-%20%2450%2C000%20to%20%2459%2C999%22%5D%2C%5B%2260000%3A74999%22%2C%22K%20-%20%2460%2C000%20to%20%2474%2C999%22%5D%2C%5B%2275000%3A99999%22%2C%22L%20-%20%2475%2C000%20to%20%2499%2C999%22%5D%2C%5B%22100000%3A124999%22%2C%22M%20-%20%24100%2C000%20to%20%24124%2C999%22%5D%2C%5B%22125000%3A149999%22%2C%22N%20-%20%24125%2C000%20to%20%24149%2C999%22%5D%2C%5B%22150000%3A199999%22%2C%22O%20-%20%24150%2C000%20to%20%24199%2C999%22%5D%2C%5B%22200000%3A99999999%22%2C%22P%20-%20%24200%2C000%20or%20more%22%5D%2C%5B%22-60000%22%2C%22Z%20-%20Not%20Elsewhere%20Classified%20%2528nec.%2529%22%5D%5D%7D
    api_url = (
        "https://api.census.gov/data/"
        + acs_year
        + "/acs/acs5/pums?tabulate=weight(WGTP)&col+RAC1P_RC1&row+GRNTP_RC1"
    )
    if ucgid is not False:
        api_url += "&ucgid=" + ucgid

    api_url += "&RAC1P=1&RAC1P=2&RAC1P=6&TEN=3&TEN=4&recode+RAC1P_RC1=%7B%22b%22:%22RAC1P%22,%22d%22:%5B%5B%221%22%5D,%5B%222%22%5D,%5B%226%22%5D%5D%7D&recode+GRNTP_RC1=%7B%22b%22:%22GRNTP%22,%22d%22:%5B%5B%7B%22mn%22:1,%22mx%22:99%7D%5D,%5B%7B%22mn%22:100,%22mx%22:149%7D%5D,%5B%7B%22mn%22:150,%22mx%22:199%7D%5D,%5B%7B%22mn%22:200,%22mx%22:249%7D%5D,%5B%7B%22mn%22:250,%22mx%22:299%7D%5D,%5B%7B%22mn%22:300,%22mx%22:349%7D%5D,%5B%7B%22mn%22:350,%22mx%22:399%7D%5D,%5B%7B%22mn%22:400,%22mx%22:449%7D%5D,%5B%7B%22mn%22:450,%22mx%22:499%7D%5D,%5B%7B%22mn%22:500,%22mx%22:549%7D%5D,%5B%7B%22mn%22:550,%22mx%22:599%7D%5D,%5B%7B%22mn%22:600,%22mx%22:649%7D%5D,%5B%7B%22mn%22:650,%22mx%22:699%7D%5D,%5B%7B%22mn%22:700,%22mx%22:749%7D%5D,%5B%7B%22mn%22:750,%22mx%22:799%7D%5D,%5B%7B%22mn%22:800,%22mx%22:899%7D%5D,%5B%7B%22mn%22:900,%22mx%22:999%7D%5D,%5B%7B%22mn%22:1000,%22mx%22:1249%7D%5D,%5B%7B%22mn%22:1250,%22mx%22:1499%7D%5D,%5B%7B%22mn%22:1500,%22mx%22:1999%7D%5D,%5B%7B%22mn%22:2000,%22mx%22:99999%7D%5D,%5B%220%22%5D%5D%7D"
    # Request the data
    response = requests.get(api_url)
    # Read the JSON
    j = json.loads(response.content)
    # Remove the header
    j.pop(0)
    # Create a data frame
    race_df = pd.DataFrame(j)
    race_df.columns = ["A - White alone", "B - Black alone", "C - Asian alone", 0]
    race_df = pd.merge(labels, race_df).reset_index(drop=True)
    # Get Rent by Ethnicity
    api_url = (
        "https://api.census.gov/data/"
        + acs_year
        + "/acs/acs5/pums?tabulate=weight(WGTP)&col+HISP_RC1&row+GRNTP_RC1"
    )
    if ucgid is not False:
        api_url += "&ucgid=" + ucgid
    api_url += "&TEN=3&TEN=4&HISP=02&HISP=03&HISP=04&HISP=05&HISP=06&HISP=07&HISP=08&HISP=09&HISP=10&HISP=11&HISP=12&HISP=13&HISP=14&HISP=15&HISP=16&HISP=17&HISP=18&HISP=19&HISP=20&HISP=21&HISP=22&HISP=23&HISP=24&recode+HISP_RC1=%7B%22b%22:%22HISP%22,%22d%22:%5B%5B%2202%22,%2203%22,%2204%22,%2205%22,%2206%22,%2207%22,%2208%22,%2209%22,%2210%22,%2211%22,%2212%22,%2213%22,%2214%22,%2215%22,%2216%22,%2217%22,%2218%22,%2219%22,%2220%22,%2221%22,%2222%22,%2223%22,%2224%22%5D%5D%7D&recode+GRNTP_RC1=%7B%22b%22:%22GRNTP%22,%22d%22:%5B%5B%7B%22mn%22:1,%22mx%22:99%7D%5D,%5B%7B%22mn%22:100,%22mx%22:149%7D%5D,%5B%7B%22mn%22:150,%22mx%22:199%7D%5D,%5B%7B%22mn%22:200,%22mx%22:249%7D%5D,%5B%7B%22mn%22:250,%22mx%22:299%7D%5D,%5B%7B%22mn%22:300,%22mx%22:349%7D%5D,%5B%7B%22mn%22:350,%22mx%22:399%7D%5D,%5B%7B%22mn%22:400,%22mx%22:449%7D%5D,%5B%7B%22mn%22:450,%22mx%22:499%7D%5D,%5B%7B%22mn%22:500,%22mx%22:549%7D%5D,%5B%7B%22mn%22:550,%22mx%22:599%7D%5D,%5B%7B%22mn%22:600,%22mx%22:649%7D%5D,%5B%7B%22mn%22:650,%22mx%22:699%7D%5D,%5B%7B%22mn%22:700,%22mx%22:749%7D%5D,%5B%7B%22mn%22:750,%22mx%22:799%7D%5D,%5B%7B%22mn%22:800,%22mx%22:899%7D%5D,%5B%7B%22mn%22:900,%22mx%22:999%7D%5D,%5B%7B%22mn%22:1000,%22mx%22:1249%7D%5D,%5B%7B%22mn%22:1250,%22mx%22:1499%7D%5D,%5B%7B%22mn%22:1500,%22mx%22:1999%7D%5D,%5B%7B%22mn%22:2000,%22mx%22:99999%7D%5D,%5B%220%22%5D%5D%7D"
    response = requests.get(api_url)
    # Read the JSON
    j = json.loads(response.content)
    # Remove the header
    j.pop(0)
    # Create a data frame
    ethn_df = pd.DataFrame(j)
    ethn_df.columns = ["D - Hispanic", 0]
    ethn_df = pd.merge(labels, ethn_df).reset_index(drop=True)
    # Put them all together
    df = pd.merge(race_df, ethn_df).drop([0], axis=1)
    return df


def get_home_value_by_race_ethnicity(acs_year, ucgid = False):
    # Home Value Labels
    labels = pd.DataFrame(
        [
            ["1", "A - Less than $10,000"],
            ["2", "B - $10,000 to $14,999"],
            ["3", "C - $15,000 to $19,999"],
            ["4", "D - $20,000 to $24,999"],
            ["5", "E - $25,000 to $29,999"],
            ["6", "F - $30,000 to $34,999"],
            ["7", "G - $35,000 to $39,999"],
            ["8", "H - $40,000 to $49,999"],
            ["9", "I - $50,000 to $59,999"],
            ["10", "J - $60,000 to $69,999"],
            ["11", "K - $70,000 to $79,999"],
            ["12", "L - $80,000 to $89,999"],
            ["13", "M - $90,000 to $99,999"],
            ["14", "N - $100,000 to $124,999"],
            ["15", "O - $125,000 to $149,999"],
            ["16", "P - $150,000 to $174,999"],
            ["17", "Q - $175,000 to $199,999"],
            ["18", "R - $200,000 to $249,999"],
            ["19", "S - $250,000 to $299,999"],
            ["20", "T - $300,000 to $399,999"],
            ["21", "U - $400,000 to $499,999"],
            ["22", "V - $500,000 to $749,999"],
            ["23", "W - $750,000 to $999,999"],
            ["24", "X - $1,000,000 or more"],
            ["25", 'Z - N/A (GQ/vacant units, except "for-sale-only" and "sold, not occupied"/not owned or being bought)']
        ],
        columns=[0, "Label"],
    )
    # Get Home Value by Race
    api_url = (
        "https://api.census.gov/data/"
        + acs_year
        + "/acs/acs5/pums?tabulate=weight(WGTP)&col+RAC1P_RC1&row+VALP_RC1"
    )
    if ucgid is not False:
        api_url += "&ucgid=" + ucgid
    api_url += "&RAC1P=1&RAC1P=2&RAC1P=6&recode+RAC1P_RC1=%7B%22b%22:%22RAC1P%22,%22d%22:%5B%5B%221%22%5D,%5B%222%22%5D,%5B%226%22%5D%5D%7D&recode+VALP_RC1=%7B%22b%22:%22VALP%22,%22d%22:%5B%5B%7B%22mn%22:1,%22mx%22:9999%7D%5D,%5B%7B%22mn%22:10000,%22mx%22:14999%7D%5D,%5B%7B%22mn%22:15000,%22mx%22:19999%7D%5D,%5B%7B%22mn%22:20000,%22mx%22:24999%7D%5D,%5B%7B%22mn%22:25000,%22mx%22:29999%7D%5D,%5B%7B%22mn%22:30000,%22mx%22:34999%7D%5D,%5B%7B%22mn%22:35000,%22mx%22:39999%7D%5D,%5B%7B%22mn%22:40000,%22mx%22:49999%7D%5D,%5B%7B%22mn%22:50000,%22mx%22:59999%7D%5D,%5B%7B%22mn%22:60000,%22mx%22:69999%7D%5D,%5B%7B%22mn%22:70000,%22mx%22:79999%7D%5D,%5B%7B%22mn%22:80000,%22mx%22:89999%7D%5D,%5B%7B%22mn%22:90000,%22mx%22:99999%7D%5D,%5B%7B%22mn%22:100000,%22mx%22:124999%7D%5D,%5B%7B%22mn%22:125000,%22mx%22:149999%7D%5D,%5B%7B%22mn%22:150000,%22mx%22:174999%7D%5D,%5B%7B%22mn%22:175000,%22mx%22:199999%7D%5D,%5B%7B%22mn%22:200000,%22mx%22:249999%7D%5D,%5B%7B%22mn%22:250000,%22mx%22:299999%7D%5D,%5B%7B%22mn%22:300000,%22mx%22:399999%7D%5D,%5B%7B%22mn%22:400000,%22mx%22:499999%7D%5D,%5B%7B%22mn%22:500000,%22mx%22:749999%7D%5D,%5B%7B%22mn%22:750000,%22mx%22:999999%7D%5D,%5B%7B%22mn%22:1000000,%22mx%22:9999999%7D%5D,%5B%22-1%22%5D%5D%7D"
    # Request the data
    response = requests.get(api_url)
    # Read the JSON
    j = json.loads(response.content)
    # Remove the header
    j.pop(0)
    # Create a data frame
    race_df = pd.DataFrame(j)
    race_df.columns = ["A - White alone", "B - Black alone", "C - Asian alone", 0]
    race_df = pd.merge(labels, race_df).reset_index(drop=True)
    # Get Home Valuue by Ethnicity
    api_url = (
        "https://api.census.gov/data/"
        + acs_year
        + "/acs/acs5/pums?tabulate=weight(WGTP)&col+HISP_RC1&row+VALP_RC1"
    )
    if ucgid is not False:
        api_url += "&ucgid=" + ucgid
    api_url += "&HISP=02&HISP=03&HISP=04&HISP=05&HISP=06&HISP=07&HISP=08&HISP=09&HISP=10&HISP=11&HISP=12&HISP=13&HISP=14&HISP=15&HISP=16&HISP=17&HISP=18&HISP=19&HISP=20&HISP=21&HISP=22&HISP=23&HISP=24&recode+HISP_RC1=%7B%22b%22:%22HISP%22,%22d%22:%5B%5B%2202%22,%2203%22,%2204%22,%2205%22,%2206%22,%2207%22,%2208%22,%2209%22,%2210%22,%2211%22,%2212%22,%2213%22,%2214%22,%2215%22,%2216%22,%2217%22,%2218%22,%2219%22,%2220%22,%2221%22,%2222%22,%2223%22,%2224%22%5D%5D%7D&recode+VALP_RC1=%7B%22b%22:%22VALP%22,%22d%22:%5B%5B%7B%22mn%22:1,%22mx%22:9999%7D%5D,%5B%7B%22mn%22:10000,%22mx%22:14999%7D%5D,%5B%7B%22mn%22:15000,%22mx%22:19999%7D%5D,%5B%7B%22mn%22:20000,%22mx%22:24999%7D%5D,%5B%7B%22mn%22:25000,%22mx%22:29999%7D%5D,%5B%7B%22mn%22:30000,%22mx%22:34999%7D%5D,%5B%7B%22mn%22:35000,%22mx%22:39999%7D%5D,%5B%7B%22mn%22:40000,%22mx%22:49999%7D%5D,%5B%7B%22mn%22:50000,%22mx%22:59999%7D%5D,%5B%7B%22mn%22:60000,%22mx%22:69999%7D%5D,%5B%7B%22mn%22:70000,%22mx%22:79999%7D%5D,%5B%7B%22mn%22:80000,%22mx%22:89999%7D%5D,%5B%7B%22mn%22:90000,%22mx%22:99999%7D%5D,%5B%7B%22mn%22:100000,%22mx%22:124999%7D%5D,%5B%7B%22mn%22:125000,%22mx%22:149999%7D%5D,%5B%7B%22mn%22:150000,%22mx%22:174999%7D%5D,%5B%7B%22mn%22:175000,%22mx%22:199999%7D%5D,%5B%7B%22mn%22:200000,%22mx%22:249999%7D%5D,%5B%7B%22mn%22:250000,%22mx%22:299999%7D%5D,%5B%7B%22mn%22:300000,%22mx%22:399999%7D%5D,%5B%7B%22mn%22:400000,%22mx%22:499999%7D%5D,%5B%7B%22mn%22:500000,%22mx%22:749999%7D%5D,%5B%7B%22mn%22:750000,%22mx%22:999999%7D%5D,%5B%7B%22mn%22:1000000,%22mx%22:9999999%7D%5D,%5B%22-1%22%5D%5D%7D"
    response = requests.get(api_url)
    # Read the JSON
    j = json.loads(response.content)
    # Remove the header
    j.pop(0)
    # Create a data frame
    ethn_df = pd.DataFrame(j)
    ethn_df.columns = ["D - Hispanic", 0]
    ethn_df = pd.merge(labels, ethn_df).reset_index(drop=True)
    # Put them all together
    df = pd.merge(race_df, ethn_df).drop([0], axis=1)
    return df


# This is where the magic happens
writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

for geo,ucgid in geos.items():
    print("Getting " + geo + " Data...")
    # Get Cost of Rent Data
    rent_by_race_ethnicity = get_rent_by_race_ethnicity(acs_year, ucgid)
    renter_income_by_race_ethnicity = get_income_by_race_ethnicity(acs_year, ucgid, True)
    # Append an empty row
    rent_by_race_ethnicity = rent_by_race_ethnicity.append(pd.Series(), ignore_index=True)
    # Combine
    cost_of_rent = rent_by_race_ethnicity.append(renter_income_by_race_ethnicity, ignore_index = True)
    # Save
    cost_of_rent.to_excel(writer, sheet_name = geo + " rent", index = False)
    # Get Cost of Home Ownership Data
    home_value_by_race_ethnicity = get_home_value_by_race_ethnicity(acs_year, ucgid)
    income_by_race_ethnicity = get_income_by_race_ethnicity(acs_year, ucgid)
    # Append an empty row
    home_value_by_race_ethnicity = home_value_by_race_ethnicity.append(pd.Series(), ignore_index=True)
    # Combine
    cost_of_home_ownership = home_value_by_race_ethnicity.append(income_by_race_ethnicity, ignore_index = True)
    # Save
    cost_of_home_ownership.to_excel(writer, sheet_name = geo + " ho", index = False)
    
writer.save()
    