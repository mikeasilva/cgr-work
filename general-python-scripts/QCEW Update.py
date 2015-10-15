# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 16:02:05 2015

@author: Michael
"""

"""
QCEW Data Download Page
http://www.bls.gov/cew/datatoc.htm
"""

""" 
============================= SCRIPT PARAMETERS ===============================
"""    
# The following is a list of the files we want to extract from the zip archive
# If you want to add to this list be sure to include a county and state    
#file_starts = ['county/cn12fl', 'county/CN12FL', 'county/cn36ny', 'county/CN36NY', 'state/st12fl', 'state/ST12FL', 'state/st36ny', 'state/ST36NY', 'msa/allmsa', 'msa/ALLMSA', 'national/nt00us', 'national/NT00US']
file_starts = ['county/cn12fl', 'county/CN12FL', 'county/cn36ny', 'county/CN36NY', 'state/st12fl', 'state/ST12FL', 'state/st36ny', 'state/ST36NY', 'national/nt00us', 'national/NT00US']

start_year = 1999
end_year = 2014

# Set the following to False if you DO NOT want to create a new update table.
# You may want to do this when you need to start the process back up after an
# error (i.e. bad zip file).
create_database_table_from_scratch = True

""" 
====== DO NOT EDIT BELOW THIS POINT UNLESS YOU KNOW WHAT YOU ARE DOING! ======
"""

""" 
============================== IMPORT LIBRARIES ===============================
""" 
import pandas as pd
import zipfile
import os
from urllib2 import urlopen, URLError, HTTPError
import struct
import MySQLdb
import shutil
""" 
============================== SCRIPT FUNCTIONS ===============================
""" 
def download_file(url):
    # Open the url
    try:
        f = urlopen(url)
        print "  Downloading " + url

        # Open our local file for writing
        with open(os.path.basename(url), "wb") as local_file:
            local_file.write(f.read())
    
    #handle errors
    except HTTPError, e:
        print "HTTP Error:", e.code, url
    except URLError, e:
        print "URL Error:", e.reason, url
        
def unzip(file_path, member):
    # This function unzips the members
    print "  Decompressing " + file_path
    zfile = zipfile.ZipFile(file_path)
    zfile.extractall('.', member)

def get_file_name_list(file_starts, years):
    # This function creates a list of the files we are looking for in the zip
    # archives.  It builds file names from their starts adding in the year and
    # the enb extension.   
    file_name_list = list()
    for f in file_starts:
        for y in years:
            y = right(str(y),2)
            file_name = f + str(y) + '.enb'
            file_name_list.append(file_name)
            file_name = f + str(y) + '.ENB'
            file_name_list.append(file_name)
    return file_name_list

def right(s, amount):
    return s[-amount:]
    
def get_intersection(a, b):
    # This returns the intersection of two lists
    return list(set(a) & set(b))        

def get_complement(a, b):
    # This returns the complement (not intersection) of two lists
    # Note: order does matter for this function!
    return list(set(a) - set(b))
    
def db_convert(fields, db_types):
    ## This converts elements in the fields list to the right data base type    
    for idx in range(len(db_types)):
        val = db_types[idx]
        if val == 'Numeric':
            fields[idx] = int(fields[idx])
    return(fields)

""" 
================================== PROCESS FLOW ===============================
"""

# Connect to MySQL Database
mydb = MySQLdb.connect(host='host',
    user='user',
    passwd='passwd',
    db='db')
cursor = mydb.cursor()

if create_database_table_from_scratch:
    ## Create clean update table
    cursor.execute('DROP TABLE IF EXISTS `BLS_QCEW_Data_UPDATE`')
    
    cursor.execute('CREATE TABLE IF NOT EXISTS `BLS_QCEW_Data_UPDATE` ( \
    `Prefix` varchar(3) DEFAULT NULL, `Area` varchar(5) DEFAULT NULL, \
    `Datatype` varchar(1) DEFAULT NULL, `Size` int(1) DEFAULT NULL, \
    `Ownership` varchar(1) DEFAULT NULL, `Industry` varchar(6) DEFAULT NULL, \
    `Year` int(4) DEFAULT NULL, `Aggregation` int(2) DEFAULT NULL, \
    `Disclosure Q1` varchar(1) DEFAULT NULL, \
    `Establishment Q1` int(8) DEFAULT NULL, `Jan Emp` int(9) DEFAULT NULL, \
    `Feb Emp` int(9) DEFAULT NULL, `Mar Emp` int(9) DEFAULT NULL, \
    `TQW Q1` bigint(15) DEFAULT NULL, `TaxQW Q1` bigint(15) DEFAULT NULL, \
    `QC Q1` int(13) DEFAULT NULL, `AWW Q1` int(8) DEFAULT NULL, \
    `Disclosure Q2` varchar(1) DEFAULT NULL, \
    `Establishment Q2` int(8) DEFAULT NULL, `Apr Emp` int(9) DEFAULT NULL, \
    `May Emp` int(9) DEFAULT NULL, `Jun Emp` int(9) DEFAULT NULL, \
    `TQW Q2` bigint(15) DEFAULT NULL, `Tax QW Q2` bigint(15) DEFAULT NULL, \
    `QC Q2` int(13) DEFAULT NULL, `AWW Q2` int(8) DEFAULT NULL, \
    `Disclosure Q3` varchar(1) DEFAULT NULL, \
    `Establishment Q3` int(8) DEFAULT NULL, `Jul Emp` int(9) DEFAULT NULL, \
    `Aug Emp` int(9) DEFAULT NULL, `Sep Emp` int(9) DEFAULT NULL, \
    `TQW Q3` bigint(15) DEFAULT NULL, `Tax QW Q3` bigint(15) DEFAULT NULL, \
    `QC Q3` int(13) DEFAULT NULL, `AWW Q3` int(8) DEFAULT NULL, \
    `Disclosure Q4` varchar(1) DEFAULT NULL, \
    `Establishment Q4` int(8) DEFAULT NULL, `Oct Emp` int(9) DEFAULT NULL, \
    `Nov Emp` int(9) DEFAULT NULL, `Dec Emp` int(9) DEFAULT NULL, \
    `TQW Q4` bigint(15) DEFAULT NULL, `TaxQW Q4` bigint(15) DEFAULT NULL, \
    `QC Q4` int(13) DEFAULT NULL, `AWW Q4` int(8) DEFAULT NULL, \
    `Disclosure Y` varchar(1) DEFAULT NULL, \
    `Establishments Y` int(8) DEFAULT NULL, `Emp Y` int(9) DEFAULT NULL, \
    `Total Wages Y` bigint(15) DEFAULT NULL, `Tax Wages Y` bigint(15) DEFAULT NULL, \
    `AC Y` int(13) DEFAULT NULL, `AWW y` int(8) DEFAULT NULL, \
    `Average Annual Pay` int(9) DEFAULT NULL, \
    KEY `Area` (`Area`), KEY `Year` (`Year`), KEY `Industry` (`Industry`), \
    KEY `Ownership` (`Ownership`) ) ENGINE=MyISAM DEFAULT CHARSET=utf8;')

# Build the list of the files we need to extract from the zip files
file_years = range(start_year - 1900, end_year - 1900 + 1)
file_name_list = get_file_name_list(file_starts, file_years)

# Get the year range the script will process
years = range(start_year, end_year + 1)

# Get the specification of the fixed width files
enb_layout = pd.read_csv('http://www.bls.gov/cew/doc/layouts/enb_layout.csv')
db_types = list(enb_layout.data_type)

# Taken from http://stackoverflow.com/questions/4914008/efficient-way-of-parsing-fixed-width-files-in-python
fieldwidths = list(enb_layout.field_length)
fmtstring = ' '.join('{}{}'.format(abs(fw), 'x' if fw < 0 else 's') for fw in fieldwidths)
fieldstruct = struct.Struct(fmtstring)
parse = fieldstruct.unpack_from

# Get the contents of the working directory.  This will be used later to 
# cleanup files that are added.
initial_directory = os.listdir(os.getcwd())

# Begin the processes
for year in years:
    print 'Processing ' + str(year)
    file_path = str(year) + '_all_enb.zip'
    
    # Download the zip file
    qcew_url = 'http://www.bls.gov/cew/data/files/' + str(year) + '/enb/' + file_path
    download_file(qcew_url)
    
    # Unzip only the files found in our list
    zipfile_name_list = zipfile.ZipFile(file_path).namelist()
    unzip_me = get_intersection(file_name_list, zipfile_name_list)
    unzip(file_path, unzip_me)
    
    # Read the file and import it into the database
    for f in unzip_me:
        print "  Parsing " + f
        a_file = open(f, "r")
        for line in a_file.readlines():
            fields = parse(line)
            fields = list(fields)
            #try:
            fields = db_convert(fields, db_types)
            # Insert data into table
            cursor.execute('INSERT INTO `BLS_QCEW_Data_UPDATE`(`Prefix`, \
            `Area`, `Datatype`, `Size`, `Ownership`, `Industry`, `Year`, \
            `Aggregation`, `Disclosure Q1`, `Establishment Q1`, `Jan Emp`, \
            `Feb Emp`, `Mar Emp`, `TQW Q1`, `TaxQW Q1`, `QC Q1`, `AWW Q1`, \
            `Disclosure Q2`, `Establishment Q2`, `Apr Emp`, `May Emp`, \
            `Jun Emp`, `TQW Q2`, `Tax QW Q2`, `QC Q2`, `AWW Q2`, \
            `Disclosure Q3`, `Establishment Q3`, `Jul Emp`, `Aug Emp`, \
            `Sep Emp`, `TQW Q3`, `Tax QW Q3`, `QC Q3`, `AWW Q3`, \
            `Disclosure Q4`, `Establishment Q4`, `Oct Emp`, `Nov Emp`, \
            `Dec Emp`, `TQW Q4`, `TaxQW Q4`, `QC Q4`, `AWW Q4`, \
            `Disclosure Y`, `Establishments Y`, `Emp Y`, `Total Wages Y`, \
            `Tax Wages Y`, `AC Y`, `AWW y`, `Average Annual Pay`)' \
            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', fields)
        a_file.close()
 
mydb.commit()
cursor.close()

# Cleanup the working directory.
current_directory = os.listdir(os.getcwd())
new_files = get_complement(current_directory, initial_directory)
for f in new_files:
    if os.path.isfile(f):
        os.remove(f)
    else:
        shutil.rmtree(f)
    
print "Done"