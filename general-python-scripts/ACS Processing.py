'''
================================================================================
ACS Processing for Community Profiles Python 3 Script

In order to use this script you must set the root_dir variable to the location
where the ACS spreadsheets are kept.  They need to be in a folder per state.

There also needs to be an id spreadsheet that holds the logical record number
ids.  This file name must match the directory name with a dash and ids.  For
example - the New York spreadsheets are stored in the NY directory and the id
spreadsheet is named NY-ids.
================================================================================
'''
# NOTE: You cannot use the \ to break apart the path.  Use / instead!
root_dir = 'H:/Data Warehouse/Census Bureau/American Community Survey/2010-14/'
'''
================================================================================
You shouldn't have to edit beyond this point
================================================================================
'''
from os.path import isfile, isdir, join
from os import listdir
from xlrd import open_workbook
import xlsxwriter

# This function handles the reading of the ids spreadhseets
def get_ids(root_dir, state_abr):
    ## Get the list of ids we need to look for
    ids = list()
    file_path = root_dir + state_abr + '-ids.xlsx'
    ws = open_workbook(file_path).sheet_by_index(0)
    col=0
    for row in range(ws.nrows):
        ids.append(ws.cell(row, col).value)
    return ids

# Get a list of directories that hold data
dirs = [d for d in listdir(root_dir) if isdir(join(root_dir, d))]

# This holds the complete list of files that have been downloaded
file_names = list()

# Fill up the files list
for state_abr in dirs:
    dir_path = join(root_dir, state_abr)
    # Get the files in the directory
    files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    for file_name in files:
        if file_name not in file_names:
            file_names.append(file_name)

# Now that we have a complete list let's create a new spreadsheet with all the
# states data in one place
progress = 0
for file_name in file_names:
    n_files = len(file_names)
    progress = progress + 1
    print('Curently working on: '+file_name+' ('+str(progress)+' out of '+str(n_files)+' files)')
    split_file_name = file_name.split('.')
    new_file_name = split_file_name[0]+'.xlsx'
    new_file_path = join(root_dir, new_file_name)
    new_wb = xlsxwriter.Workbook(new_file_path)
    new_ws = new_wb.add_worksheet()
    new_row = 0
    for state_abr in dirs:
        file_path = join(root_dir, state_abr, file_name)
        if not isfile(file_path):
            print(' '+state_abr+' does not have data.')
        if isfile(file_path):
            ids = get_ids(root_dir, state_abr)
            ids_to_find = len(ids)
            print(' '+state_abr+' data exists.  Searching for '+str(ids_to_find)+' records.')
            ids_found = 0
            ws = open_workbook(file_path).sheet_by_index(0)
            for row in range(ws.nrows):
                if ids_found < ids_to_find:
                    lookup_id = ws.cell(row, 5).value
                    if lookup_id in ids:
                        # The following line checks to make sure we don't duplicate
                        # a header line (ids_found == 0) on a non-header row
                        # (new_row > 0)
                        if (ids_found == 0 and new_row == 0) or ids_found > 0:
                            for col in range(ws.ncols):
                                new_ws.write(new_row, col, ws.cell(row, col).value)
                        # Remove the id from the list so we don't search for it again
                        ids.remove(lookup_id)
                        if not (ids_found == 0 and new_row > 0):
                            # Since we skipped the duplicate header row we don't
                            # want to advance the new_row variable
                            new_row = new_row + 1
                        ids_found = ids_found + 1
    new_wb.close()
print('Done!')
