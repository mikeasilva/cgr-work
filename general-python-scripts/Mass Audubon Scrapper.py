import requests
from bs4 import BeautifulSoup
import pandas as pd

areatypes = ['Town', 'County', 'Watershed', 'Regional Planning Area', 'Ecoregion', 'Geophysical Setting', 'State']
areatypes = ['Town', 'County', 'State']
data = list()

for areatype in areatypes:
	url = 'http://www.massaudubon.org/losingground/lgv/areatype_query.php'
	payload = {'areatype': areatype}
	r = requests.post(url, data=payload)
	soup = BeautifulSoup(r.text, 'xml')

	for row in soup.find_all('row'):
		attrs = row.attrs
		id = attrs['id']
		name = attrs['name']
		print('Getting data for: '+name)
		url = 'http://www.massaudubon.org/our-conservation-work/advocacy/shaping-the-future-sustainable-planning/publications-community-resources/losing-ground-report/losing-ground-fifth-edition-statistics/(areaid)/'+id
		response = requests.get(url)
		page = BeautifulSoup(response.text, 'lxml')
		for tr in page.find_all('tr'):
			td = tr.find_all('td')
			td = [ele.text.strip() for ele in td]
			td = [name] + [areatype] + [id] + td
			data.append(td)
print('Saving file')
df=pd.DataFrame(data, columns=['Name', 'Area Type', 'Area ID', 'Description', 'Value', 'Rank'])	
writer = pd.ExcelWriter('MASS Audubon Scrapper Output.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.save()
print('Done')