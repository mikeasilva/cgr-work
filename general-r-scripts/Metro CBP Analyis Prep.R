## Metro CBP Analysis Prep.R
#
# This script takes data processed by 'Metro CBP Data.R' and pulls and 
# aggregates the manufacturing and total industry lines.

library(dplyr)

files <- list.files('.', pattern=".rds")
for(file in files){
  cbp <- readRDS(file)
  if(cbp[1,]$is.naics==1){
    total <- cbp %>%
      filter(industry %in% c('------')) %>%
      mutate(industry = 'total')
    yr <- total[1,]$year
    mfg <- cbp %>%
      filter(industry %in% c('31----', '321///', '322///', '323///', '324///', '325///', '326///', '327///', '331///', '332///', '333///', '334///', '335///', '336///', '337///', '339///')) %>%
      select(-industry, -is.naics, -year) %>%
      group_by(msa.fips) %>%
      summarise_each(funs(sum)) %>%
      mutate(industry='mfg') %>%
      mutate(is.naics = 1) %>%
      mutate(year=yr)
    temp <- rbind(total,mfg)
    if(!exists('cbp.naics')){
      cbp.naics <- temp
    }else{
      cbp.naics <- rbind(cbp.naics, temp)
    }
  }
  else {
    total <- cbp %>%
      filter(industry %in% c('----')) %>%
      mutate(industry = 'total')
    yr <- total[1,]$year
    mfg <- cbp %>%
      filter(industry %in% c('2000', '2100', '2200', '2300', '2400', '2500', '2600', '2700', '2800', '2900', '3000', '3100', '3200', '3300', '3400', '3500', '3600', '3700', '3800', '3900')) %>%
      select(-industry, -is.naics, -year) %>%
      group_by(msa.fips) %>%
      summarise_each(funs(sum)) %>%
      mutate(industry='mfg') %>%
      mutate(is.naics = 0) %>%
      mutate(year=yr)
    temp <- rbind(total,mfg)
    if(!exists('cbp.sic')){
      cbp.sic <- temp
    }else{
      cbp.sic <- rbind(cbp.sic, temp)
    }
  }
  
}

rm(cbp, mfg, temp, total, file, files, yr)

final.data <- rbind(cbp.sic, cbp.naics) %>%
  arrange(msa.fips, industry, year) %>%
  as.data.frame(.)

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

rdcomexport(final.data,'cbp')

xls$Sheets("Sheet1")$Delete()
filename <- 'Metro CBP Anaysis Prep.xlsx'
wb$SaveAs(filename)
wb$Close(filename)