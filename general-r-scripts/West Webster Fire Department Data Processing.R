library(dplyr)
dir <- 'G:/2015 Projects/509-NEJFD Evaluation of Fire Service/ECD data/CGR-NEJFD'
patterns <- c('WEBF','UHIF')
for(pattern in patterns){
  files <- dir(dir, pattern=pattern, full.names=TRUE, ignore.case=TRUE)
  
  for(file in files){
    message(paste('Processing',file))
    
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
      
      data[i,]$call.id <- paste0(pattern,'-20',substr(as.character(data[i,]$date),5,6),'-',substr(as.character(data[i,]$date),1,2),'-',as.character(call.id2))  
      #data[i,]$call.id <- paste0(substr(as.character(data[i,]$date),1,2),'-',as.character(call.id2))  
      
      ## Identify the records within each call
      if(data[i,]$start.record == 1){
        data[i,]$record.id <- record.id <- 0
      } else{
        data[i,]$record.id <- record.id <- record.id + 1
      }
      
      if(data[i,]$record.id == 1){
        temp.call.start.check <- substr(as.character(data[i,]$date),1,2)
        temp.call.start <- paste0(pattern,'-20',substr(as.character(data[i,]$date),5,6),'-',substr(as.character(data[i,]$date),1,2))  
        if(!(temp.call.start.check == '' || temp.call.start.check == '  ')){
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
    
    message('Done!')
  }
  
  message('Processing final.data')
  final.data$sort <- 1:nrow(final.data)
  final.data$event.type <- gsub(' ', '', final.data$event.type ) # Strip out extra spaces
  final.data$date2 <- as.Date(gsub(' ', '', final.data$date ), '%m%d%y') # convert to date
  final.data$location <- gsub(' ,',', ', gsub('  ','', final.data$location))
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
  
  final.data <- final.data[!names(final.data) %in% c('date')] %>%
    rename(date = date2)
  
  first.on.scene <- final.data %>%
    do(filter(., complete.cases(arriv))) %>%
    arrange(call.id, arriv) %>%
    group_by(call.id) %>%
    mutate(min.sort = min(sort)) %>%
    mutate(keep = ifelse(sort == min.sort, 1,0)) %>%
    filter(keep == 1) %>%
    select(call.id, arriv, record.id) %>%
    mutate(first.on.scene = 1)
  
  final.data <- merge(x=final.data, y=first.on.scene, all.x=TRUE) %>%
    arrange(sort)
  
  ## Change all the data that is NA to 0
  final.data[is.na(final.data$first.on.scene),c('first.on.scene')] <- 0
  
  ## This function breaks the time into shifts
  getShifts <- function(time){
    hour <- as.numeric(substr(time, 1, 2))
    number.of.shifts <- 6
    floor((number.of.shifts/24)*hour) + 1
  }
  
  ## Create tables from the cleaned data
  message('Creating tables')
  table.1 <- final.data %>%
    filter(record.id==1) %>%
    select(call.id, record.id, id, location, cross.street.info, date, node, event.type, cr.num, create)
  
  table.2 <- final.data %>%
    filter(record.id > 1) %>%
    select(first.on.scene, sort, call.id, record.id, call.id2, cr.num, dispt, arriv, clear, dis, res, job) %>%
    merge(., table.1[,c('call.id','date','create')]) %>%
    arrange(sort) %>%
    mutate(create2 = as.POSIXct(ifelse(is.na(create), NA, paste(date, create)), format="%Y-%m-%d %H:%M:%S")) %>%
    mutate(dispt2 = as.POSIXct(ifelse(is.na(dispt), NA, paste(date, dispt)), format="%Y-%m-%d %H:%M:%S")) %>%
    mutate(arriv2 = as.POSIXct(ifelse(is.na(arriv), NA, paste(date, arriv)), format="%Y-%m-%d %H:%M:%S")) %>%
    mutate(clear2 = as.POSIXct(ifelse(is.na(clear), NA, paste(date, clear)), format="%Y-%m-%d %H:%M:%S")) %>%
    select(call.id, record.id, date, cr.num, create2, dispt2, arriv2, clear2, dis, res, job, first.on.scene) %>%
    rename(create = create2) %>%
    rename(dispt = dispt2) %>%
    rename(arriv = arriv2) %>%
    rename(clear = clear2) %>%
    select(call.id, record.id, date, cr.num, create, dispt, arriv, clear, dis, res, job, first.on.scene)
  
  table.3 <- final.notes
  
  ## Cleanup
  rm(data, notes, call.id, call.id2, call.start, drops, file, files, i, record.id, report, temp.call.start, widths, final.data, final.notes, temp.call.start.check, first.on.scene, getShifts)
  
  ## Save Processed Data
  message('Saving Tables')
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
  filename <- paste(pattern,'data.xlsx')
  wb$SaveAs(filename)
  wb$Close(filename)
  xls$Quit()
}
