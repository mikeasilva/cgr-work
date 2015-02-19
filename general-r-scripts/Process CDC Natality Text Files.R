## Process Text Files.R
## This script processes the CDC's prenatale care text files for 
## incorporation into CGR's Data Warehouse.

library(tidyr)
library(dplyr)
library(reshape)

setwd('H:/Data Warehouse/Centers for Disease Control and Prevention (CDC)/Prenatal Care')
files <- dir(pattern='.txt') # get the list of .txt files in the directory

for(file in files){

  message(paste('Processing',file))
  ## Read in the data
  txt <- tbl_df(read.delim2(file, stringsAsFactors=FALSE))
  
  ## We won't want to keep all rows so we are creating a flag
  txt$keep.row <- 1
  
  ## Rename State level variables
  if('State' %in% names(txt)) {
    names(txt)[names(txt) == 'State'] <- 'County'
    txt$County <- paste(txt$County,'State')
    names(txt)[names(txt) == 'State.Code'] <- 'County.Code'
  }
  
  ## There are footnotes at the end of the text files.  They can be identified
  ## by three dashes.
  found.end <- FALSE
    for(i in 1:nrow(txt)){
    if(txt[i,c('Notes')] == '---'){found.end <- TRUE}
    if(found.end){txt[i,c('keep.row')] <- 0}
  }
  rm(found.end, i)

  ## Check for the cdc.data (aggregated text file data)
  if(!exists('cdc.data')){
    cdc.data <- txt
  }
  ## cdc.data exists so we need to append rows
  else {
    ## Check to make sure we have the same number of columns as cdc.data
    if(ncol(cdc.data) != ncol(txt)){
      ## Identify the missing columns by name
      missing.cols <- names(cdc.data)[!names(cdc.data) %in% names(txt)]
      ## Get the count of missing columns
      n.missing <- length(missing.cols)
      ## Add in NA for the missing columns
      txt[,ncol(txt)+1:n.missing] <- NA
      names(txt)[(ncol(txt)-n.missing+1):ncol(txt)] <- missing.cols
      ## Clean up R Environment
      rm(missing.cols, n.missing)
    }
    ## Now that we are sure the column count is the same let's append the data
    cdc.data <- rbind(cdc.data, txt)
  } 
}
## Clean up R Environment
rm(txt, file, files)

## Now let's clean up the cdc.data
## We will use dplyr's pipe (so when you see %>% read then)

#bk <- cdc.data
cdc.data <- cdc.data %>%
  filter(keep.row == 1)

## Standardize Prenatale Care
# 0	No prenatal care
# 1	1st month
# 2	2nd month
# 3	3rd month
# 4	4th month
# 5	5th month
# 6	6th month
# 7	7th month
# 8	8th month
# 9	9th month
# 10	10th month
# 98	Excluded
# 99	Not stated/Not on certificate

cdc.data$std.pnc <- 'Other'
cdc.data[cdc.data$Month.Prenatal.Care.Began.Code %in% c(98,99),]$std.pnc <- 'Not stated/Not on certificate'
cdc.data[cdc.data$Month.Prenatal.Care.Began.Code %in% c(7,8,9,10),]$std.pnc <- '7th - 10th'
cdc.data[cdc.data$Month.Prenatal.Care.Began.Code %in% c(4,5,6),]$std.pnc <- '4th - 6th'
cdc.data[cdc.data$Month.Prenatal.Care.Began.Code %in% c(1,2,3),]$std.pnc <- '1st - 3rd'
cdc.data[cdc.data$Month.Prenatal.Care.Began.Code %in% c(0),]$std.pnc <- 'No prenatal care'

cdc.data[cdc.data$std.pnc == 'Other',c('keep.row')] <- 0

## Standardize Races
# 1002-5  American Indian or Alaska Native
# 2028-9	Other Asian 
# 2034-7	Chinese
# 2036-2	Filipino
# 2039-6	Japanese
# 2054-5	Black or African American
# 2076-8	Hawaiian
# 2106-3	White
# A-PI	Asian or Pacific Islander
cdc.data$std.race <- 'Other'
cdc.data[cdc.data$Race.Code %in% c('2028-9','2034-7','2036-2','2039-6','2076-8','A-PI'),]$std.race <- 'Asian'
cdc.data[cdc.data$Race.Code %in% c('2106-3'),]$std.race <- 'White'
cdc.data[cdc.data$Race.Code %in% c('2054-5'),]$std.race <- 'Black or African American'

