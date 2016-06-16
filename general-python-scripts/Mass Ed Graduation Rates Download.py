# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 10:31:04 2016

@author: Michael
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

def select_to_dict(select):
    select_dict = {}
    for option in select.find_all('option'):
        select_dict[option['value']] = option.text
    del(select_dict[''])
    return(select_dict)

def soup_to_df(soup):
    table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_GradRateGridView'})
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
    
url = 'http://profiles.doe.mass.edu/state_report/gradrates.aspx'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'lxml')

years = select_to_dict(soup.find('select', {'id': 'ctl00_ContentPlaceHolder1_cohortYear'}))
rates = select_to_dict(soup.find('select', {'id': 'ctl00_ContentPlaceHolder1_rateType'}))
student_groups = select_to_dict(soup.find('select', {'id': 'ctl00_ContentPlaceHolder1_studentGroup'}))

df = soup_to_df(soup)

for year in years:
    for rate in rates:
        for student_group in student_groups:
            print('Getting '+rates[rate]+' Graduation Rates for '+student_groups[student_group]+' Students in '+str(year))
            post_vars = {'__EVENTARGUMENT':'',
 '__EVENTTARGET':'',
 '__EVENTVALIDATION':'/wEdAC2DQCoaIr0HdD6GWO34g0xRUkGXNeoU71fffCyoYjkdPCpoplPr0NEMT0XjFqbTT4OW26R1xDoG9eQXFVw6X48xouRxoLVtOpKxD09qRmpAqgYZSyPGII3S/fm0rDWYJSXrCDb3LUmIUmqhiftK9gA/8OXkM2Y0C+k7jKx0GvbVMWPTlCqKnu6bgtQA0NphBYLvvOK1evFVlaf+FzSdt5PolDiJ+dba1ENXAFnp3MBrXiZMYmnF8kl0LqCVUNF5lOk1mvu9SMfptGcYFh5MVQl8WRokuiBa3Eo5nm+sN4U2BCADZx6fez/uPv3PbId5onpI9Bd4G8WqAcZgvZRg3IJEMt3kPUHts1LQzwIlZK85lZyCnbmVT2sQTMk/wrXyPHa9iqr6FAw2wHolFI5q5L5oj2zfGC8NvYN/ObGkpfD1MhgzHhLkxATzUbIFJNYtLeKD9q/BUs/1X/IvTiKG6KkrgmkR7m/xXSTU5kWeOEdoxXUi1fMQEbveGpxlNzOtUTRgbPK49eChgqawPm6PmloB0Qh5u/LlpqwPt8xTAQa80uq5sOy6Ry7GPtqKXwVVy9IoIjUrsASKHzcE1x2qRMDrcceAcJidwslXUI6BPmEOU1nHV5TOQx5262E4tKUiF8e94bHD97qQlXFWrY0axNYI7z62BZEIXEJ24rcxbCA+bxKXmhWzVdzGUf/TwUBNN4OblglF9/MzT1GFceugI5fmsHxXRpxQ7Etoo2M2WGGLXGCAqLvIblw7RN6sFfLLygy9FzlhrZaOy//qBT6e+yUtTxq4Rs4zJLj8D3wMooB+/W70CrrTCx5rOekd8Nqr5RcNDXg/IcbHaoZj4oVvFSm0HCzlG/3cu6wulmdoh60/Q/ChaSHPOrnCc4CtueqPUHt9uOXifWYFqJwYSvbt7v/ujj/w0wdYbKwjIkIBr2yrsXT3FLLuwGjF+APxw+SgIz1anFQUxHtdyCp+2l7YbBTnQv9i3mq3Ioh9zUVJD92NPQ==',
 '__VIEWSTATE':'/wEPDwUKLTIzMDA3OTY1MWQYAQUqY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSRHcmFkUmF0ZUdyaWRWaWV3DzwrAAwBCAIBZG8Ip/pptO+7HSWnpgwRkGnixGFdqhDQxloNqdeDPUlv',
 '__VIEWSTATEGENERATOR':'62368C5D',
 'ctl00$ContentPlaceHolder1$Continue':'View Report',
 'ctl00$ContentPlaceHolder1$cohortYear':year,
 'ctl00$ContentPlaceHolder1$rateType':rate,
 'ctl00$ContentPlaceHolder1$reportType':'DISTRICT',
 'ctl00$ContentPlaceHolder1$studentGroup':student_group}
            r = requests.post(url, data = post_vars)
            r_soup = BeautifulSoup(r.text, 'lxml')
            temp_df = soup_to_df(r_soup)
            if 0 not in temp_df.columns.values:
                temp_df['Rate Type'] = rates[rate]
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
numeric_columns.remove('DISTRICT')
numeric_columns.remove('Org Code')
numeric_columns.remove('Rate Type')
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
writer = pd.ExcelWriter('H:/Data Warehouse/25-Massachusetts/Department of Elementary & Secondary Education/Graduation Rates.xlsx', engine='xlsxwriter')
mass_edu_data.to_excel(writer,'MA_Graduation_Rates', index=False)
writer.save()
