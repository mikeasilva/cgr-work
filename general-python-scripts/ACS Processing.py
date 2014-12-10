import datetime

print(str(datetime.datetime.now().time())+' <- Begin Script')

## NOTE: You cannot use the \ to break apart the path.  Use / instead!
root_dir = 'H:/Data Warehouse/Census Bureau/American Community Survey/2009-13/'
state_abr = 'FL'
## Import the libraries we need to make the script work
from os import listdir
from os import walk
from os.path import isfile, isdir, join
from xlrd import open_workbook
import xlsxwriter

## This function opens a xlsx workbook and returns the worksheet
def get_worksheet(file_path, sheet_name):
    wb = open_workbook(file_path, on_demand=True)
    return(wb.sheet_by_name(sheet_name))

## This function
def process_acs_spreadsheet(file_name, ids, root_dir, state_abr):
    ids_to_find = len(ids)
    print(str(datetime.datetime.now().time()) + ' <- Searching for ' + str(ids_to_find) + ' geographies in '+file_name)
    if ids_to_find > 0:
        # Open the spreadsheet (this takes a while)
        file_path = root_dir + state_abr + '/' + file_name
        print(str(datetime.datetime.now().time()) + ' <- Opening the file')
        ws = open_workbook(file_path).sheet_by_index(0)

        # Create the new spreadsheet
        new_file_path = root_dir + 'Processed/' + state_abr + '/' + file_name
        new_wb = xlsxwriter.Workbook(new_file_path)
        new_ws = new_wb.add_worksheet()
        # Initialize vars
        ids_found = 0
        for row in range(ws.nrows):
            if ids_found < ids_to_find:
                lookup_id = ws.cell(row, 5).value
                if lookup_id in ids:
                    for col in range(ws.ncols):
                        new_ws.write(ids_found, col, ws.cell(row, col).value)
                    ids.remove(lookup_id)
                    ids_found = ids_found + 1
        new_wb.close()
        print(str(datetime.datetime.now().time()) + ' <- Done')

def get_ids(root_dir, state_abr):
    ## Get the list of ids we need to look for
    ids_data = []
    file_path = root_dir + state_abr + '-ids.xlsx'
    ws = open_workbook(file_path).sheet_by_index(0)
    col=0
    for row in range(ws.nrows):
        ids_data.append(ws.cell(row, col).value)
    return ids_data

dir_path = join(root_dir, state_abr)
## Get the files in the sub directory
files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

for file_name in files:
    ids = get_ids(root_dir, state_abr)
    process_acs_spreadsheet(file_name, ids, root_dir, state_abr)
