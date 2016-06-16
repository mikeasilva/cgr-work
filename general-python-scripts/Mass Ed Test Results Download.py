# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 12:37:17 2016

@author: Michael
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

start_year = 2000
end_year = 2015

def select_to_dict(select):
    select_dict = {}
    for option in select.find_all('option'):
        select_dict[option['value']] = option.text
    del(select_dict[''])
    return(select_dict)

def soup_to_df(soup):
    table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_mcasGridView'})
    records = []
    header = []
    for tr in table.findAll("tr"):
        row = {}
        i=0
        for th in tr.findAll("th"):
            header.append(th.text)
            i=i+1
        
        for td in tr.findAll("td"):
            row[i] = td.text
            #print(str(i)+' '+td.text)
            i=i+1

        if len(row) > 0: 
            records.append(row)
    df = pd.DataFrame(records)
    if len(records) > 1 :
        df.columns = header
    return(df)
    
url = 'http://profiles.doe.mass.edu/state_report/mcas.aspx'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'lxml')

#years = select_to_dict(soup.find('select', {'id': 'ctl00_ContentPlaceHolder1_year'}))
grades = select_to_dict(soup.find('select', {'id': 'ctl00_ContentPlaceHolder1_grade'}))
student_groups = select_to_dict(soup.find('select', {'id': 'ctl00_ContentPlaceHolder1_studentGroup'}))

df = soup_to_df(soup)

for year in range(start_year, end_year+1):
    for grade in grades:
        for student_group in student_groups:
            print('Getting Test Results for Grade '+grades[grade]+' '+student_groups[student_group]+' Students in '+str(year))
            post_vars = {'__EVENTARGUMENT':'','__EVENTTARGET':'', '__VIEWSTATEGENERATOR':'62EDAC75', 'ctl00$ContentPlaceHolder1$Continue':'View Report', 'ctl00$ContentPlaceHolder1$grade':grade, 'ctl00$ContentPlaceHolder1$reportType':'DISTRICT','ctl00$ContentPlaceHolder1$schoolType':'All', 'ctl00$ContentPlaceHolder1$studentGroup':student_group,'ctl00$ContentPlaceHolder1$year':year}
            r = requests.post(url, data = post_vars)
            r_soup = BeautifulSoup(r.text, 'lxml')
            temp_df = soup_to_df(r_soup)
            if 0 not in temp_df.columns.values:
                temp_df['Grade'] = grades[grade]
                temp_df['Student Group'] = student_groups[student_group]
                temp_df['Year'] = year
                # Append data frame if it exists
                if 'mass_edu_data' in locals():
                    mass_edu_data = mass_edu_data.append(temp_df, ignore_index=True)
                else:
                    mass_edu_data = temp_df

# Convert string values to numeric
print('Converting Data')
numeric_columns = list(mass_edu_data.columns.values)
numeric_columns.remove('Org Name')
numeric_columns.remove('Org Code')
numeric_columns.remove('Subject')
numeric_columns.remove('Grade')
numeric_columns.remove('Student Group')
mass_edu_data[numeric_columns] = mass_edu_data[numeric_columns].apply(pd.to_numeric, errors='ignore')

# Rearrange Column Order
print('Reordering Columns')
cols = list(df.columns.values)
append_to_cols = set(list(mass_edu_data.columns.values)) - set(cols)
for item in append_to_cols:
    cols.append(item)
# Add the Year to the end of the list
cols.remove('Year')
cols.append('Year')
mass_edu_data = mass_edu_data[cols]

# Save it as an Excel file
print('Writing Data')
writer = pd.ExcelWriter('H:/Data Warehouse/25-Massachusetts/Department of Elementary & Secondary Education/MCAS Data.xlsx', engine='xlsxwriter')
mass_edu_data.to_excel(writer,'MA_MCAS_Data', index=False)
writer.save()
