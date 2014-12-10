from os.path import isfile, isdir, join
from os import listdir
from xlrd import open_workbook
import xlsxwriter

# NOTE: You cannot use the \ to break apart the path.  Use / instead!
root_dir = 'H:/Data Warehouse/Census Bureau/American Community Survey/2009-13/'

dirs = [d for d in listdir(root_dir) if isdir(join(root_dir, d))]

def get_ids(root_dir, state_abr):
    ## Get the list of ids we need to look for
    ids = list()
    file_path = root_dir + state_abr + '-ids.xlsx'
    ws = open_workbook(file_path).sheet_by_index(0)
    col=0
    for row in range(ws.nrows):
        ids.append(ws.cell(row, col).value)
    return ids

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
    new_file_path = join(root_dir, file_name)
    new_wb = xlsxwriter.Workbook(new_file_path)
    new_ws = new_wb.add_worksheet()
    new_row = 0
    first_line_not_printed = True
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
                        for col in range(ws.ncols):
                            if (ids_found == 0 and first_line_not_printed) or ids_found > 0:
                                new_ws.write(new_row, col, ws.cell(row, col).value)
                            if ids_found == 0:
                                first_line_not_printed = False
                        ids.remove(lookup_id)
                        new_row = new_row + 1
                        ids_found = ids_found + 1
    new_wb.close()
print('Done!')
