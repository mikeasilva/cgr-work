# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 11:49:27 2018

@author: Michael

You must install the chrome driver for this script.  You can find it at:
https://sites.google.com/a/chromium.org/chromedriver/home

Move the file into C:\Windows\System32 to "install" it
"""
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy import create_engine
import pandas as pd

start_year = 2002
end_year = 2015
years = range(start_year, end_year+1)


def parse_lehd_html(html, search_text):
    """Scrapes HTML for search text and returns a dictionary"""
    data = dict()
    soup = BeautifulSoup(html, 'html5lib')
    for i in soup.find_all('tr'):
        for find_me in search_text:
            if find_me in i.contents[0]:
                tds = i.find_all('td')
                key = tds[0].string
                value = str(tds[1].string).replace(',', '')
                data[key] = int(value)
    return(data)

# This is the text we will be searching for
search_text = ('Employed in the Selection Area but Living Outside', 
               'Employed and Living in the Selection Area',
               'Living in the Selection Area but Employed Outside')

engine = create_engine('mysql+pymysql://user:password@server/db')
conn = engine.connect()
    
sql = 'SELECT CGR_GEO_ID, NAME, LEHD_URL FROM CGR_GeographyIndex WHERE CI_GEO=1 AND LEHD_URL IS NOT NULL'

query = conn.execute(sql)
browser = webdriver.Chrome()

data = list()

for row in query:
    print('Getting data for '+row[1])
    for year in years:
        browser.get(row[2])
        browser.find_element_by_id('analysis_type4').click()
        # Select the year
        browser.find_element_by_xpath('.//*[@type="checkbox"]').click()
        for el in browser.find_elements_by_name('year'):
            if int(el.get_attribute('value')) == year:
                el.click()
        # Submit the form
        browser.find_element_by_id('run_btn').click()
        # Scrape the webpage
        temp = parse_lehd_html(browser.page_source, search_text)
        # Add in additional info
        temp['year'] = year
        temp['CGR_GEO_ID'] = row[0]
        data.append(temp)
        
browser.quit()

df = pd.DataFrame(data)
df.dropna(inplace=True)

writer = pd.ExcelWriter('Scrapped LEHD Data.xlsx', engine='xlsxwriter')
df.to_excel(writer,'data', index=False)
writer.save()