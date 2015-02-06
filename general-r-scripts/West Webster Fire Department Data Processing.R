dir <- 'G:/2015 Projects/509-NEJFD Evaluation of Fire Service/ECD data/Text Files'

files <- dir(dir, full.names = TRUE, ignore.case = TRUE)

for(file in files){
  message(paste0('Processing ',file))
  
  ## This indicates where the breaks are
  widths <- c(5,30,31,7,5,7,8,7,7,7,7,4,4,3)
  
  ## Read in the data
  data <- read.fwf(file, widths=widths, fill=T, stringsAsFactors=F)
  names(data) <- c('id','location','cross.street.info','date','node','event.type','cr.num','create','dispt','arriv','clear','dis','res','job')
  
  ## This will indicate rows we need to drop
  data$drop.me <- 0
  
  ## We want to remove the reports so let's identify where they start
  data$report <- 0
  data[data$id == 'Numbe',]$report <- 1
  
  ## Check for lines begining with ===== or ----- because they are new records
  data$start.record <- 0
  data[data$id %in% c('=====','-----'),]$start.record <- 1
  
  ## Initialize variable before walking through
  call.id <- data$call.id <- 'string'
  call.start <- data$call.id2 <- call.id2 <- data$record.id <- record.id <- 0
  report <- FALSE
  drops <- c('Agenc', 'Proce', 'Numbe', 'HOUR ', 'LOCATION                      ', 'AND REMARKS                   ', ' NUMBER                       ')
  
  # Step through all records
  for(i in 1:nrow(data)){
    
    ## Identify the calls
    data[i,]$call.id2 <- call.id2 <- call.id2 + data[i,]$start.record
    
    data[i,]$call.id <- paste0(substr(as.character(data[i,]$date),1,2),'-',as.character(call.id2))  
    
    ## Identify the records within each call
    if(data[i,]$start.record == 1){
      data[i,]$record.id <- record.id <- 0
    } else{
      data[i,]$record.id <- record.id <- record.id + 1
    }
    
    if(data[i,]$record.id == 1){
      temp.call.start <- substr(as.character(data[i,]$date),1,2)
      if(!(temp.call.start == '' || temp.call.start == '  ')){
        call.start <- temp.call.start
      }
      call.id <- paste0(call.start,'-',as.character(call.id2))  
    }
    data[i,]$call.id <- call.id
    
    ## Check to see if we have got to the reports section
    if(data[i,]$report == 1){
      report <- TRUE
    }
    
    ## Check to see if we should drop this row
    if(report || data[i+1,]$id == 'Agenc' || data[i,]$start.record == 1 || data[i,]$id %in% drops || data[i,]$location %in% drops)
    {
      data[i,]$drop.me <- 1
    }
    
    message('Done!')
  }
  
  ## Drop unneeded rows
  data <- data[data$drop.me == 0, !names(data) %in% c('drop.me', 'report', 'start.record')]
  notes <- data.frame(call.id=data[data$record.id ==2,]$call.id, call.notes=paste0(data[data$record.id ==2,]$location,data[data$record.id ==2,]$cross.street.info))
  notes <- notes[!notes$call.notes == '                                                             ',]
  
  if(!exists('final.data')){
    final.data <- data
    final.notes <- notes
  } else {
    final.data <- rbind(final.data, data)
    final.notes <- rbind(final.notes, notes)
  }
  
  rm(data, notes, call.id, call.id2, call.start, dir, drops, file, files, i, record.id, report, temp.call.start, widths)
}


final.data$event.type <- gsub(' ', '', final.data$event.type ) # Strip out extra spaces
final.data$date <- as.Date(gsub(' ', '', final.data$date ), '%d%M%y') # convert to date
## Fix Times
final.data$create <- strftime(strptime(final.data$create, "%H%M%S"),format="%H:%M:%S")
final.data$dispt <- strftime(strptime(final.data$dispt, "%H%M%S"),format="%H:%M:%S")
final.data$arriv <- strftime(strptime(final.data$arriv, "%H%M%S"),format="%H:%M:%S")
final.data$clear <- strftime(strptime(final.data$clear, "%H%M%S"),format="%H:%M:%S")
## Fix Variable Types
final.data$dis  <- as.numeric(final.data$dis)
final.data$res  <- as.numeric(final.data$res)
final.data$job  <- as.numeric(final.data$job)
final.data$id   <- as.numeric(final.data$id)
final.data$node <- as.numeric(final.data$node)

## Create tables from the cleaned data
table.1 <- final.data[final.data$record.id==1, c(names(final.data)[1:8],'call.id','record.id')]
table.2 <- final.data[final.data$record.id > 1, c('cr.num',names(final.data)[9:16],'call.id','record.id')]
table.3 <- final.notes

## Cleanup
rm(final.data, final.notes)


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

rdcomexport(table.3,'table.3')
rdcomexport(table.2,'table.2')
rdcomexport(table.1,'table.1')

xls$Sheets("Sheet1")$Delete()
filename <- 'data.xlsx'
wb$SaveAs(filename)
wb$Close(filename)
xls$Quit()