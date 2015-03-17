## Nonemployer data wrangling

library(dplyr)

# https://www.census.gov/econ/nonemployer/download/cty_dd.txt
urls <- c('ftp://ftp.census.gov/econ2012/NONEMPLOYER_CSV/nonemp12co.zip',
          'ftp://ftp.census.gov/econ2011/NONEMPLOYER_CSV/nonemp11co.zip',
          'ftp://ftp.census.gov/econ2010/NONEMPLOYER_CSV/nonemp10co.zip',
          'ftp://ftp.census.gov/econ2009/NONEMPLOYER_CSV/nonemp09co.zip',
          'ftp://ftp.census.gov/econ2008/NONEMPLOYER_CSV/nonemp08co.zip',
          'ftp://ftp.census.gov/econ2007/NONEMPLOYER_CSV/nonemp07co.zip',
          'ftp://ftp.census.gov/econ2006/NONEMPLOYER_CSV/nonemp06co.zip',
          'http://www.census.gov/epcd/nonemployer/download/05_data/nonemp05co.zip',
          'http://www.census.gov/epcd/nonemployer/download/04_data/nonemp04co.zip',
          'http://www.census.gov/econ/nonemployer/download/03_data/Nonemp03co.zip',
          'http://www.census.gov/econ/nonemployer/download/02_data/Nonemp02co.zip',
          'http://www.census.gov/econ/nonemployer/download/01_data/Nonemp01co.zip',
          'http://www.census.gov/econ/nonemployer/download/00_data/Nonemp00co.zip',
          'http://www.census.gov/econ/nonemployer/download/99_data/Nonemp99co.zip',
          'http://www.census.gov/econ/nonemployer/download/98_data/Nonemp98co.zip',
          'http://www.census.gov/econ/nonemployer/download/97_data/Nonemp97co.zip')

getYear <- function(filename){
  year <- as.numeric(substr(filename, 7,8))
  if(year < 14)
    return(2000 + year)
  else
    return(1900 + year)
}

metrolist <- read.csv('metrolist.csv') %>%
  select(msa.fips, county.fips)

#temp = data.frame(file=character(), var=character())
for(url in urls){
  # Get the file name from the url
  split.url <- unlist(strsplit(url,'/'))
  destfile <- split.url[length(split.url)]
  
  # Download the file
  if(!file.exists(destfile)){
    download.file(url, destfile)
  }
  unzip(destfile)
  file <- list.files(pattern=".txt")
  data <- read.csv(file, nrow=1)
  #temp <- rbind(temp, data.frame(file=file, var=names(data)))
  
  classes <- rep('character',ncol(data))
  data <- read.csv(file, colClasses=classes)
  
  drops <- names(data) %in% c('rcptot_f','RCPTOT_F', 'rcptot_n_f', 'RCPTOT_N_F', 'estab_f', 'ESTAB_F')
  
  data <- data[!drops]
  
  if('COUNTY' %in% names(data)){
    data <- data %>%
      rename(cty = COUNTY)
  }
  if('CTY' %in% names(data)){
    data <- data %>%
      rename(cty = CTY)
  }
  if('ST' %in% names(data)){
    data <- data %>%
      rename(st = ST)
  }
  
  
  data <- data %>%
    mutate(county.fips = paste0(st,cty)) %>%
    merge(metrolist, .) %>%
    mutate(year = getYear(file))
    
  if(!exists('nonemp')){
    nonemp <- data
  } else {
    names(data) <- names(nonemp)
    nonemp <- rbind(nonemp, data)
  }
  
  unlink(file)
  rm(data, classes, destfile, file, split.url, url, drops)
}

saveRDS(nonemp, 'county Nonemployer.rds')

nonemp <- nonemp %>%
  mutate(estab = as.numeric(estab)) %>%
  mutate(rcptot = as.numeric(rcptot)) %>%
  select(-county.fips, -st, -cty) %>%
  group_by(year, msa.fips, naics) %>%
  summarise_each(funs(sum))

saveRDS(nonemp, 'Metro Nonemployer.rds')
