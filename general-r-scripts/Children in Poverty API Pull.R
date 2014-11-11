library(dplyr)
library(rjson)

## This function takes an API url and returns a data frame containing the data
CensusAPI <- function(url, char.col=NA){
  ## Request the data
  data <- fromJSON(file=url, method='C')
  ## Convert List to Data Frame
  data <- data.frame(matrix(unlist(data), nrow=length(data), byrow=T))
  ## Convert factors to characters
  data <- data.frame(lapply(data, as.character), stringsAsFactors=FALSE)
  ## Clean up the names
  names(data) <- data[1,]
  ## Remove 1st Row (since it is the variable name)
  data <- data[2:nrow(data),]
  if(length(char.col)>1 || !is.na(char.col)){
    ## Change characters to numbers
    col.to.convert <- names(data)[!names(data) %in% char.col]
    for(ctc in col.to.convert){
      data[,ctc] <- as.numeric(data[,ctc])
    }
  }
  ## Return the data frame
  return(data)
}

## Some of the state fips codes are missing the leading zero.  This fixes that
fipsCleaner <- function(fips.codes, size){
  i <- 0
  for(fips.code in fips.codes){
    i <- i + 1
    if(nchar(fips.code) < size){
      number.of.zeros <- size - nchar(fips.code)
      
      fips.codes[i] <- paste0(paste(rep('0',number.of.zeros), collapse=''),code)
    }
  }
  return(fips.codes)
}

## Size filter
size.filter <- 100000

## Census API Base URL
api.url <- 'http://api.census.gov/data/'

## Load my Census API key (api.key)
source('~/census.api.R')

'
2010 Census SF-1
P0010001  Total Population
NAME  GEO PLACE HOLDER

P12. Sex By Age
P0120004  Male: 5 to 9 years
P0120005	Male: 10 to 14 years
P0120006	Male: 15 to 17 years
P0120028  Female: 5 to 9 years
P0120029	Female: 10 to 14 years
P0120030	Female: 15 to 17 years
'
url <- paste0(api.url, '2010/sf1?key=', api.key, '&for=place:*&get=NAME,P0010001,P0120004,P0120005,P0120006,P0120028,P0120029,P0120030')
sf1.2010 <- CensusAPI(url, c('NAME','state','place')) %>% # Request the data
  filter(P0010001 >= size.filter) %>% # Filter out places with pop < size.filter
  order_by(P0010001) # Sort by pop

## Create the 5 to 17 population total
cols <- c('P0120004','P0120005','P0120006','P0120028','P0120029','P0120030')
sf1.2010$people.5.to.17 <- rowSums(sf1.2010[, cols])

'
2000 Census SF-1
See http://api.census.gov/data/2000/sf1/variables.html

P001001  Total Population
NAME  Area Name-Legal/Statistical Area Description (LSAD)

P12. Sex By Age
P012004  SEX BY AGE:Male:5 to 9 
P012005  SEX BY AGE:Male:10 to 14 
P012006	SEX BY AGE:Male:15 to 17
P012028  SEX BY AGE:Female:5 to 9 
P012029	SEX BY AGE:Female:10 to 14 
P012030	SEX BY AGE:Female:15 to 17
'
url <- paste0(api.url, '2000/sf1?key=', api.key, '&for=place:*&get=NAME,P001001,P012004,P012005,P012006,P012028,P012029,P012030')
sf1.2000 <- CensusAPI(url, c('NAME','state','place'))
## Create the 5 to 17 population total
cols <- c('P012004','P012005','P012006','P012028','P012029','P012030')
sf1.2000$people.5.to.17 <- rowSums(sf1.2000[, cols])

sf1.2000$state <- fipsCleaner(sf1.2000$state, 2)
sf1.2000$place <- fipsCleaner(sf1.2000$place, 5)

'
2000 Census SF-3
See http://api.census.gov/data/2000/sf3/variables.html

NAME  Area Name-Legal/Statistical Area Description (LSAD)

P87. Poverty Status in 1999 by Age 
P087004  Total: Income in 1999 below poverty level: 5 years
P087005	Total: Income in 1999 below poverty level: 6 to 11 years
P087006	Total: Income in 1999 below poverty level: 12 to 17 years
P087012  Total: Income in 1999 at or above poverty level: 5 years 
P087013	Total: Income in 1999 at or above poverty level: 6 to 11 years 
P087014	Total: Income in 1999 at or above poverty level: 12 to 17 years
'
url <- paste0(api.url, '2000/sf3?key=', api.key, '&for=place:*&get=NAME,P087004,P087005,P087006,P087012,P087013,P087014')
sf3.2000 <- CensusAPI(url, c('NAME','state','place'))

'
1990 SF-1
See http://api.census.gov/data/1990/sf1/variables.html
LOGRECPN  Logical Record Part Number
ANPSADPI  Area Name/PSAD Term/Part Indicator 14
P0010001  Total Persons
P0110004  Persons Age 5 yrs 
P0110005	Persons Age 6 yrs 
P0110006	Persons Age 7-9 yrs 
P0110007	Persons Age 10-11 yrs 
P0110008	Persons Age 12-13 yrs 
P0110009	Persons Age 14 yrs 
P0110010	Persons Age 15 yrs 
P0110011	Persons Age 16 yrs 
P0110012	Persons Age 17 yrs
'
url <- paste0(api.url, '1990/sf1?key=', api.key, '&for=place:*&get=LOGRECPN,ANPSADPI,P0010001,P0110004,P0110005,P0110006,P0110007,P0110008,P0110009,P0110010,P0110011,P0110012')
sf1.1990 <- CensusAPI(url, c('LOGRECPN','ANPSADPI', 'state', 'place'))

'
1990 SF-3
See http://api.census.gov/data/1990/sf3/variables.html
LOGRECPN  Logical Record Part Number
ANPSADPI  Area Name/PSAD Term/Part Indicator 14
P1170002  INC IN 89 ABOVE POVERTY[24] 5 years
P1170003	INC IN 89 ABOVE POVERTY[24] 6-11 years
P1170004	INC IN 89 ABOVE POVERTY[24] 12-17 years
P1170014  INC IN 89 BELOW POVERTY[24] 5 years
P1170015	INC IN 89 BELOW POVERTY[24] 6-11 years
P1170016	INC IN 89 BELOW POVERTY[24] 12-17 years
'
url <- paste0(api.url, '1990/sf3?key=', api.key, '&for=place:*&get=ANPSADPI,P1170002,P1170003,P1170004,P1170014,P1170015,P1170016')
sf3.1990 <- CensusAPI(url, c('LOGRECPN','ANPSADPI', 'state', 'place'))

