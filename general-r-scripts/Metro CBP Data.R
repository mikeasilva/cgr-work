## Metro CBP Data.R
#
# This script takes the county business patterns data and creates, aggregates
# them to the metro level and saves them as a RDS file for further processing.
#
# Since there is NAICS and SIC based data we rename the classification as
# "industry" and add in a bolean is.naics flag.

library(dplyr)

getYear <- function(filename){
  year <- as.numeric(substr(filename, 4,5))
  if(year < 14)
    return(2000 + year)
  else
    return(1900 + year)
}

# The directory where the CBP data is stored with trailing slash
base.path <- 'H:/Data Warehouse/Census Bureau/County Business Patterns/Complete County Files/'

# The county fips to metro map
metros <- read.csv('metrolist.csv')
names(metros) <- c('msa.fips','msa.name','county.fips','county.name')

files <- list.files(base.path, pattern=".zip")
for(file in files){
  path <- file.path(base.path,file)
  text.file <- paste0(gsub('.zip','.txt',file))
  if(!file.exists(text.file)){
    unzip(path)
  }
  
  metros.subset <- select(metros, county.fips, msa.fips)
  
  # To ensure we don't loose any information we will read in the data as characters
  cbp <- read.csv(text.file, nrows=1)
  classes <- rep('character',ncol(cbp))
  
  # Read in the raw data and change the variable type from text to numeric
  cbp <- read.csv(text.file, colClasses=classes) %>%
    mutate(county.fips=paste0(fipstate,fipscty)) %>%
    merge(metros.subset, .) %>%
    mutate(emp = as.numeric(emp)) %>%
    mutate(ap = as.numeric(ap)) %>%
    mutate(est = as.numeric(est)) %>%
    mutate(n1_4 = as.numeric(n1_4)) %>%
    mutate(n5_9 = as.numeric(n5_9)) %>%
    mutate(n10_19 = as.numeric(n10_19)) %>%
    mutate(n20_49 = as.numeric(n20_49)) %>%
    mutate(n50_99 = as.numeric(n50_99)) %>%
    mutate(n100_249 = as.numeric(n100_249)) %>%
    mutate(n250_499 = as.numeric(n250_499)) %>%
    mutate(n500_999 = as.numeric(n500_999)) %>%
    mutate(n1000 = as.numeric(n1000)) %>%
    mutate(n1000_1 = as.numeric(n1000_1)) %>%
    mutate(n1000_2 = as.numeric(n1000_2)) %>%
    mutate(n1000_3 = as.numeric(n1000_3)) %>%
    mutate(n1000_4 = as.numeric(n1000_4))
  
  # Futher processing broken out by industry classification system
  if('naics' %in% names(cbp)){
    # NAICS Based CBP data
    cbp <- cbp %>%
      select(msa.fips, naics, emp, ap, est, n1_4, n5_9, n10_19, n20_49, n50_99, n100_249, n250_499, n500_999, n1000, n1000_1, n1000_2, n1000_3, n1000_4) %>%
      rename(industry = naics) %>%
      group_by(msa.fips, industry) %>%
      summarise_each(funs(sum)) %>%
      mutate(is.naics = 1) %>%
      mutate(year = getYear(text.file))
  } else{
    # SIC Based CBP data
    cbp <- cbp %>%
      select(msa.fips, sic, emp, ap, est, n1_4, n5_9, n10_19, n20_49, n50_99, n100_249, n250_499, n500_999, n1000, n1000_1, n1000_2, n1000_3, n1000_4) %>%
      rename(industry = sic) %>%
      group_by(msa.fips, industry) %>%
      summarise_each(funs(sum)) %>%
      mutate(is.naics = 0) %>%
      mutate(year = getYear(text.file))
  }
  
  rds.file <- paste0(gsub('.zip','.rds',file))
  saveRDS(cbp, rds.file)
  unlink(text.file)
}