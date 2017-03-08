# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 08:30:12 2016

@author: Michael Silva
"""

import pandas as pd
from sqlalchemy import create_engine
import requests, os, zipfile, shutil, struct

"""
============================= SCRIPT PARAMETERS ===============================
"""
end_year = 2015
start_year = 1999

# The following is a list of the files we want to extract from the zip 
# archive.  If you want to add to this list be sure to include a county 
# and state
file_starts = ['county/cn12fl', 'county/CN12FL', 'county/cn10de', 'county/CN10DE', 'county/cn17il', 'county/CN17IL', 'county/cn25ma', 'county/CN25MA', 'county/cn36ny', 'county/CN36NY', 'state/st12fl', 'state/ST12FL', 'state/st10de', 'state/ST10DE', 'state/st17il', 'state/ST17IL', 'state/st25ma', 'state/ST25MA', 'state/st36ny', 'state/ST36NY', 'state/st44ri', 'state/ST44RI', 'msa/allmsa', 'msa/ALLMSA', 'national/nt00us', 'national/NT00US']

"""
====== DO NOT EDIT BELOW THIS POINT UNLESS YOU KNOW WHAT YOU ARE DOING! ======
"""


"""
============================== SCRIPT FUNCTIONS ===============================
"""
def get_file_name_list(file_starts, years):
    # This function creates a list of the files we are looking for in 
    # the zip archives.  It builds file names from their starts adding 
    # in the year and the enb extension.
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

def download_with_progress_bar(url, file_name):
    response = requests.get(url, stream=True)
    total_length = response.headers.get('content-length')
    if total_length is not None:
        fh = open(file_name, 'wb')
        dl=0
        total_length = int(total_length)
        for data in response.iter_content(chunk_size=4096):
            dl += len(data)
            done = int(50 * dl / total_length)
            print("\r[%s%s]" % ('=' * done, ' ' * (50-done)), end='')
            if not data:
                break
            else:
                fh.write(data)
        fh.close()
        print('')

def get_intersection(a, b):
    # This returns the intersection of two lists
    return list(set(a) & set(b))

def get_complement(a, b):
    # This returns the complement (not intersection) of two lists
    # Note: order does matter for this function!
    return list(set(a) - set(b))
    
def unzip(file_name, member):
    # This function unzips the members
    print(" Decompressing " + file_name)
    zfile = zipfile.ZipFile(file_name)
    zfile.extractall('.', member)
    
def get_int_or_float(v):
    # This is used in the pandas converters
    number_float = float(v)
    number_int = int(number_float)
    return number_int if number_float == number_int else number_float
    
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

# Connect to CGR's Data Warehouse
print ("Connecting to CGR's Data Warehouse")
engine = create_engine('mysql+pymysql://USER:PASSWORD@SERVER/DATABASE')
conn = engine.connect()

# Drop old data table and create placeholder
conn.execute('DROP TABLE IF EXISTS `BLS_QCEW_Data_UPDATE`')
# This next step is needed because the column names in BLS_QCEW_Data_UPDATE
# do not follow the ENB specifications
conn.execute('CREATE TABLE `BLS_QCEW_Data_UPDATE` LIKE `BLS_QCEW_Data`')

# Get the specification of the fixed width files
print('Getting file layout')
enb_layout = pd.read_csv('http://www.bls.gov/cew/doc/layouts/enb_layout.csv')
db_types = list(enb_layout.data_type)

# Get the field lengths names and build the converters dictionary
field_length = list(enb_layout.field_length)

# Taken from http://stackoverflow.com/questions/4914008/efficient-way-of-parsing-fixed-width-files-in-python
fieldwidths = list(enb_layout.field_length)
fmtstring = ' '.join('{}{}'.format(abs(fw), 'x' if fw < 0 else 's') for fw in fieldwidths)
fieldstruct = struct.Struct(fmtstring)
unpack = fieldstruct.unpack_from
parse = lambda line: tuple(s.decode() for s in unpack(line.encode()))
 
# Build the list of the files we need to extract from the zip files
file_years = range(start_year - 1900, end_year - 1900 + 1)
file_name_list = get_file_name_list(file_starts, file_years)

# Begin the processes
for year in range(start_year, end_year + 1):
    file_name = str(year) + '_all_enb.zip'
    if not os.path.exists(file_name):
        # Download the zip file
        zip_file_url = 'http://www.bls.gov/cew/data/files/' + str(year) + '/enb/' + file_name
        print('Requesting '+zip_file_url)
        download_with_progress_bar(zip_file_url, file_name)
    else:
        print(file_name+' found!')
    
    # Get the names of the files in the zip file 
    zipfile_name_list = zipfile.ZipFile(file_name).namelist()
    unzip_me = get_intersection(file_name_list, zipfile_name_list)
    unzip(file_name, unzip_me)

    # Read the file and import it into the database
    for f in unzip_me:
        print("  Parsing " + f)
        a_file = open(f, "r")
        for line in a_file.readlines():
            fields = parse(line)
            fields = list(fields)
            #try:
            fields = db_convert(fields, db_types)
            # Insert data into table
            conn.execute('INSERT INTO `BLS_QCEW_Data_UPDATE`(`Prefix`, \
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
        
    # Cleanup
    print(" Cleaning up")
    folders = list()
    for f in unzip_me:
        os.remove(f)
        f_split = f.split("/")
        if f_split[0] not in folders:
            folders.append(f_split[0])
    for folder in folders:
        shutil.rmtree(folder)
        
conn.close()