library(plyr)
library(dplyr)
library(rjson)
library(reshape2)
library(xlsx)

data <- read.csv('Local Arts Index.csv')
rows.to.keep <- 10:15
cols.to.keep <- 2:6
data <- data[data$row %in% rows.to.keep, cols.to.keep]

## Relabel the measure (All data is 2013 figures)
measure <- c('10' = 'Entertainment admission fees per capita',
            '11' = 'Recorded media per capita',
            '12' = 'Musical instruments per capita',
            '13' = 'Photographic equipment and supplies per capita',
            '14' = 'Reading materials per capita',
            '15' = 'Total per capita')

data$measure <- revalue(as.factor(data$row), measure)

## Convert Percapita to number
names(data)[1] <- 'value'
data$value <- as.numeric(sub('\\$','',as.character(data$value)))

## Convert from long to wide
m.df <- melt(data[,c('value','fips','measure')], id=c('fips', 'measure'))
m.df$variable <- data$measure 
data <- dcast(m.df, fips ~ variable)

## Get Population Estimates
source('~/census.api.R')

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

url <- paste0('http://api.census.gov/data/2013/pep/cty?get=POP,DATE&for=county:*&key=',api.key)

## Select 2013 (DATE == 6)
pop2013 <- CensusAPI(url, c('state', 'county')) %>% filter(DATE == 6)

## correct FIPS Code
pop2013$fips.txt <- paste0(pop2013$state, pop2013$county)

## Mergeable FIPS Code
pop2013$fips <- as.numeric(pop2013$fips.txt)
pop2013 <- pop2013[,c('fips','fips.txt','POP')]

## Merge the Population with the per capita
data <- merge(data, pop2013)

## Clean Up names
names(data)[ncol(data)] <- 'Population'
data$fips<-data$fips.txt
names(data)[1] <- 'FIPS Code'

data <- data[!names(data) %in% c('fips.txt')]

## Add in the Year

data$Year <- 2013

## Write an XLSX

file.path <- paste0('H:/Data Warehouse/Americans for the Arts/Arts Spending-2013.xlsx')
write.xlsx(data, file.path)
