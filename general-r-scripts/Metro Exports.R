library(rvest)
library(dplyr)
library(xlsx)

export.html <- html('http://tse.export.gov/metro/MetroMapDisplay.aspx?ReportID=1&Referrer=SelectReports.aspx&DataSource=Metro&ReportOption=Map')

exports <- export.html %>%
  html_node('#ScrollableTable1_tblScrollData') %>%
  html_table() %>%
  as.data.frame(.)

names(exports) <- export.html %>%
  html_node('#ScrollableTable1_tlbHeader') %>%
  html_table() %>%
  as.data.frame(.) %>%
  names(.)

write.xlsx(exports, file='Metro Exports.xlsx', sheetName='Sheet1', row.names=FALSE)
