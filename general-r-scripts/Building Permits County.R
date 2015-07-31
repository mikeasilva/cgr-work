library(RCurl)
library(rvest)
library(dplyr)
library(xlsx)

place.names <- c('Erie County',
                 'Monroe County',
                 'Onondaga County')
places <- c('029',
            '055',
            '067')
years <- 2005:2014

pb <- txtProgressBar(min = 1, max = (length(years) * length(places)), style = 3)

count <- 0
for(i in 1:length(places)){
  place <- places[i]
  place.name <- place.names[i]
  
  for(year in years){
    count <- count + 1
    setTxtProgressBar(pb, count)
    temp <- html(postForm('http://censtats.census.gov/cgi-bin/bldgprmt/bldgdisp.pl', 
                          o='Annual',
                          S='36New York',
                          M='',
                          Y=year,
                          r='County',
                          A='2014 1996 2015',
                          C=place,
                          checkCounty='Place'
    )) %>%
      html_nodes("table") %>%
      html_table()
    temp <- temp[[3]]
    names(temp) <- c('BLANK','Item','Est Building','Est Units','Est Construction Cost','Reported Building','Reported Units','Reported Construction Cost')
    temp <- temp %>%
      mutate(Place = place.name) %>%
      mutate(Year = year)
    
    if(exists("census.data")){
      census.data <- rbind(census.data,temp)
    }
    else{
      census.data <- temp
    }
  }
}
close(pb)

census.data <- select(census.data, -BLANK)

#write.csv(census.data, 'G:/2014 Projects/420-Consensus CNY/Building Permits.csv', row.names = FALSE)

write.xlsx(census.data, file = "G:/2014 Projects/420-Consensus CNY/Building Permits County.xlsx", sheetName = "Sheet1", row.names = FALSE)
