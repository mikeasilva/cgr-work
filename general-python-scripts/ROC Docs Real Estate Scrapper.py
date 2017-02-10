# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 12:58:57 2016

@author: Michael Silva
"""

import requests
import sqlite3 as db

create_fresh_db = False
scrape_for_data = True

max_year = 2016
min_year = 1993

con = db.connect("ROC Docs Real Estate.sqlite")
con.row_factory = lambda cursor, row: row[0]
c = con.cursor()
if create_fresh_db:
    c.execute('DROP TABLE IF EXISTS `scrapped_data`')
    c.execute('DROP TABLE IF EXISTS `try_again`')
    c.execute('DROP TABLE IF EXISTS `scrapped_index`')
    # Create tables
    c.execute('''CREATE TABLE `scrapped_data`
             (`id`, `Town`, `Address`, `Zip Code`, `Sale Price`, `Sale Date`, `Seller(s) Name`, `Buyer(s) Name`,`County`)''')
    c.execute('''CREATE TABLE `try_again` 
             (`id`, `url`)''')
    c.execute('''CREATE TABLE `scrapped_index` 
             (`id`, `url`)''')
    con.commit()
    i=0
    error_i = 0
    scrapped_i = 0
    scrapped_list = list()
else:
    print('Restarting data scrapping...')
    ids = c.execute('SELECT MAX(id) AS id FROM scrapped_data').fetchall()
    i = ids[0]
    ids = c.execute('SELECT MAX(id) AS id FROM try_again').fetchall()
    if not ids[0]:
        error_i = 0
    else:
        error_i = ids[0]
    ids = c.execute('SELECT MAX(id) AS id FROM scrapped_index').fetchall()
    scrapped_i = ids[0]
    scrapped_list = c.execute('SELECT url FROM scrapped_index').fetchall()

if scrape_for_data:
    for year in range(min_year, max_year+1, 1):
        for c1 in range(1, 58, 1):
            scrape_data = True
            
            base_url = 'http://rochester.nydatabases.com/ajax/43?textsearch_2=&c1%5B%5D='+str(c1)+'&c2%5B%5D=&c6%5B%5D='+str(year)+'&c5%5B%5D=&c5%5B%5D=&textsearch=&sort=5&sort_dir=asc&_=1477938267366&start='
            start = 0
            
            while scrape_data:
                url = base_url+str(start)
                if url not in scrapped_list:
                    r = requests.get(url)
                    if r.status_code == 200:
                        try:
                            j = r.json()
                            try:
                                for result in j['result']:
                                    if url not in scrapped_list:
                                        scrapped_i += 1
                                        scrapped_list.append(url)
                                        row = [(scrapped_i, url)]
                                        c.executemany('INSERT INTO scrapped_index VALUES (?, ?)', row)
                                        con.commit()
                                        
                                    i += 1
                                    print(str(i)+': '+result[4]+' (County: '+str(c1)+')')
                                    row = [(i, result[0], result[1], result[2], result[3], result[4], result[5], result[6], c1)]
                                    c.executemany('INSERT INTO scrapped_data VALUES (?,?,?,?,?,?,?,?,?)', row)
                                con.commit()
                                
                                # Check to see if we need to keep going.  This will work until we get an IndexError
                                try:
                                    # Let's identify what the start should be for the next round.
                                    starts = j['pages'].split('selected_page')
                                    starts = starts[1].split('start="')
                                    starts = starts[1].split('"')
                                    start = int(starts[0])
                                except:
                                    # There was and IndexError so we don't need to scrape data any more
                                    scrape_data = False 
                            except:
                                print('Something bad happend with '+url)
                                error_i += 1
                                row = [(error_i, url)]
                                c.executemany('INSERT INTO try_again VALUES (?, ?)', row)
                                con.commit()
                                scrape_data = False 
                                continue
                        except:
                            print('No Results found')
                            scrape_data = False
                            continue
                else:
                    print('Already scrapped: '+url)
                    scrape_data = False 
                    continue
    con.commit()
    con.close()
