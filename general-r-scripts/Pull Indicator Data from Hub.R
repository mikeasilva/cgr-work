# Pull Data from Hub
library(cp)
library(dplyr)
library(openxlsx)

file_name <- "G:/2020 Projects/033-Oswego County Opioid Assessment/Data/Indicators from the Hub.xlsx"

geos <- c("36", "36075", "36125")
indicators <- c("CI_05018_US","CI_09006_NY","CI_09012_US","CI_09030_NY","CI_09039_US","CI_09069_NY","CI_09074_NY","CI_09013_US","CI_10017_US","CI_13008_NY","CI_09019_NY",
                "CI_11015_NY","CI_07003_US","CI_04001_US","CI_09001_US")


wb <- createWorkbook()
sheet_number <- 0

for(indicator in indicators){
  message(paste("Working on", indicator))
  
  sheet_number <- sheet_number + 1
  
  addWorksheet(wb, sheetName = indicator)
  
  df <- hub_get(indicator) %>%
    filter(ci_geography_id %in% geos)
  
  writeDataTable(wb, sheet = sheet_number, x = df, tableStyle = "TableStyleMedium9", withFilter = FALSE)
  saveWorkbook(wb, file_name, overwrite = TRUE)
}