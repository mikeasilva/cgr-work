library(dplyr)
library(xlsx)

# The directory where the data will be stored with trailing slash
base.path <- './OES/'

# Create the base folder
if (!file.exists(base.path)){
  dir.create(base.path)
}

# Find out the release
file <- read.table('http://download.bls.gov/pub/time.series/oe/oe.release')

# Create the path where the data will be downloaded to
path <- paste0(base.path, file$release_date, "-", file$description)

if (!file.exists(path)){
  dir.create(path)
}

# Download all the OES files if they don't exist
url <- 'http://download.bls.gov/pub/time.series/oe/'
files <- c('oe.area', 'oe.areatype', 'oe.contacts', 'oe.data.1.AllData', 'oe.datatype', 'oe.footnote', 'oe.industry', 'oe.occugroup', 'oe.occupation', 'oe.release', 'oe.seasonal', 'oe.sector', 'oe.series', 'oe.statemsa', 'oe.txt')
for(file in files){
  file.path <- paste0(path,"/",file)
  if(!file.exists(file.path)){
    file.url <- paste0(url,file)
    download.file(file.url, file.path)
  }
}

# SOC Code Worker Class Definitions
#
# White-collar
# 0010-0430 Management Occupations
# 0500-0950 Business and financial operations occupations
# 1000-1240 Computer and mathematical science occupations
# 1300-1560 Architecture and engineering occupations
# 1600-1960 Life, physical, and social science occupations
# 2000-2060 Community and social service occupations
# 2100-2150 Legal occupations
# 2200-2550 Education, training, and library occupations
# 2600-2960 Arts, design, entertainment, sports, and media occupations
# 3000-3540 Healthcare practitioner and technical occupations
# 4700-4960 Sales and related occupations
# 5000-5930 Office and administrative support occupations
# 
# Service
# 3600-3650 Healthcare support occupations
# 3700-3950 Protective service
# 4000-4160 Food preparation and serving related occupations
# 4200-4250 Building and grounds cleaning and maintenance occupations
# 4300-4650 Personal care and service occupations
# 
# Blue-collar
# 6200-6940 Construction and extraction occupations
# 7000-7620 Installation, maintenance, and repair occupations
# 7700-8960 Production occupations
# 9000-9750 Transportation and material moving occupations
# 
# Excluded
# 6000-6130 Farming, fishing, and forestry occupations
# 9840 Armed Forces

white.collar <- c('110000', '130000', '150000', '170000', '190000', '210000', '230000', '250000', '270000', '290000', '410000', '430000')
blue.collar <- c('470000', '490000', '510000', '530000')
service <- c('310000', '330000', '350000', '370000', '390000')

# Get the Series ID's that we are interested in
file.path <- paste0(path,'/oe.series')
oe.series <- read.table(file.path, header = TRUE, sep = '\t', colClasses = rep('character',12)) %>%
  filter(datatype_code == '01') %>% # Only pull in the employment measure
  filter(areatype_code == 'M') %>% # Only pull in the MSA data
  filter(industry_code == '000000') # Only pull in industry totals


# Pull out the high tech and total jobs
white.collar <- oe.series %>%
  filter(occupation_code %in% white.collar) %>%
  select(series_id, area_code)
blue.collar <- oe.series %>%
  filter(occupation_code %in% blue.collar) %>%
  select(series_id, area_code)
service <- oe.series %>%
  filter(occupation_code %in% service) %>%
  select(series_id, area_code)
total <- oe.series %>%
  filter(occupation_code %in% '000000') %>%
  select(series_id, area_code)

# Free up some memory
rm(oe.series)

file.path <- paste0(path,'/oe.data.1.AllData')

# Import the data values
oe.data <- read.table(file.path, header = TRUE, sep = '\t', colClasses = c('character', 'integer', 'character', 'character', 'character'))

# Merge in the values
white.collar <- merge(oe.data, white.collar) %>%
  select(area_code, value, year) %>%
  mutate(value = as.numeric(value)) %>%
  group_by(area_code, year) %>%
  summarise(white.collar=sum(value))

blue.collar <- merge(oe.data, blue.collar) %>%
  select(area_code, value, year) %>%
  mutate(value = as.numeric(value)) %>%
  group_by(area_code, year) %>%
  summarise(blue.collar=sum(value))

service <- merge(oe.data, service) %>%
  select(area_code, value, year) %>%
  mutate(value = as.numeric(value)) %>%
  group_by(area_code, year) %>%
  summarise(service=sum(value))

total <- merge(oe.data, total) %>%
  select(area_code, value, year) %>%
  mutate(value = as.numeric(value)) %>%
  group_by(area_code, year) %>%
  summarise(total=sum(value))

# Free up some memory
rm(oe.data)

merge(white.collar, blue.collar) %>%
  merge(., service) %>%
  merge(., total) %>%
  write.xlsx(., file='Metro Occupations by Type.xlsx', sheetName='Occupations', row.names=FALSE)