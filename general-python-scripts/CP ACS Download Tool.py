# -*- coding: utf-8 -*-
"""
Community Profile ACS Download Tool 

Started on Tue Apr 21 15:54:31 2015

@author: Michael Silva

@description: This script downloads ACS data for CGR community profiles using 
the API and saves them as csv files.  It begins by prompting the user for which
data set they want to get.  Next it creating the directory structure on the 
network drive to hold the csv files.  Then it downloads the list of variables 
available via the API and builds a table list & the table/variable dictionary.
With all these things in place it moves on to the data download and processing
phase.  It checks the desired table against the table list.  If it is present,
it will download all variables in the table for the state, and all counties, 
places  and county subdivisions in a state.  It will process the data and save
it to the network drive.  If the table is not in the table list it gets added
to the list of tables not available via the API. At the end of the processing
the script will output this list so the user knows they will have to get the 
data by some other means.
"""
import requests, pandas, os

api_key = 'REMOVED' # CGR's API key

state_fips = dict()
state_fips['NY']='36'
state_fips['FL']='12'
state_fips['TN']='47'

api_pull = dict() # This will hold all the tables needed per state
api_pull['NY'] = ['B08013', 'B08105A', 'B08105B', 'B08105D', 'B08105I', 'B08134', 'B11001', 'B11005', 'B15002', 'B17001', 'B17001A' ,'B17001B', 'B17001D', 'B17001I', 'B17010', 'B17010A', 'B17010B', 'B17010D', 'B17010I', 'B17020A', 'B17020B', 'B17020D', 'B17020I', 'B19013', 'B19013A', 'B19013B', 'B19013D', 'B19013I', 'B19001', 'B19001A', 'B19001B', 'B19001D', 'B19001I', 'B23008', 'B25002', 'B25003', 'B25003A', 'B25003B', 'B25003D', 'B25003I', 'B25044', 'B25064', 'B25064', 'B25077', 'B25075', 'B25119', 'B08301', 'C15002A', 'C15002B', 'C15002D', 'C15002I', 'S2301']
api_pull['FL'] = ['B08013', 'B08134', 'B15002', 'B17001', 'B17010', 'B19013', 'B25064', 'B25077', 'B25119', 'B15010', 'B17005']
api_pull['TN'] = ['B08013', 'B08134', 'B15002', 'B17010', 'B17010A', 'B17010B', 'B17010D', 'B17010I', 'B19001', 'B19001A', 'B19001B', 'B19001D', 'B19001I', 'B25064', 'B25075', 'B08301', 'B09001', 'B10002', 'S2701']


# You should not need to edit below this line
# =============================================================================

##
# GET THE USER'S INPUT ON WHAT DATA TO PULL
##

year = input('What ACS 5 year data set (enter 2013 for 2009-13)? ')

##
# BUILD DIRECTORIES ON H TO HOLD CSV FILES
##
print '  Building directory structure on H:\...',
acs_year = str(year-4) + '-' + str(year)[-2:]
base_dir = "H:\Data Warehouse\Census Bureau\American Community Survey\\" + acs_year
# Create base directory if it doesn't exist
if not os.path.exists(base_dir):
    os.makedirs(base_dir)
# Create subdirectories if they don't exist
for geo in api_pull:
    directory = base_dir + '\\' + geo
    if not os.path.exists(directory):
        os.makedirs(directory)
print('\bDone')

## 
# PULLING THE VARIABLE LIST FROM API
##

# Now that we know what year of data the user wants we need to pull the 
# variable list.

print '  Pulling JSON variable list...',
# Build the API URL
variables_url = 'http://api.census.gov/data/'+str(year)+'/acs5/variables.json'
# Read in the data
data = requests.get(url=variables_url)
# Check to make sure we could pull variables
if data.status_code == 404:
    print('\bFailed')
    import sys
    sys.exit('You entered an invalid ACS year.  Please try again.')
else:
    data = data.json()
    print('\bDone')

## 
# BUILDING ACS TABLE VARIABLE LIST DICTIONARY
##

# We now will iterate through the data and build a dictionary that has all
# the variables associated with the table.

print '  Building table list...',
table_list = list() # This will hold all the tables.
acs_dict = dict() # This will hold the variables by table.
# Iterate through the variables
for variable in data['variables']:
    s = variable.split('_') # Break the string apart by the underscore.
    table = s[0] # This is the table name.
    
    if not table in table_list:
        table_list.append(table) # Add it to the table list
        var_list = list() # Create an empty list for the acs_dict
        var_list.append(variable) # Put the variable name in the list
        acs_dict[table] = var_list # Add the variable list to the dictionary
    else:
        var_list = acs_dict[table] # Pull the existing variable list
        var_list.append(variable) # Add in the new variable
        var_list.sort() # Sort it (so the estimates are followed by the MOE)
        acs_dict[table] = var_list # Replace the list with the updated one
print('\bDone')

# Now that this has been complete we can call acs_dict['B10001'] to get all
# the variables in the table

