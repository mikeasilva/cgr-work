#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 1 08:15:50 2017

@author: Michael Silva
"""
from selenium import webdriver
import sqlite3
import requests
from bs4 import BeautifulSoup

base_url = 'https://onthemap.ces.census.gov/'

start_year = 2002
end_year = 2014

years = range(start_year, end_year+1)

con = sqlite3.connect('County LEHD Data.db3')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS `data`
                (`url` TEXT, `html` TEXT, `location` TEXT, `year` INTEGER);''')

# Set up selenium with the chromium chrome driver
chromedriver_path = '/usr/lib/chromium-browser/chromedriver'
b = webdriver.Chrome(chromedriver_path)

states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA',
          'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA',
          'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY',
          'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
          'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

for st in states:
    print('Getting '+st+' data')
    start_url = base_url+'tot/?q='+st+'&ds=us_cty'
    response = requests.get(start_url)
    soup = BeautifulSoup(response.content, 'lxml')
    uls = soup.find_all('ul', 'otm_m_search_item')
    for ul in uls:
        links = ul.find_all('a')
        for a in links:
            url = a.attrs['href'].replace('../', base_url)
            location = a.string.strip()
            for year in years:
                cur.execute('SELECT * FROM data WHERE location=? AND year=?',
                            (location, year))
                try:
                    db_data = cur.fetchone()[0]
                    print('  '+location+' '+str(year)+' data in db')
                except:
                    print('  Scrapping '+location+' '+str(year)+' data')
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
                        data = (url, b.page_source, location, year)
                        cur.execute('''INSERT INTO data
                                    (url, html, location, year)
                                    VALUES (?, ?, ?, ?);''', data)
                        con.commit()

b.quit()
con.close()
