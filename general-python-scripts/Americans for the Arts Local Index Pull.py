#-------------------------------------------------------------------------------
# Name:        Americans for the Arts Local Index Extractor
# Purpose:     This pulls the data from the AftA Local Index into a csv file
#
# Author:      Michael Silva
#
# Created:     20/11/2014
#-------------------------------------------------------------------------------

import requests
import pandas
import os

# This function creates a text progress bar
def progressBar(i, j, size_of_pb = 40):
    percent_done = i / j
    pb_done = round(size_of_pb * percent_done, 0)
    pb_left = size_of_pb - pb_done
    percent_done = round(percent_done*100)
    return('|' + '='*int(pb_done) + '>' + ' '*int(pb_left) + '| ' +str(percent_done)+'%')

# Initialize Progress Bar
pb_i=0
print(progressBar(pb_i, len(states)))

states = ['AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']

# Step through the states
for st in states:
    print('Starting '+st)
    # Get the counties in the state
    url1 = 'http://www.artsindexusa.org/fetchCounties.php?state='+st
    r1 = requests.get(url1)
    json1 = r1.json()
    # Step through the counties
    for fips in json1:
        s = fips.split(':')
        county_fips = s[0]
        county_name = s[1]
        #print(county_name,st) # Useful for debugging
        url2 = 'http://www.artsindexusa.org/fetchCounty.php?selectedCounty='+county_fips
        df = pandas.io.json.read_json(url2)
        df['row'] = df.index.values
        df['fips'] = county_fips
        df['county name'] = county_name
        df['state'] = st

        # Store the data in a data frame
        try:
            arts_data
        except NameError:
            # The data frame does not exist so let's create it
            arts_data = df
        else:
            # Append the rows to the data frame
            arts_data = arts_data.append(df)

    # Update progress bar
    pb_i = pb_i + 1
    print(progressBar(pb_i, len(states)))

# Save the Files to the Desktop
userhome = os.path.expanduser('~')
desktop = userhome + '/Desktop/'
file_path = desktop + 'Local Arts Index.csv'
arts_data.to_csv(file_path, sep=',', encoding='utf-8')