## Standardize Hispanic Origin
# 2148-5  Mexican
# 2180-8	Puerto Rican
# 2182-4	Cuban
# 4	Central or South American
# 5	Other and Unknown Hispanic
# 6	Non-Hispanic White
# 7	Non-Hispanic Black
# 8	Non-Hispanic other races
# 9	Origin unknown or not stated
cdc.data$std.hisp <- 'Other'
cdc.data[cdc.data$Hispanic.Origin.Code %in% c('2148-5','2180-8','2182-4','4','5'),]$std.hisp <- 'Hispanic'

## Fill in all the blank counties with United States
cdc.data[is.na(cdc.data$County),c('County')] <- 'United States'

## Subset the data one final time
cdc.data <- cdc.data %>%
  filter(keep.row == 1) %>%
  filter(Year >= 2000) %>% 
  select(County, Births, Year, std.race, std.hisp, std.pnc)

## Final Data
message('Building Races Statistics')

## Step through the races
races <- c('Asian','Black or African American','White')

for(race in races){

  temp <- cdc.data %>%
    filter(std.race == race) %>%
    group_by(County, Year, std.race, std.pnc) %>%
    summarise(Births = sum(Births))
  ## Get totals
  totals <- temp %>%
    group_by(County, Year, std.race) %>%
    summarise(Births = sum(Births)) %>%
    mutate(std.pnc = 'Total')
  ## Append Totals
  temp <- rbind(temp, totals)
  
  ## Create/Append temp data to final data
  if(!exists('final.data')){
    final.data <- temp
  } else {
    final.data <- rbind(final.data, temp)
  }
}
## Clean up R
rm(race, races)

message('Building Ethnicity Statistics')

## Hispanic Statistics
temp <- cdc.data %>%
  filter(std.hisp == 'Hispanic') %>%
  group_by(County, Year, std.hisp, std.pnc) %>%
  summarise(Births = sum(Births))
## Get totals
totals <- temp %>%
  group_by(County, Year, std.hisp) %>%
  summarise(Births = sum(Births)) %>%
  mutate(std.pnc = 'Total')
## Append totals
temp <- rbind(temp, totals)
## Rename column
names(temp)[names(temp) == 'std.hisp'] <- 'std.race'
## Append temp data to final data
final.data <- rbind(final.data, temp) 

message('Building Total Statistics')
## Totals
temp <- cdc.data %>%
  group_by(County, Year, std.pnc) %>%
  summarise(Births = sum(Births)) %>%
  mutate(std.race = 'Total')
## Get totals
totals <- temp %>%
  group_by(County, Year, std.race) %>%
  summarise(Births = sum(Births)) %>%
  mutate(std.pnc = 'Total')
## Append Totals
temp <- rbind(temp, totals) 
final.data <- rbind(final.data, temp)%>%
  arrange(County, Year, std.race, std.pnc)

message('Building Final Data')
names(final.data) <- c('Geography', 'Year', 'Race.Ethnicity', 'Prenatal.Care', 'Births')
final.data$Race.Ethnicity <- as.factor(final.data$Race.Ethnicity)
final.data$Prenatal.Care <- as.factor(final.data$Prenatal.Care)
final.data <- melt(final.data, id=c('Geography', 'Year', 'Race.Ethnicity', 'Prenatal.Care'))
final.data <- cast(final.data, Geography + Year + Race.Ethnicity ~ Prenatal.Care, sum, fill='')

rm(totals, temp, cdc.data)

message('Saving Data to Excel')
## Save Processed Data
library(RDCOMClient)
source("http://www.omegahat.org/RDCOMClient/examples/excelUtils3.R")

xls <- COMCreate("Excel.Application")
xls[["Visible"]] <- TRUE
wb = xls[["Workbooks"]]$Add(1)
rdcomexport <- function(df, sheet.name) {
  sh = wb[["Worksheets"]]$Add()
  sh[["Name"]] <- sheet.name
  exportDataFrame(df, at = sh$Range("A1"))
}

rdcomexport(final.data,'CDC_Prenatal_Care')

xls$Sheets("Sheet1")$Delete()
filename <- 'Prenatal Care.xlsx'
wb$SaveAs(filename)
wb$Close(filename)
xls$Quit()

rm(filename, wb, xls)