##
# DOWNLOAD ACS DATA
##

def download_and_save_data(acs_dict, state_fips, location, api_key, api_url_base, base_dir, table):
    # Since there is a 50 variable maximum we need to see how many calls
    # to the API we need to make to get all the variables.
    api_calls_needed = (len(acs_dict[table])/49)+1
    api_calls_done = 0
    variable_range = 49
    while api_calls_done < api_calls_needed:
        get_string = ''
        print('        API Call Set '+str(api_calls_done+1)+' of '+str(api_calls_needed))
        variable_range_start = variable_range * api_calls_done
        variable_range_end = variable_range_start + variable_range
        for variable in acs_dict[table][variable_range_start:variable_range_end]:
            get_string = get_string + ','+variable
        # Get the state level data
        api_url = api_url_base + get_string + '&for=state:' + state_fips[location] + '&key=' + api_key
        state_data = pandas.io.json.read_json(api_url)
        state_data.columns = state_data[:1].values.tolist() # Rename columns based on first row
        state_data['Geocode'] = state_data['state']
        state_data = state_data[1:] # Drop first row
        # Pull all of the counties in the state
        api_url = api_url_base + get_string + '&for=county:*&in=state:' + state_fips[location] + '&key=' + api_key
        county_data = pandas.io.json.read_json(api_url)
        county_data.columns = county_data[:1].values.tolist() # Rename columns based on first row
        county_data['Geocode'] = county_data['state'] + county_data['county']
        county_data = county_data[1:] # Drop first row
        # Pull all places in the state
        api_url = api_url_base + get_string + '&for=place:*&in=state:' + state_fips[location] + '&key=' + api_key
        place_data = pandas.io.json.read_json(api_url)
        place_data.columns = place_data[:1].values.tolist() # Rename columns based on first row
        place_data['Geocode'] = place_data['state'] + place_data['place']
        place_data = place_data[1:] # Drop first row
        # Pull all county subdivisions in the state
        api_url = api_url_base + get_string + '&for=county+subdivision:*&in=state:' + state_fips[location] + '&key=' + api_key
        county_subdivision_data = pandas.io.json.read_json(api_url)
        county_subdivision_data.columns = county_subdivision_data[:1].values.tolist() # Rename columns based on first row
        county_subdivision_data['Geocode'] = county_subdivision_data['state'] + county_subdivision_data['county'] + county_subdivision_data['county subdivision']
        county_subdivision_data = county_subdivision_data[1:] # Drop first row
        # Build long table by append rows
        temp = state_data.append(county_data)
        temp = temp.append(place_data)
        temp = temp.append(county_subdivision_data)
        # Add columns if the final data frame is created
        if api_calls_done == 0:
            data = temp
        else:
            data = pandas.concat([data, temp], axis=1)
        api_calls_done = api_calls_done + 1
        
    csv_path = base_dir + '\\' + location + '\\' + table + '.csv'
    # Pull out the Geocode and Name        
    geocode = data['Geocode']
    series = type(pandas.Series())
    #if type(geocode) == 'pandas.core.series.Series':
    if isinstance(geocode, series):
        geocode = pandas.DataFrame(geocode, columns=['Geocode'])
    else:
        geocode = geocode[[1]]
    name = data['NAME']
    if isinstance(name, series):
        name = pandas.DataFrame(name, columns=['NAME'])
    else:
        name = name[[1]]
    # Drop unneeded columns in they exist
    data = data.drop(['state'], axis=1) # Drop the state column
    data = data.drop(['county'], axis=1) # Drop the county column
    data = data.drop(['place'], axis=1) # Drop the place column
    data = data.drop(['county subdivision'], axis=1) # Drop the county subdivision column
    # Drop the location information
    data = data.drop(['Geocode'], axis=1)
    data = data.drop(['NAME'], axis=1)
    # Build data frame with columns in the desired order
    data = pandas.concat([geocode, name, data], axis=1)
    data.to_csv(csv_path, index=False)
    print('      Table '+table+' Downloaded and Saved')


print('  Downloading tables for')
not_available_via_api = list() # This will hold the tables we can't get via the API
i=0
for location in api_pull:
    i=i+1
    print('    '+location+' (Location '+str(i)+' of '+str(len(api_pull))+')')
    j=0
    for table in api_pull[location]:
        j=j+1
        print('      Table '+table+' ('+str(j)+' of '+str(len(api_pull[location]))+')')
        api_url_base = 'http://api.census.gov/data/'+str(year)+'/acs5?get=NAME'
        if table in table_list:
            download_and_save_data(acs_dict, state_fips, location, api_key, api_url_base, base_dir, table)
        else:
            if table not in not_available_via_api:
                not_available_via_api.append(table)
            print('      WARNING: Table '+table+' is not available via the API!')

print ('All data is now stored on the H drive!')
print ('\rThe following tables were not downloaded:')
for table in not_available_via_api:
    print('  '+table)