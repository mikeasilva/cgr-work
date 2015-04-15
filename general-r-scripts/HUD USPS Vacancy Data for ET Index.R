library(foreign)
library(dplyr)

housing <- function(df){
  df %>%
    select(AMS_RES, RES_VAC, NOSTAT_RES) %>%
    summarise(AMS_RES = sum(AMS_RES), RES_VAC=sum(RES_VAC), NOSTAT_RES=sum(NOSTAT_RES)) %>%
    mutate(vacant=RES_VAC + NOSTAT_RES) %>%
    mutate(denominator=AMS_RES) %>%
    select(vacant, denominator)
}

path <- 'H:/Data Warehouse/US Department of Housing and Urban Development (HUD)/USPS Vacancy Data/2010 Census Tracts/Q1'

## Get the list of files in the working directory
initial.files <- list.files(getwd())

## Get the list of zip files
zip.files <- list.files(path)

## Create data frame to hold results
hud.data <- data.frame(fips=numeric(), vacant=numeric(), denominator=numeric(), year=numeric(), stringsAsFactors=FALSE)

## Step through zip files list
for(zip.file in zip.files){
  ## Get the year
  year <- as.numeric(substr(zip.file,12,15))
  ## Display the progress
  message('Processing the ',year,' data ...')
  
  zip.file.path <- paste0(path,'/',zip.file)
  ## Unzip the file
  unzip(zip.file.path)
  ## Find out what was zipped
  current.files <- list.files(getwd())
  dbf.file <- current.files[!current.files %in% initial.files]
  ## Open the dbf file
  dbf <- read.dbf(dbf.file)
  ## Delete the dbf file
  unlink(dbf.file)
  
  ## Add om FIPS Codes
  dbf$STATE.FIPS <- substr(dbf$GEOID,0,2)
  dbf$COUNTY.FIPS <- substr(dbf$GEOID,0,5)

  ## Append the U.S.
  hud.data <- rbind(hud.data, c(fips=0, housing(dbf), year=year))
  
  ## Append TN
  temp <- dbf %>%
    filter(STATE.FIPS=='47') %>%
    housing(.)
  hud.data <- rbind(hud.data, c(fips=47, temp, year=year))
  
  ## Append Anderson, TN
  temp <- dbf %>%
    filter(COUNTY.FIPS=='47001') %>%
    housing(.)
  hud.data <- rbind(hud.data, c(fips=47001, temp, year=year))
  
  ## Append Blount, TN
  temp <- dbf %>%
    filter(COUNTY.FIPS=='47009') %>%
    housing(.)
  hud.data <- rbind(hud.data, c(fips=47009, temp, year=year))
  
  ## Append Jefferson, TN
  temp <- dbf %>%
    filter(COUNTY.FIPS=='47089') %>%
    housing(.)
  hud.data <- rbind(hud.data, c(fips=47089, temp, year=year))
  
  ## Append Knox, TN
  temp <- dbf %>%
    filter(COUNTY.FIPS=='47093') %>%
    housing(.)
  hud.data <- rbind(hud.data, c(fips=47093, temp, year=year))
  
  ## Append Loudon, TN
  temp <- dbf %>%
    filter(COUNTY.FIPS=='47105') %>%
    housing(.)
  hud.data <- rbind(hud.data, c(fips=47105, temp, year=year))
  
  ## Append Monroe, TN
  temp <- dbf %>%
    filter(COUNTY.FIPS=='47123') %>%
    housing(.)
  hud.data <- rbind(hud.data, c(fips=47123, temp, year=year))

  ## Append Roane, TN
  temp <- dbf %>%
    filter(COUNTY.FIPS=='47145') %>%
    housing(.)
  hud.data <- rbind(hud.data, c(fips=47145, temp, year=year))
  
  ## Append Sevier, TN
  temp <- dbf %>%
    filter(COUNTY.FIPS=='47155') %>%
    housing(.)
  hud.data <- rbind(hud.data, c(fips=47155, temp, year=year))
  
  ## Append Union, TN
  temp <- dbf %>%
    filter(COUNTY.FIPS=='47173') %>%
    housing(.)
  hud.data <- rbind(hud.data, c(fips=47173, temp, year=year))
  message('... Done')
}
## Save the data
write.csv(hud.data,'HUD Vacancy Data.csv', row.names=FALSE)
