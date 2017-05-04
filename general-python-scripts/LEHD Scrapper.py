#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  3 15:57:06 2017

@author: Michael Silva
"""

import sqlite3
import csv
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from os import remove

base_url = 'https://onthemap.ces.census.gov/'

start_year = 2002
end_year = 2014

start_from_scratch = False
failed_url_filename = 'failed urls.csv'

years = range(start_year, end_year+1)

con = sqlite3.connect('Scrapped LEHD Data.db3')
cur = con.cursor()

failed_count = 0

if start_from_scratch:
    try:
        remove(failed_url_filename)
    except:
        pass
    with open(failed_url_filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Location', 'Year'])
    f.close()
    cur.execute('DROP TABLE IF EXISTS `location`')
    cur.execute('DROP TABLE IF EXISTS `data`')

# The following is a dictionary of db fields to their LEHD HTML content
search_dict = {'enter': 'Employed in the Selection Area but Living Outside',
               'stay': 'Employed and Living in the Selection Area',
               'leave': 'Living in the Selection Area but Employed Outside'}
search_text = list(search_dict.values())

cur.execute('''CREATE TABLE IF NOT EXISTS `location`
                (`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
                `name`	TEXT UNIQUE);''')

cur.execute('''CREATE TABLE IF NOT EXISTS `data`
                (`location_id`	INTEGER,
                `year`	INTEGER,
                `enter`	NUMERIC,
                `stay`	NUMERIC,
                `leave`	NUMERIC,
                UNIQUE(`location_id`, `year`));''')

# Set up selenium with the chromium chrome driver
chromedriver_path = '/usr/lib/chromium-browser/chromedriver'
b = webdriver.Chrome(chromedriver_path)

# Here's the list of states we are going to scrape
states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA',
          'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA',
          'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY',
          'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
          'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
# Test case
# states = ['DC']


def parse_lehd_html(html, search_text):
    """Search the html for the search text terms and pull out the data."""
    data = dict()
    soup = BeautifulSoup(html, 'lxml')
    for i in soup.find_all('tr'):
        for find_me in search_text:
            if find_me in i.contents[0]:
                tds = i.find_all('td')
                key = tds[0].string
                value = str(tds[1].string).replace(',', '')
                data[key] = value
    return(data)


for st in states:
    print('Getting '+st+' data')
    # County level data
    # start_url = base_url+'tot/?q='+st+'&ds=us_cty'
    # County subdivisions
    start_url = base_url+'tot/?q='+st+'&ds=us_csub'
    # Places
    # start_url = base_url+'tot/?q='+st+'&ds=us_plc'
    response = requests.get(start_url)
    soup = BeautifulSoup(response.content, 'lxml')
    uls = soup.find_all('ul', 'otm_m_search_item')
    for ul in uls:
        links = ul.find_all('a')
        for a in links:
            url = a.attrs['href'].replace('../', base_url)
            location = a.string.strip()
            for year in years:
                cur.execute('SELECT `id` FROM `location` WHERE `name` = ?',
                            (location,))
                try:
                    location_id = cur.fetchone()[0]
                    cur.execute('''SELECT * FROM data
                                WHERE location_id=? AND year=?''',
                                (location_id, year))
                    db_data = cur.fetchone()[0]
                    print('We have '+str(year)+' data for '+location+' in db')
                except:
                    cur.execute('SELECT `id` FROM `location` WHERE `name` = ?',
                                (location,))
                    try:
                        location_id = cur.fetchone()[0]
                    except:
                        print('Adding '+location+' to location table')
                        cur.execute('INSERT INTO location (`name`) VALUES (?)',
                                    (location,))
                        location_id = cur.lastrowid
                        con.commit()
                    print('Scrapping '+str(year)+' data for '+location)
                    b.get(url)
                    # Select Inflow/Outflow
                    b.find_element_by_id('analysis_type4').click()

                    # Select the year
                    b.find_element_by_xpath('.//*[@type="checkbox"]').click()
                    for el in b.find_elements_by_name('year'):
                        if int(el.get_attribute('value')) == year:
                            el.click()

                    # Submit the form
                    b.find_element_by_id('run_btn').click()

                    if b.current_url != url:
                        data = parse_lehd_html(b.page_source, search_text)
                        try:
                            enter = int(data[search_dict['enter']])
                            stay = int(data[search_dict['stay']])
                            leave = int(data[search_dict['leave']])
                            for_db = (location_id, year, enter, stay, leave)
                            cur.execute('''INSERT INTO data
                                        (location_id, year, enter, stay, leave)
                                        VALUES (?, ?, ?, ?, ?);''', for_db)
                        except:
                            # Record the failure
                            with open(failed_url_filename, 'a') as f:
                                writer = csv.writer(f)
                                writer.writerow([url, location, year])
                            f.close()
                            failed_count += 1

            con.commit()

# Report back on failures
print('Done!  There were '+str(failed_count)+' failed attemps')
if failed_count == 0:
    remove(failed_url_filename)
else:
    print('Check '+failed_url_filename+' for what failed')

# Shut it all down
b.quit()
con.commit()
con.close()
