## This Script Pulls the Metro Populations Using the BEA's API
library(dplyr)
library(xlsx)

## The following file assigns my BEA API key to the variable 'api.key'
source('~/bea.api.key.R')

## This file has the beaAPI and cleanData function
source('~/BEA API Functions.R')


metrolist <- read.csv('metrolist.csv')
names(metrolist)[1] <- 'msa.fips'

geo.fips.vector <- metrolist[1] %>%
  unique(.)

## Download & clean the data
data <- beaAPI(api.key, 'POP_MI', geo.fips.vector) %>%
  as.data.frame(.) %>%
  cleanData(., 'population')

write.xlsx(data, file='Metro Population.xlsx', sheetName='population', row.names=FALSE)
