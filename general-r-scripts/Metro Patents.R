## Metro Utility Patents by Year
## This script scrapes the PTO's website for their utility patents by year and
## aggregates the county level data to the creates and excel file 

library(rvest)
library(dplyr)
library(tidyr)
library(xlsx)

metros <- read.csv('metrolist.csv') %>%
  select(county.fips, metro.name) %>%
  rename(FIPS.Code = county.fips)

## Scrape the web for utility patent grant figures
pto <- html('http://www.uspto.gov/web/offices/ac/ido/oeip/taf/countyall/usa_county_gd.htm') %>%
  html_nodes('table') %>%
  html_table() %>%
  as.data.frame(.) %>%
  select(-Total) %>%
  merge(metros, .) %>%
  select(-FIPS.Code, -Mail.Code, -State.or.Territory, -Regional.Area.Component) %>%
  aggregate(. ~ metro.name, data=., sum) %>%
  gather(metro.name)

names(pto)[2] <- 'year'
pto$year <- as.numeric(substr(pto$year,2,5))

metros <- read.csv('metrolist.csv') %>%
  select(-county.fips, -county.name) %>%
  filter(metro.name %in% unique(pto$metro.name)) %>%
  unique(.)

names(metros)[1] <- 'msa.fips'
pto <- merge(pto, metros)

write.xlsx(pto, file='Metro Utility Patents.xlsx', sheetName='Sheet1', row.names=FALSE)

