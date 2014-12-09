import datetime

print(str(datetime.datetime.now().time())+' <- Begin Script')

## NOTE: You cannot use the \ to break apart the path.  Use / instead!
root_dir = 'H:/Data Warehouse/Census Bureau/American Community Survey/2009-13/'

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
def process_acs_spreadsheet(file_name, ids, root_dir):
    ids_to_find = len(ids)
    file_path = root_dir + 'NY/' + file_name
    print(str(datetime.datetime.now().time()) + ' <- Before opening ' + file_path)
    ws = open_workbook(file_path).sheet_by_index(0)
    print(str(datetime.datetime.now().time()) + ' <- After opening ' + file_path)

    new_file_path = root_dir + 'Processed/' + file_name
    new_wb = xlsxwriter.Workbook(new_file_path)
    new_ws = new_wb.add_worksheet()

    ids_found = 0

    for row in range(ws.nrows):
        if ids_found < ids_to_find:
            row_id = ws.cell(row, 5).value
            if row_id in ids:
                for col in range(ws.ncols):
                    new_ws.write(ids_found, col, ws.cell(row, col).value)
                ids.remove(row_id)
                ids_found = ids_found + 1

    new_wb.close()

## Get the list of ids we need to look for
ids_data = []
file_path = root_dir + 'ids.xlsx'
print(str(datetime.datetime.now().time())+' <- Before opening ids.xlsx')
ws = get_worksheet(file_path, '2009-13 ACS')
print(str(datetime.datetime.now().time())+' <- After opening ids.xlsx')
col=0
for row in range(ws.nrows):
    ids_data.append(ws.cell(row, col).value)

ids_to_find = len(ids_data)

all_subdirs = ['NY']
## Loop through all the sub directories
for d in all_subdirs:
    dir_path = join(root_dir, d)
    ## Get the files in the sub directory
    files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    ## Loop through each file
    for file_name in files:
        print(str(datetime.datetime.now().time())+' <- Starting on '+file_name)
        process_acs_spreadsheet(file_name, ids_data, root_dir)