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
      
      fips.codes[i] <- paste0(paste(rep('0',number.of.zeros), collapse=''),fips.code)
    }
  }
  return(fips.codes)
}

## This function is used to calculated MOE's on aggregated ACS data
aggregateMOE <- function(moe.vector){
  sqrt(sum((moe.vector)^2))
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
P0120004  Male: 5 to 9 years
P0120005	Male: 10 to 14 years
P0120006	Male: 15 to 17 years
P0120028  Female: 5 to 9 years
P0120029	Female: 10 to 14 years
P0120030	Female: 15 to 17 years
'
url <- paste0(api.url, '2010/sf1?key=', api.key, '&for=place:*&get=NAME,P0010001,P0120004,P0120005,P0120006,P0120028,P0120029,P0120030')
sf1.2010 <- CensusAPI(url, c('NAME','state','place')) %>% # Request the data
  filter(P0010001 >= size.filter) # Filter out places with pop < size.filter
## Create the 5 to 17 population total
cols <- c('P0120004','P0120005','P0120006','P0120028','P0120029','P0120030')
sf1.2010$people.5.to.17.2010 <- rowSums(sf1.2010[, cols])
## Drop raw data
raw <- names(sf1.2010) %in% cols 
sf1.2010 <- sf1.2010[!raw]

'
2000 Census SF-1
See http://api.census.gov/data/2000/sf1/variables.html
NAME  Area Name-Legal/Statistical Area Description (LSAD)
P012004  SEX BY AGE:Male:5 to 9 
P012005  SEX BY AGE:Male:10 to 14 
P012006	SEX BY AGE:Male:15 to 17
P012028  SEX BY AGE:Female:5 to 9 
P012029	SEX BY AGE:Female:10 to 14 
P012030	SEX BY AGE:Female:15 to 17
'
url <- paste0(api.url, '2000/sf1?key=', api.key, '&for=place:*&get=NAME,P012004,P012005,P012006,P012028,P012029,P012030')
sf1.2000 <- CensusAPI(url, c('NAME','state','place'))
## Clean the FIPS codes
sf1.2000$state <- fipsCleaner(sf1.2000$state, 2)
sf1.2000$place <- fipsCleaner(sf1.2000$place, 5)
## Create the 5 to 17 population total
cols <- c('P012004','P012005','P012006','P012028','P012029','P012030')
sf1.2000$people.5.to.17.2000 <- rowSums(sf1.2000[, cols])
## Drop raw data
raw <- names(sf1.2000) %in% cols 
sf1.2000 <- sf1.2000[!raw]

'
2000 Census SF-3
See http://api.census.gov/data/2000/sf3/variables.html 
P087004  Total: Income in 1999 below poverty level: 5 years
P087005	Total: Income in 1999 below poverty level: 6 to 11 years
P087006	Total: Income in 1999 below poverty level: 12 to 17 years
P087012  Total: Income in 1999 at or above poverty level: 5 years 
P087013	Total: Income in 1999 at or above poverty level: 6 to 11 years 
P087014	Total: Income in 1999 at or above poverty level: 12 to 17 years
'
url <- paste0(api.url, '2000/sf3?key=', api.key, '&for=place:*&get=P087004,P087005,P087006,P087012,P087013,P087014')
sf3.2000 <- CensusAPI(url, c('state','place'))
## Clean the FIPS codes
sf3.2000$state <- fipsCleaner(sf3.2000$state, 2)
sf3.2000$place <- fipsCleaner(sf3.2000$place, 5)
## Create the 5 to 17 population total
cols <- c('P087004','P087005','P087006')
sf3.2000$poverty.5.to.17.2000 <- rowSums(sf3.2000[, cols])
cols <- c('P087004','P087005','P087006','P087012','P087013','P087014')
sf3.2000$pov.status.5.to.7.2000 <- rowSums(sf3.2000[, cols])
## Drop raw data
raw <- names(sf3.2000) %in% cols 
sf3.2000 <- sf3.2000[!raw]

'
1990 SF-1
See http://api.census.gov/data/1990/sf1/variables.html
ANPSADPI  Area Name/PSAD Term/Part Indicator 14
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
url <- paste0(api.url, '1990/sf1?key=', api.key, '&for=place:*&get=ANPSADPI,P0110004,P0110005,P0110006,P0110007,P0110008,P0110009,P0110010,P0110011,P0110012')
sf1.1990 <- CensusAPI(url, c('ANPSADPI', 'state', 'place'))
## Clean  the FIPS codes
sf1.1990$state <- fipsCleaner(sf1.1990$state, 2)
sf1.1990$place <- fipsCleaner(sf1.1990$place, 5)
## Create the 5 to 17 population total
cols <- c('P0110004','P0110005','P0110006','P0110007','P0110008','P0110009','P0110010','P0110011','P0110012')
sf1.1990$people.5.to.7.1990 <- rowSums(sf1.1990[, cols])
## Drop raw data
raw <- names(sf1.1990) %in% cols 
sf1.1990 <- sf1.1990[!raw]

'
1990 SF-3
See http://api.census.gov/data/1990/sf3/variables.html
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
## Clean the FIPS codes
sf3.1990$state <- fipsCleaner(sf3.1990$state, 2)
sf3.1990$place <- fipsCleaner(sf3.1990$place, 5)
## Create the 5 to 17 population total
cols <- c('P1170014','P1170015','P1170016')
sf3.1990$poverty.5.to.7.1990 <- rowSums(sf3.1990[, cols])
cols <- c('P1170002','P1170003','P1170004','P1170014','P1170015','P1170016')
sf3.1990$pov.status.5.to.7.1990 <- rowSums(sf3.1990[, cols])
## Drop raw data
raw <- names(sf3.1990) %in% cols 
sf3.1990 <- sf3.1990[!raw]


'
2013 ACS 1 Year Estimates
http://api.census.gov/data/2013/acs1/variables.html
B01001_004E  Male:!!5 to 9 years
B01001_004M	Margin of Error for!!Male:!!5 to 9 years
B01001_005E	Male:!!10 to 14 years
B01001_005M	Margin of Error for!!Male:!!10 to 14 years
B01001_006E	Male:!!15 to 17 years
B01001_006M	Margin of Error for!!Male:!!15 to 17 years
B01001_028E  Female:!!5 to 9 years
B01001_028M	Margin of Error for!!Female:!!5 to 9 years
B01001_029E	Female:!!10 to 14 years
B01001_029M	Margin of Error for!!Female:!!10 to 14 years
B01001_030E	Female:!!15 to 17 years
B01001_030M	Margin of Error for!!Female:!!15 to 17 years

B17001_005E  Income in the past 12 months below poverty level:!!Male:!!5 years
B17001_005M	Margin of Error for!!Income in the past 12 months below poverty level:!!Male:!!5 years
B17001_006E	Income in the past 12 months below poverty level:!!Male:!!6 to 11 years
B17001_006M	Margin of Error for!!Income in the past 12 months below poverty level:!!Male:!!6 to 11 years
B17001_007E	Income in the past 12 months below poverty level:!!Male:!!12 to 14 years
B17001_007M	Margin of Error for!!Income in the past 12 months below poverty level:!!Male:!!12 to 14 years
B17001_008E	Income in the past 12 months below poverty level:!!Male:!!15 years
B17001_008M	Margin of Error for!!Income in the past 12 months below poverty level:!!Male:!!15 years
B17001_009E	Income in the past 12 months below poverty level:!!Male:!!16 and 17 years
B17001_009M	Margin of Error for!!Income in the past 12 months below poverty level:!!Male:!!16 and 17 years
B17001_019E  Income in the past 12 months below poverty level:!!Female:!!5 years
B17001_019M	Margin of Error for!!Income in the past 12 months below poverty level:!!Female:!!5 years
B17001_020E	Income in the past 12 months below poverty level:!!Female:!!6 to 11 years
B17001_020M	Margin of Error for!!Income in the past 12 months below poverty level:!!Female:!!6 to 11 years
B17001_021E	Income in the past 12 months below poverty level:!!Female:!!12 to 14 years
B17001_021M	Margin of Error for!!Income in the past 12 months below poverty level:!!Female:!!12 to 14 years
B17001_022E	Income in the past 12 months below poverty level:!!Female:!!15 years
B17001_022M	Margin of Error for!!Income in the past 12 months below poverty level:!!Female:!!15 years
B17001_023E	Income in the past 12 months below poverty level:!!Female:!!16 and 17 years
B17001_023M Margin of Error for!!Income in the past 12 months below poverty level:!!Female:!!16 and 17 years

B17001_034E  Income in the past 12 months at or above poverty level:!!Male:!!5 years
B17001_034M	Margin of Error for!!Income in the past 12 months at or above poverty level:!!Male:!!5 years
B17001_035E	Income in the past 12 months at or above poverty level:!!Male:!!6 to 11 years
B17001_035M	Margin of Error for!!Income in the past 12 months at or above poverty level:!!Male:!!6 to 11 years
B17001_036E	Income in the past 12 months at or above poverty level:!!Male:!!12 to 14 years
B17001_036M	Margin of Error for!!Income in the past 12 months at or above poverty level:!!Male:!!12 to 14 years
B17001_037E	Income in the past 12 months at or above poverty level:!!Male:!!15 years
B17001_037M	Margin of Error for!!Income in the past 12 months at or above poverty level:!!Male:!!15 years
B17001_038E	Income in the past 12 months at or above poverty level:!!Male:!!16 and 17 years
B17001_038M	Margin of Error for!!Income in the past 12 months at or above poverty level:!!Male:!!16 and 17 years

B17001_048E  Income in the past 12 months at or above poverty level:!!Female:!!5 years
B17001_048M	Margin of Error for!!Income in the past 12 months at or above poverty level:!!Female:!!5 years
B17001_049E	Income in the past 12 months at or above poverty level:!!Female:!!6 to 11 years
B17001_049M	Margin of Error for!!Income in the past 12 months at or above poverty level:!!Female:!!6 to 11 years
B17001_050E	Income in the past 12 months at or above poverty level:!!Female:!!12 to 14 years
B17001_050M	Margin of Error for!!Income in the past 12 months at or above poverty level:!!Female:!!12 to 14 years
B17001_051E	Income in the past 12 months at or above poverty level:!!Female:!!15 years
B17001_051M	Margin of Error for!!Income in the past 12 months at or above poverty level:!!Female:!!15 years
B17001_052E	Income in the past 12 months at or above poverty level:!!Female:!!16 and 17 years
B17001_052M	Margin of Error for!!Income in the past 12 months at or above poverty level:!!Female:!!16 and 17 years
'
url <- paste0(api.url, '2013/acs1?key=', api.key, '&for=place:*&get=NAME,B01001_004E,B01001_004M,B01001_005E,B01001_005M,B01001_006E,B01001_006M,B01001_028E,B01001_028M,B01001_029E,B01001_029M,B01001_030E,B01001_030M,B17001_005E,B17001_005M,B17001_006E,B17001_006M,B17001_007E,B17001_007M,B17001_008E,B17001_008M,B17001_009E,B17001_009M,B17001_019E,B17001_019M,B17001_020E,B17001_020M,B17001_021E,B17001_021M,B17001_022E,B17001_022M,B17001_023E,B17001_023M')
acs.2013 <- CensusAPI(url, c('NAME','state', 'place'))
url <- paste0(api.url, '2013/acs1?key=', api.key, '&for=place:*&get=NAME,B17001_034E,B17001_034M,B17001_035E,B17001_035M,B17001_036E,B17001_036M,B17001_037E,B17001_037M,B17001_038E,B17001_038M,B17001_048E,B17001_048M,B17001_049E,B17001_049M,B17001_050E,B17001_050M,B17001_051E,B17001_051M,B17001_052E,B17001_052M')
acs.2013 <- merge(acs.2013, CensusAPI(url, c('NAME','state', 'place')))
## Create the 5 to 17 population total
cols <- c('B01001_004E','B01001_005E','B01001_006E','B01001_028E','B01001_029E','B01001_030E')
acs.2013$people.5.to.7.2013 <- rowSums(acs.2013[, cols])
cols <- c('B01001_004M','B01001_005M','B01001_006M','B01001_028M','B01001_029M','B01001_030M')
acs.2013$people.5.to.7.2013.moe <- apply(acs.2013[, cols], 1, aggregateMOE)

cols <- c('B17001_005E','B17001_006E','B17001_007E','B17001_008E','B17001_009E','B17001_019E','B17001_020E','B17001_021E','B17001_022E','B17001_023E')
acs.2013$poverty.5.to.7.2013 <- rowSums(acs.2013[, cols])
cols <- c('B17001_005M','B17001_006M','B17001_007M','B17001_008M','B17001_009M','B17001_019M','B17001_020M','B17001_021M','B17001_022M','B17001_023M')
acs.2013$poverty.5.to.7.2013.moe <- apply(acs.2013[, cols], 1, aggregateMOE)

cols <- c('B17001_005E','B17001_006E','B17001_007E','B17001_008E','B17001_009E','B17001_019E','B17001_020E','B17001_021E','B17001_022E','B17001_023E','B17001_034E','B17001_035E','B17001_036E','B17001_037E','B17001_038E','B17001_048E','B17001_049E','B17001_050E','B17001_051E','B17001_052E')
acs.2013$pov.status.5.to.7.2013 <- rowSums(acs.2013[, cols])
cols <- c('B17001_005M','B17001_006M','B17001_007M','B17001_008M','B17001_009M','B17001_019M','B17001_020M','B17001_021M','B17001_022M','B17001_023M','B17001_034M','B17001_035M','B17001_036M','B17001_037M','B17001_038M','B17001_048M','B17001_049M','B17001_050M','B17001_051M','B17001_052M')
acs.2013$pov.status.5.to.7.2013.moe <- apply(acs.2013[, cols], 1, aggregateMOE)

## Rename the NAME variable
names(acs.2013)[1] <- c('name.2013')

## Drop raw data
cols <- c('B01001_004E','B01001_005E','B01001_006E','B01001_028E','B01001_029E','B01001_030E')
cols <- c(cols, 'B01001_004M','B01001_005M','B01001_006M','B01001_028M','B01001_029M','B01001_030M')
cols <- c(cols, 'B17001_005E','B17001_006E','B17001_007E','B17001_008E','B17001_009E','B17001_019E','B17001_020E','B17001_021E','B17001_022E','B17001_023E')
cols <- c(cols, 'B17001_005M','B17001_006M','B17001_007M','B17001_008M','B17001_009M','B17001_019M','B17001_020M','B17001_021M','B17001_022M','B17001_023M')
cols <- c(cols, 'B17001_005E','B17001_006E','B17001_007E','B17001_008E','B17001_009E','B17001_019E','B17001_020E','B17001_021E','B17001_022E','B17001_023E','B17001_034E','B17001_035E','B17001_036E','B17001_037E','B17001_038E','B17001_048E','B17001_049E','B17001_050E','B17001_051E','B17001_052E')
cols <- c(cols, 'B17001_005M','B17001_006M','B17001_007M','B17001_008M','B17001_009M','B17001_019M','B17001_020M','B17001_021M','B17001_022M','B17001_023M','B17001_034M','B17001_035M','B17001_036M','B17001_037M','B17001_038M','B17001_048M','B17001_049M','B17001_050M','B17001_051M','B17001_052M')

raw <- names(acs.2013) %in% cols 
acs.2013 <- acs.2013[!raw]

## Merge the data together
census.1990 <- merge(sf1.1990, sf3.1990)
census.2000 <- merge(sf1.2000, sf3.2000)
census <- merge(census.2000, census.1990)
census <- merge(acs.2013, census)
census <- merge(sf1.2010, census)

## Write the file to csv
write.csv(census,'~/5-to-7-poverty.csv')