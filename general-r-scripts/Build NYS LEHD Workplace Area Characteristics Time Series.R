library(R.utils)

# Set the start and end of the timeseries
start <- 2002
end <- 2013

# Download, extract and parse geography crosswalk
url <- 'http://lehd.ces.census.gov/data/lodes/LODES7/ny/ny_xwalk.csv.gz'
download.file(url, 'xwalk.csv.gz')
gunzip('xwalk.csv.gz', overwrite=TRUE)
xwalk <- read.csv('xwalk.csv', nrows=1)
col.classes <- rep('character', ncol(xwalk))
xwalk <- read.csv('xwalk.csv', colClasses = col.classes)

# Download, extract and parse LEHD data
for(year in start:end){
  url <- paste0('http://lehd.ces.census.gov/data/lodes/LODES7/ny/wac/ny_wac_S000_JT00_',year,'.csv.gz')
  file.name <- paste0('lodes',year,'.csv.gz')
  csv.file.name <- paste0('lodes',year,'.csv')
  download.file(url, file.name)
  gunzip(file.name, overwrite=TRUE)
  # Parse data file
  temp <- read.csv(csv.file.name, nrows = 1)
  col.classes <- c('character', rep('numeric', ncol(temp)-1))
  temp <- read.csv(csv.file.name, colClasses = col.classes)
  # Build times series data frame
  temp$year <- year
  # Merge in crosswalk
  temp <- merge(temp, xwalk, by.x='w_geocode', by.y='tabblk2010')
  if(exists('lodes.wac')){
    lodes.wac <- rbind(lodes.wac, temp)
  }
  else{
    lodes.wac <- temp
  }
  # Housekeeping
  rm(col.classes, csv.file.name, file.name, temp, url)
  unlink(csv.file.name)
}
# Housekeeping
rm(xwalk, end, start, year)
unlink('xwalk.csv')

# Save data
saveRDS(lodes.wac, file='lodes.wac.rds')
