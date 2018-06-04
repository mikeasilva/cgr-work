import PyPDF2
import pandas as pd

pdf_file_name = '2018_tentative_assessment_roll.pdf'
fh = open(pdf_file_name, 'rb')
pdf = PyPDF2.PdfFileReader(fh)

end_page_string = '*' * 132
start_record_string = '**** '

extracted_data = dict()
record_count = 0

convert_me = set()

for i in range(pdf.numPages):
    page = pdf.getPage(i).extractText()
    tax_map_parcel_number = 'FAKE TAX MAP NUMBER'
    look_for_data = False
    lines = page.split('\n')
    current_line = 0

    get_data = False
    for line in lines:
        if tax_map_parcel_number in line and get_data:
            a = line.replace(tax_map_parcel_number, '').strip().split('  ')
            extracted_data[tax_map_parcel_number]['prop_type'] = a[0].strip()

        if 'FULL MARKET VALUE' in line and get_data:
            fmv = line.replace('FULL MARKET VALUE', '').strip().split(' ')
            fmv = fmv[0].replace(',', '')
            extracted_data[tax_map_parcel_number]['value_full_market'] = fmv
            convert_me.add('value_full_market')

        if 'TAXABLE VALUE' in line and get_data:
            tv = line.split('TAXABLE VALUE')
            tv_type = tv[0].strip().split('  ')
            tv_type = tv_type[len(tv_type)-1].strip().lower()
            taxable_value = tv[1].strip().split(' ')
            key = 'value_taxable_'+tv_type
            taxable_value = taxable_value[0].replace(',', '')
            extracted_data[tax_map_parcel_number][key] = taxable_value
            convert_me.add(key)

        if start_record_string in line and end_page_string not in line:
            tax_map_parcel_number = line.split(' ')[1]
            extracted_data[tax_map_parcel_number] = {'page': (i + 1),
                                                     'record': record_count}
            record_count = record_count + 1
            get_data = True

        if end_page_string in line:
            get_data = False

        current_line = current_line + 1

df = pd.DataFrame.from_dict(extracted_data, orient='index')

convert_me = list(convert_me)
df[convert_me] = df[convert_me].apply(pd.to_numeric, errors='coerce')
df = df.sort_values('record').reset_index()

excel_file_name = pdf_file_name.split('.')[0] + '.xlsx'
writer = pd.ExcelWriter(excel_file_name)
df.to_excel(writer, 'Sheet1', index=False)
writer.save()
