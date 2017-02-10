# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 08:55:52 2016

@author: Michael Silva
"""
# Get the libraries that I will use
import requests # Handles requesting data from web
import sqlite3 as db # Handles sqlite database

# This is the year of the data we want to pull
year = 2015
# This is the base URL which limits the data to Niagara Falls
base_url = 'http://rochester.nydatabases.com/ajax/43?textsearch_2=&c1%5B%5D=29&c2%5B%5D=Niagara+Falls&c6%5B%5D='+str(year)+'&c5%5B%5D=&c5%5B%5D=&textsearch=&_=1480946474582&start='


# Connect to an sqlite database (or create it if it doesn't exist)
con = db.connect("Niagara Falls Sales Price Data.sqlite")
# Create the cursor to run SQL queries
c = con.cursor()
# Delete the scrapped_data table if it exists (helpful if you need to rerun the script)
c.execute('DROP TABLE IF EXISTS `scrapped_data`')
# Create table
c.execute('''CREATE TABLE `scrapped_data`
             (`id`, `Town`, `Address`, `Zip Code`, `Sale Price`, `Sale Date`, `Seller(s) Name`, `Buyer(s) Name`)''')

# To move through the pages you need to use this start parameter
start = 0
# This will be the unique id column in our database
i=0
# We want to scrape data until there is no more data available.  This helps with that process.
scrape_data = True

while scrape_data:
    # Add on the start to the url
    url = base_url+str(start)
    # Request the data from the web
    r = requests.get(url)
    # Check to see if we have secussfully completed the request (there's data)
    if r.status_code == 200:
        # Read in the JSON data
        j = r.json()   
        # Step through each result (or row)
        for result in j['result']:
            # Add one to the id
            i += 1
            # Print the id and the date so the user has some feedback on what the script is doing
            print(str(i)+': '+result[4])
            # Pull out the data from the result that we want
            row = [(i, result[0], result[1], result[2], result[3], result[4], result[5], result[6])]
            # Insert the data into the database
            c.executemany('INSERT INTO scrapped_data VALUES (?,?,?,?,?,?,?,?)', row)
        # Save all the inserted data
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

# Save again just to be safe
con.commit()
# Close the database connection
con.close()