library(rjson)
library(dplyr)

source('~/census.api.R')

'
1990 Data

Rate (SF3)
P114A001  INC 89[1] Per capita Income In 1989
P115A001  PER CAPITA INC[5] White	Population
P115A002	PER CAPITA INC[5] Black	Population
P115A003	PER CAPITA INC[5] Am Ind-Eskimo-Aleut
P115A004	PER CAPITA INC[5] Asian-Pacfic Islander
P115A005	PER CAPITA INC[5] Other race

Numerator (SF3)
P1160001  AGGR INC 89[1] Total
P1150001  AGGR INC 89[5] White	Population
P1150002	AGGR INC 89[5] Black	Population
P1150003	AGGR INC 89[5] Am Indian-Eskimo-Aleut
P1150004	AGGR INC 89[5] Asian or Pacific Islander
P1150005	AGGR INC 89[5] Other race

Denominator (SF3)
P0010001  PERSONS[1] Total
P0080001  RACE[5] White
P0080002	RACE[5] Black
P0080003	RACE[5] American Indian, Eskimo, or Aleu
P0080004	RACE[5] Asian or Pacific Islander
P0080005	RACE[5] Other race
'

## Build the Request URLs
api.url <- paste0('http://api.census.gov/data/1990/sf3?key=', api.key, '&for=county:*&get=P114A001,P115A001,P115A002,P115A003,P115A004,P115A005,P1160001,P1150001,P1150002,P1150003,P1150004,P1150005,P0010001,P0080001,P0080002,P0080003,P0080004,P0080005')

## Request the tables
sf3 <- fromJSON(file=api.url, method='C')

## Convert List to Data Frame
sf3.df <- data.frame(matrix(unlist(sf3), nrow=length(sf3), byrow=T))

## Convert factors to characters
sf3.df <- data.frame(lapply(sf3.df, as.character), stringsAsFactors=FALSE)

## Clean up the names
names(sf3.df) <- sf3.df[1,]

## Remove 1st Row (since it is the variable name)
sf3.df <- sf3.df[2:nrow(sf3.df),]

## Change characters to numbers
col.to.convert <- names(sf3.df)[!names(sf3.df) %in% c('state','county')]

for(ctc in col.to.convert){
  sf3.df[,ctc] <- as.numeric(sf3.df[,ctc])
}

## Rename the columns
names(sf3.df) <- c('pci.total','pci.white','pci.black','pci.ai','pci.a','pci.o',
                   'ai.total','ai.white','ai.black','ai.ai','ai.a','ai.o',
                   'pop.total','pop.white','pop.black','pop.ai','pop.a','pop.o',
               'state','county')

## Add leading zero to state
sf3.df$state <- ifelse(as.numeric(sf3.df$state) < 10, paste0('0',sf3.df$state), sf3.df$state)

## Bluid county.fips to join on
sf3.df$county.fips <- paste0(sf3.df$state,sf3.df$county)

## Select the list of metro names for later
metro.names <- read.csv('~/metrolist.csv') %>%
  select(msa.fips,metro.name) %>%
  unique(.)

## Let's aggregate this county level data to the metro level
metro.1990 <- read.csv('~/metrolist.csv') %>%
  select(msa.fips,county.fips) %>%
  merge(sf3.df, .) %>%
  select(-county,-state,-county.fips) %>%
  group_by(msa.fips) %>%
  summarise_each(funs(sum)) %>%
  mutate(ai.total = ai.white + ai.black + ai.ai + ai.a + ai.o) %>%
  mutate(pci.total = ai.total/pop.total) %>%
  mutate(pci.white = ai.white/pop.white) %>%
  mutate(pci.black = ai.black/pop.black) %>%
  mutate(pci.ai = ai.ai/pop.ai) %>%
  mutate(pci.a = ai.a/pop.a) %>%
  merge(., metro.names)

## Write CSV Files
write.csv(metro.1990,'~/1990-metro.csv', row.names=FALSE)
write.csv(sf3.df,'~/1990-county.csv', row.names=FALSE)