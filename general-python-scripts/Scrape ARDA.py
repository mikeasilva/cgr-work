# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 15:49:33 2020

@author: Michael Silva
"""

from sqlalchemy import create_engine
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

build_from_scratch = False


def scrape_arda(county_fips, year):
    url = (
        "http://www.thearda.com/rcms2010/rcms2010a.asp?U="
        + county_fips
        + "&T=county&Y="
        + str(year)
        + "&S=Name"
    )
    response = requests.get(url)
    return response.text


def process_arda_data(data):
    soup = BeautifulSoup(data[2], features="lxml")
    content = soup.find("div", {"id": "content"})
    table = content.find("table", {"class": "data"})
    df = pd.read_html(str(table))[0]
    df["geography_id"] = data[0]
    df["year"] = data[1]
    return df


def scrape_arda2(county_fips, year):
    url = (
        "http://www.thearda.com/rcms2010/rcms2010a.asp?U="
        + county_fips
        + "&T=county&Y="
        + str(year)
        + "&S=Name"
    )
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="lxml")
    content = soup.find("div", {"id": "content"})
    table = content.find("table", {"class": "data"})
    df = pd.read_html(str(table))[0]
    df["geography_id"] = county_fips
    df["year"] = year
    return df


years = [1980, 1990, 2000, 2010]

engine = create_engine("mysql+pymysql://dba:cgr1915@data.cgr.org/hub")
conn = engine.connect()

con = sqlite3.connect("ARDA.db")
cur = con.cursor()
if build_from_scratch:
    cur.execute("DROP TABLE IF EXISTS data")
    cur.execute(
        """CREATE TABLE "data" (
        "geography_id" TEXT,
        "year" INT,
        "data" TEXT
    );"""
    )
    cur.execute('CREATE INDEX "ix_data" ON "data" ("geography_id", "date");')
    con.commit()

# Scrape data and save it to sqlite database
i = 0
for row in conn.execute(
    'SELECT CGR_GeographyIndex.CGR_GEO_ID, CGR_GeographyIndex.NAME FROM CGR_GeographyIndex WHERE CGR_GeographyIndex.TYPE="County";'
):
    print("Pulling data for " + row[1])
    geography_id = row[0]
    for year in years:
        cur.execute(
            "SELECT * FROM data WHERE `geography_id` LIKE ? AND `year` = ?",
            (geography_id, year),
        )
        if len(cur.fetchall()) != 1:
            temp = scrape_arda(geography_id, year)
            cur.execute(
                "INSERT INTO data (`geography_id`, `year`, `data`) VALUES (?, ?, ?);",
                (geography_id, year, temp),
            )
            i += 1
            if i == 10 * len(years):
                con.commit()
                i = 0
con.commit()

for row in cur.execute("SELECT * FROM data"):
    temp = process_arda_data(row)
    if "arda_df" in locals():
        arda_df = pd.concat([arda_df, temp.copy()])
    else:
        arda_df = temp.copy()

arda_df.to_excel(
    "ARDA Data.xlsx", index=False,
)


con.close()
