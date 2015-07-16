library(RCurl)
library(rvest)
library(dplyr)
library(xlsx)

place.names <- c('Syracuse',
                 'Town of Camillus',
                 'Town of Cicero',
                 'Town of Clay',
                 'Town of De Witt',
                 'Town of Elbridge',
                 'Town of Fabius',
                 'Town of Geddes',
                 'Town of La Fayette',
                 'Town of Lysander',
                 'Town of Manlius',
                 'Town of Marcellus',
                 'Town of Onondaga',
                 'Town of Otisco',
                 'Town of Pompey',
                 'Town of Salina',
                 'Town of Skaneateles',
                 'Town of Spafford',
                 'Town of Tully',
                 'Town of Van Buren',
                 'Village of Baldwinsville',
                 'Village of Camillus',
                 'Village of East Syracuse',
                 'Village of Elbridge',
                 'Village of Fabius',
                 'Village of Fayetteville',
                 'Village of Jordan',
                 'Village of Liverpool',
                 'Village of Manlius',
                 'Village of Marcellus',
                 'Village of Minoa',
                 'Village of North Syracuse',
                 'Village of Skaneateles',
                 'Village of Solvay',
                 'Village of Tully')
places <- c('715000',
            '099500',
            '141500',
            '146000',
            '188000',
            '222500',
            '238000',
            '273000',
            '380000',
            '421500',
            '432000',
            '436000',
            '532500',
            '545000',
            '588500',
            '642500',
            '678500',
            '692500',
            '729500',
            '743000',
            '045000',
            '100000',
            '216500',
            '223000',
            '238500',
            '244000',
            '368000',
            '408000',
            '432500',
            '436500',
            '463000',
            '516000',
            '679000',
            '685000',
            '730000')
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
         r='Place',
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

write.xlsx(census.data, file = "G:/2014 Projects/420-Consensus CNY/Building Permits.xlsx", sheetName = "Sheet1", row.names = FALSE)
