## This function will estimate the median age of the intercensal data
## Written by: Mike Silva <msilva@cgr.org>
library(dplyr)

## Download the data
download.file('http://www.census.gov/popest/data/intercensal/county/files/CO-EST00INT-AGESEX-5YR.csv', 'CO-EST00INT-AGESEX-5YR.csv')
## http://www.census.gov/popest/data/intercensal/county/files/CO-EST00INT-AGESEX-5YR.pdf

## Read in the CSV and only select the totals (don't break it out by sex)
csv <- read.csv('CO-EST00INT-AGESEX-5YR.csv', colClasses=c(rep('character',5),rep('numeric',15)), stringsAsFactors=FALSE) %.%
  filter(SEX ==0)

## This data frame contains the age groups
age.groups <- data.frame(
  AGEGRP = 0:18,
  label = c('Total', 'Age 0 to 4 years', 'Age 5 to 9 years', 'Age 10 to 14 years', 'Age 15 to 19 years', 'Age 20 to 24 years', 'Age 25 to 29 years', 'Age 30 to 34 years', 'Age 35 to 39 years', 'Age 40 to 44 years', 'Age 45 to 49 years', 'Age 50 to 54 years', 'Age 55 to 59 years', 'Age 60 to 64 years', 'Age 65 to 69 years', 'Age 70 to 74 years', 'Age 75 to 79 years', 'Age 80 to 84 years', 'Age 85 years and older'),
  lower.bound = c(NA, seq(0, 85, 5)),
  upper.bound = c(NA, seq(4, 89, 5))
)

## This function derives the median from the grouped data
get.median <- function(groups, counts, age.groups){
  ## Check for NAs - If there are NAs the function returns NA
  if(length(counts) == length(counts[!is.na(counts)])){
    total <- counts[1]
    i <- 1 ## initialized at 1 so it will skip the total line
    cum.sum <- 0
    ## Find the interval where the median lies
    repeat{
      i <- i + 1
      cum.sum <- cum.sum + counts[i]
      cum.freq <- cum.sum / total
      if(cum.freq >= 0.5){
        break
      }      
    }
    ## Find the bounds of the age group that contains the median
    age.group.lower.bound <- age.groups[i, 3]
    age.group.upper.bound <- age.groups[i, 4]
    age.group.interval <- age.group.upper.bound - age.group.lower.bound
    ## Find the counts surrounding the median
    count.upper.bound <- cum.sum
    count.lower.bound <- cum.sum-counts[i]+1
    count.interval <- counts[i]
    ## Figure out where the median lies
    median.in.interval <- ((total/2) - count.lower.bound) / count.interval
    the.median <- age.group.lower.bound + (age.group.interval * median.in.interval)
  } else{
    the.median <- NA
  }
  return(the.median)
}

## Use the above function to calculate the median age
median.df <- csv %.%
  group_by(STATE, COUNTY, STNAME, CTYNAME) %.%
  summarize(
    ESTIMATESBASE2000 = get.median(AGEGRP, ESTIMATESBASE2000, age.groups),
    POPESTIMATE2000 = get.median(AGEGRP, POPESTIMATE2000, age.groups),
    POPESTIMATE2001 = get.median(AGEGRP, POPESTIMATE2001, age.groups),
    POPESTIMATE2002 = get.median(AGEGRP, POPESTIMATE2002, age.groups),
    POPESTIMATE2003 = get.median(AGEGRP, POPESTIMATE2003, age.groups),
    POPESTIMATE2004 = get.median(AGEGRP, POPESTIMATE2004, age.groups),
    POPESTIMATE2005 = get.median(AGEGRP, POPESTIMATE2005, age.groups),
    POPESTIMATE2006 = get.median(AGEGRP, POPESTIMATE2006, age.groups),
    POPESTIMATE2007 = get.median(AGEGRP, POPESTIMATE2007, age.groups),
    POPESTIMATE2008 = get.median(AGEGRP, POPESTIMATE2008, age.groups),
    POPESTIMATE2009 = get.median(AGEGRP, POPESTIMATE2009, age.groups),
    POPESTIMATE2010 = get.median(AGEGRP, POPESTIMATE2010, age.groups)
  )

## Store the data
write.csv(median.df, 'Intercensal Median Age Estimates.csv')