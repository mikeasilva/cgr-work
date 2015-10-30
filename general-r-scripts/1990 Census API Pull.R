source('~/R/census.api.R')
'
Numerator (SF3)
P1170014  INC IN 89 BELOW POVERTY[24] 5 years
P1170015	INC IN 89 BELOW POVERTY[24] 6-11 years
P1170016	INC IN 89 BELOW POVERTY[24] 12-17 years

Denominator (SF1)
P0110004  Persons Age 5 yrs
P0110005	Persons Age 6 yrs
P0110006	Persons Age 7-9 yrs
P0110007	Persons Age 10-11 yrs
P0110008	Persons Age 12-13 yrs
P0110009	Persons Age 14 yrs
P0110010	Persons Age 15 yrs
P0110011	Persons Age 16 yrs
P0110012	Persons Age 17 yrs

Geographical Info (SF1)
PMSA  Primary Metropolitan Statistical Area
CMSA  Combined Metropolitan Statistical Area

Alt Denominator (SF3)
P1170002  INC IN 89 ABOVE POVERTY[24] 5 years
P1170003  INC IN 89 ABOVE POVERTY[24] 6-11 years
P1170004  INC IN 89 ABOVE POVERTY[24] 12-17 years
'
## Build the Request URLs
api.url <- 'http://api.census.gov/data/1990/'
sf1.url <- paste0(api.url, 'sf3?key=', api.key, '&for=county:*&get=CMSA,PMSA,P0110004,P0110005,P0110006,P0110007,P0110008,P0110009,P0110010,P0110011,P0110012')
sf3.url <- paste0(api.url, 'sf3?key=', api.key, '&for=county:*&get=P1170002,P1170003,P1170004,P1170014,P1170015,P1170016')

## Request the tables
library(rjson)
sf1 <- fromJSON(file=sf1.url, method='C')
sf3 <- fromJSON(file=sf3.url, method='C')

## Convert List to Data Frame
sf1.df <- data.frame(matrix(unlist(sf1), nrow=length(sf1), byrow=T))
sf3.df <- data.frame(matrix(unlist(sf3), nrow=length(sf3), byrow=T))

## Convert factors to characters
sf1.df <- data.frame(lapply(sf1.df, as.character), stringsAsFactors=FALSE)
sf3.df <- data.frame(lapply(sf3.df, as.character), stringsAsFactors=FALSE)

## Clean up the names
names(sf1.df) <- sf1.df[1,]
names(sf3.df) <- sf3.df[1,]

## Remove 1st Row (since it is the variable name)
sf1.df <- sf1.df[2:nrow(sf1.df),]
sf3.df <- sf3.df[2:nrow(sf3.df),]

## Combine the two data frames
census <- merge(sf1.df, sf3.df, by=c('state','county'))

## Change characters to numbers
col.to.convert <- names(census)[!names(census) %in% c('state','county','PMSA','CMSA')]
 for(ctc in col.to.convert){
  census[,ctc] <- as.numeric(census[,ctc])
}

## Aggregate data to MSA level
aggdata <- aggregate(. ~ CMSA + PMSA, data=census[,!names(census) %in% c('state','county')] , FUN=sum)

## Write CSV Files
write.csv(aggdata,'1990.csv')
write.csv(census,'1990-census.csv')