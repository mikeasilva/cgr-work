## This R Script imprts the SAHIE csv files and aggregates them by year.

library(dplyr)
## The name of the CSV files
files <- c('sahie2008.csv', 'sahie2009.csv', 'sahie2010.csv', 'sahie_2011.csv', 'sahie2012.csv', 'sahie2013.csv')

## Step through each file
for(file.name in files){
  ## Show the Progress
  message(paste('Parsing',file.name))
  ## Read the csv
  csv <- read.csv(file.name, skip=3, na.strings='N/A', stringsAsFactors=FALSE, colClasses=rep('character',18))
  
  if(!exists('sahie.data')){
    ## SAHIE data does not exist in the R environment so create it
    sahie.data <- csv
  } else{
    ## SAHIE data exists in the R environment so append the csv data to it
    sahie.data <- rbind_list(sahie.data, csv)
  }
}
## Cleanup
rm(csv)

## Change variable types & remove the equal sign from the stcou variable
sahie.data <- sahie.data %>%
  mutate(year = as.numeric(year)) %>%
  mutate(nipr = as.numeric(nipr)) %>%
  mutate(nipr_moe = as.numeric(nipr_moe)) %>%
  mutate(nui = as.numeric(nui)) %>%
  mutate(nui_moe = as.numeric(nui_moe)) %>%
  mutate(nic = as.numeric(nic)) %>%
  mutate(nic_moe = as.numeric(nic_moe)) %>%
  mutate(pctui = as.numeric(pctui)) %>%
  mutate(pctui_moe = as.numeric(pctui_moe)) %>%
  mutate(pctic = as.numeric(pctic)) %>%
  mutate(pctic_moe = as.numeric(pctic_moe)) %>%
  mutate(stcou = gsub('=','', stcou))

## Remove the trailing whitespace from the name variable
trim.trailing <- function (x) sub("\\s+$", "", x)
sahie.data$name <- trim.trailing(sahie.data$name)

write.csv(sahie.data, 'Census_SAHIE_Data.csv', row.names=FALSE)

## Create data set for Delaware Indicators

de.geos <- data.frame(
  stcou = c('10000','44000', '10001', '10003', '10005', '12003', '12019', '12031', '12089', '12109', '51007', '51033', '51036', '51041', '51049', '51053', '51075', '51085', '51087', '51097', '51101', '51109', '51127', '51145', '51149', '51183', '51570', '51670', '51730', '51760'),
  cgr_name = c('Delaware','Rhode Island','Kent County, DE', 'New Castle County, DE', 'Sussex County, DE', 'CGR Jacksonville, FL MSA', 'CGR Jacksonville, FL MSA', 'CGR Jacksonville, FL MSA', 'CGR Jacksonville, FL MSA', 'CGR Jacksonville, FL MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA', 'CGR Richmond, VA MSA')
)

us.sahie.data <- sahie.data %>%
  filter(agecat == 0) %>%
  filter(racecat == 0) %>%
  filter(sexcat == 0) %>%
  filter(iprcat == 0) %>%
  filter(geocat == 40) %>%
  mutate(cgr_name = 'United States') %>%
  select(name, cgr_name, year, nui, nic) %>%
  mutate(rate = nui/nic)

de.sahie.data <- sahie.data %>%
  filter(agecat == 0) %>%
  filter(racecat == 0) %>%
  filter(sexcat == 0) %>%
  filter(iprcat == 0) %>%
  merge(., de.geos) %>%
  select(name, cgr_name, year, nui, nic) %>%
  mutate(rate = nui/nic) %>%
  rbind(., us.sahie.data)

write.csv(de.sahie.data, 'DE_Census_SAHIE_Data.csv', row.names=FALSE)
