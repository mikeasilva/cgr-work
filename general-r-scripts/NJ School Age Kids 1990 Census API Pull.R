source('~/R/census.api.R')
## Build the Request URLs
# P0010001  Total Population
# P0110004	Persons Age 5 yrs
# P0110005	Persons Age 6 yrs
# P0110006	Persons Age 7-9 yrs
# P0110007	Persons Age 10-11
# P0110008	Persons Age 12-13
# P0110009	Persons Age 14 yrs
# P0110010	Persons Age 15 yrs
# P0110011	Persons Age 16 yrs
# P0110012	Persons Age 17 yrs
# P0110013	Persons Age 18 yrs
# P0110014	Persons Age 19 yrs

api.url <- 'http://api.census.gov/data/1990/'
sf3.url <- paste0(api.url, 'sf3?key=', api.key, '&for=county+subdivision:*&in=state:34+county:025&get=P0010001,P0110004,P0110005,P0110006,P0110007,P0110008,P0110009,P0110010,P0110011,P0110012,P0110013,P0110014')
library(rjson)
## Request the tables
sf3 <- fromJSON(file=sf3.url, method='C')

## Convert List to Data Frame
sf3.df <- data.frame(matrix(unlist(sf3), nrow=length(sf3), byrow=T))

## Convert factors to characters
sf3.df <- data.frame(lapply(sf3.df, as.character), stringsAsFactors=FALSE)

## Clean up the names
names(sf3.df) <- sf3.df[1,]

## Remove 1st Row (since it is the variable name)
sf3.df <- sf3.df[2:nrow(sf3.df),]
write.csv(sf3.df,'nj.csv', row.names = FALSE)