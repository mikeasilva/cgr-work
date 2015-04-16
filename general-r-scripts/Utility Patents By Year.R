## Utility Patents by Year
## This script scrapes the PTO's website for their utility patents by year and
## creates and excel file 

library(dplyr)
library(rvest)
library(reshape2)
library(xlsx)

## Value & Variable Names
val.name <- 'Utility Patents'
var.name <- 'Year'
## The path of the output
file.path <- 'H:/Data Warehouse/US Patent and Trademark Office (USPTO)/Utility Patents By Year.xlsx'

## Scrape the web for utility patent grant figures
url <- 'http://www.uspto.gov/web/offices/ac/ido/oeip/taf/countyall/usa_county_gd.htm'

pto <- html(url) %>%
  html_nodes('table') %>%
  html_table() %>%
  as.data.frame(.) %>%
  select(-Total)

## Reshape from wide to long
pto <- melt(pto, id.vars = names(pto)[1:4], variable.name=var.name, 
            value.name=val.name)

## Reorder the columns
pto <- pto[,c(names(pto)[1:4], val.name, var.name)]

## Save the PTO data
write.xlsx(x=pto, file=file.path, sheetName='USPTO_Utility_Patents_By_Year', 
           row.names = FALSE)
# The quicker alternative
#write.csv(pto, 'H:/Data Warehouse/US Patent and Trademark Office (USPTO)/Utility Patents By Year.csv', row.names=FALSE)
