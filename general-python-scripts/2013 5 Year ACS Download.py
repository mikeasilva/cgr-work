# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 10:17:27 2015

@author: Michael Silva
"""

referenceYear = 2013
periodCovered = 5 #year(s)
# This dictionary has the state's abreviation followed by the name as found in the download URL from the line above
stateDict = {'NY':'NewYork', 'FL':'Florida'}

# This is which tables we want to download
acsTables = {'B08013', 'B08105A', 'B08105B', 'B08105D', 'B08105I', 'B08134', 'B08301', 'B09001', 'B10002', 'B11001', 'B11005', 'B15002', 'B15010', 'B17001', 'B17001A', 'B17001B', 'B17001D', 'B17001I', 'B17005', 'B17010', 'B17010A', 'B17010B', 'B17010D', 'B17010I', 'B17020A', 'B17020B', 'B17020D', 'B17020I', 'B19001', 'B19001A', 'B19001B', 'B19001D', 'B19001I', 'B19013', 'B19013A', 'B19013B', 'B19013D', 'B19013I', 'B23008', 'B25002', 'B25003', 'B25003A', 'B25003B', 'B25003D', 'B25003I', 'B25044', 'B25063', 'B25064', 'B25075', 'B25077', 'B25119', 'C15002A', 'C15002B', 'C15002D', 'C15002I', 'C21007'}#, 'S2301', 'S2701'}
# For debugging/testing
acsTables = {'B08105A'}

baseURL = 'http://www2.census.gov/acs' + str(referenceYear) + '_' + str(periodCovered) + 'yr/summaryfile/'
downloadURL = baseURL + '2009-2013_ACSSF_By_State_By_Sequence_Table_Subset/'

#==============================================================================
#================  You shouldn't have to edit below this line  ================
#==============================================================================

# Load the libraries we need
import pandas as pd
import numpy as np
import requests, zipfile, StringIO, os

# This will be used later to convert the line number floats to text integers
def flotToInt(text):
    if '.0' in text:
        return text[:text.rfind('.0')]
    return text

# This will be used later to check meta data line number to make sure they are
# whole numbers (integers)
def validMetaData(n):
    if n%2 == 0 or (n+1)%2 == 0:
        return True
    return False
    
# Get the Sequence & Table Numbers
print('Downloading Sequence and Table Number Lookup')
lookupURL = baseURL + 'Sequence_Number_and_Table_Number_Lookup.txt'
converter = {'Sequence Number': np.str} # Change the data type from the default way pandas reads it in
lookup = pd.read_csv(lookupURL, converters=converter)
# Change the string numbers to actual numbers
lookup['Line Number'] = pd.to_numeric(lookup['Line Number'], errors='coerce')
sequenceNumbers = lookup[['Table ID','Sequence Number']].drop_duplicates()

# Iterate through the state list
for stateAbreviation, stateName in stateDict.iteritems():
    print('Downloading ACS data for ' + stateAbreviation)
    stateDownloadURL = downloadURL + stateName + '/All_Geographies_Not_Tracts_Block_Groups/'
    
    # Grab the geography file once although we will use it more than once
    geoFileName = 'g' + str(referenceYear) + str(periodCovered) + stateAbreviation.lower() + '.csv'    
    geoURL = stateDownloadURL + geoFileName
    converter = {0: np.str, 1: np.str, 2: np.str, 3: np.str, 4: np.str} # make these variables strings
    geo = pd.read_csv(geoURL, header=None, converters=converter, low_memory=False)
    # Rename data frame
    geo.columns = ['FILEID', 'STUSAB', 'SUMLEVEL', 'COMPONENT', 'LOGRECNO', 'US', 'REGION', 'DIVISION', 'STATECE', 'STATE', 'COUNTY', 'COUSUB', 'PLACE', 'TRACT', 'BLKGRP', 'CONCIT', 'AIANHH', 'AIANHHFP', 'AIHHTLI', 'AITSCE', 'AITS', 'ANRC', 'CBSA',  'CSA', 'METDIV', 'MACC', 'MEMI', 'NECTA', 'CNECTA', 'NECTADIV ', 'UA', 'BLANK', 'CDCURR', 'SLDU', 'SLDL', 'BLANK', 'BLANK', 'ZCTA5', 'SUBMCD', 'SDELM', 'SDSEC', 'SDUNI', 'UR', 'PCI', 'BLANK', 'BLANK', 'PUMA5', 'BLANK', 'GEOID', 'NAME', 'BTTR', 'BTBG', 'BLANK']
    # Grab only the columns that we want
    geo = geo[['LOGRECNO', 'GEOID', 'NAME']]
    
    # Iterate through the table list
    for acsTable in acsTables:
        # Get the sequence number for the acs table
        sequenceNumber = sequenceNumbers['Sequence Number'].values[sequenceNumbers['Table ID'].values == acsTable][0]       
        
        # Create the data frame column names
        # Since the data does not have a header we need to create a list of 
        # column names we can use to name the columns
        columnStart = ['File Type', 'Estimate Type', 'State', 'ltter#', 'SeqNum', 'LOGRECNO']
        columnNames = list(columnStart)
        estColumnNames = list(columnStart)
        moeColumnNames = list(columnStart)
        
        metaData = lookup[lookup['Sequence Number'] == sequenceNumber]
        # Remove rows without a line number
        metaData = metaData[np.isfinite(metaData['Line Number'])]
        # Remove the rows with a .5 ending
        metaData = metaData[metaData['Line Number'].apply(validMetaData)]        
        # Create the begining of the column name
        metaData['columnNameBase'] = metaData['Table ID'] + '_' + metaData['Line Number'].map(np.str)
        # Remove the fraction part from the float
        metaData['columnNameBase'] = metaData['columnNameBase'].apply(flotToInt)
        # Create estimate and moe column names
        metaData['estColumnName'] = metaData['columnNameBase'] + '_EST'
        metaData['moeColumnName'] = metaData['columnNameBase'] + '_MOE'
        estColumnNames.extend(metaData['estColumnName'].tolist())
        moeColumnNames.extend(metaData['moeColumnName'].tolist())
        
        print('Getting ' + acsTable + ' data')
        # Download the ACS data        
        zipFileName = str(referenceYear) + str(periodCovered) + stateAbreviation.lower() + sequenceNumber + '000.zip'
        tableURL = stateDownloadURL + zipFileName
        r = requests.get(tableURL)
        # Extract the files
        zipFile = zipfile.ZipFile(StringIO.StringIO(r.content))
        zipFile.extractall()
        # Build a list of files that were zipped
        ZipNameList = zipFile.namelist()
        
        print('Processing ' + acsTable + ' data')
        # Read in the estimates and margins of errors        
        converter = {0: np.str, 1: np.str, 2: np.str, 3: np.str, 4: np.str, 5: np.str} # make these variables strings
        estimate = pd.read_csv(ZipNameList[0], header=None, converters=converter)
        moe = pd.read_csv(ZipNameList[1], header=None, converters=converter)
        # Rename the columns        
        estimate.columns = estColumnNames
        moe.columns = moeColumnNames

        # Select the columns with the ACS table name in their name
        estCols = columnStart + [col for col in estimate.columns if acsTable in col]
        estimate = estimate[estCols]
        moeCols = columnStart + [col for col in moe.columns if acsTable in col]
        moe = moe[moeCols]
        
        # Now we are ready to merge the estimate, moe and geography data frames
        # First we need to drop the moe estimate types column b/c it messes up 
        # the merge
        moe = moe.drop('Estimate Type', 1)
        
        # Now we merge the estimates and geography data. Then merge in the moes
        acsData = estimate.merge(geo)
        acsData = acsData.merge(moe)
        
        # We need to set up the final data frame.  First we start with our
        # column names list and add in the geography variables.  Next we get
        # the estimate and moe variables however they will be unsorted (the 
        # estimate is not next to the moe).  We will sort this list and add it
        # to our column names list.
        geoCols = ['GEOID', 'NAME']
        columnNames.extend(geoCols)
        unsortedCols = list(set(acsData.columns) - set(columnStart) - set(geoCols))
        sortedCols = sorted(unsortedCols)
        columnNames.extend(sortedCols)
        
        # Create the data frame with the columns we want in the right order
        acsData = acsData[columnNames]

        # Save the ACS data as an Excel file
        fileName = acsTable + '-' + stateAbreviation + '.xlsx'
        print('Saving ' + fileName)
        acsData.to_excel(fileName, index=False)
        
        # Delete the files we unzipped
        os.remove(ZipNameList[0])
        os.remove(ZipNameList[1])