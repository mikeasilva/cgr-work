## This script downloads the data from Americans for the Arts
## Local Arts Index (http://www.artsindexusa.org/local-arts-index)

library(jsonlite)

base.url <- 'http://www.artsindexusa.org/fetchCounty.php?selectedCounty='

states <- c('AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY')

## Progress bar
pb <- txtProgressBar(min=0, max=length(states), style=3)
pb.i <- 0

## Step through each state
for(st in states){
  message('Starting ',st)
  
  ## Get county list
  url <- paste0('http://www.artsindexusa.org/fetchCounties.php?state=', st)
  county.fips <- fromJSON(url)
  
  ## Step through each county
  for(fips in county.fips){
    s <- unlist(strsplit(fips,":"))[1]
    county.name <- unlist(strsplit(fips,":"))[2]
    url <- paste0(base.url, s)
    json.data <- as.data.frame(fromJSON(url))
    json.data$row <- 1:nrow(json.data)
    json.data$fips <- s
    json.data$county_name <- county.name
    json.data$state <- st
    ## Store data
    if(exists("arts.data")){
      arts.data <- rbind(arts.data, json.data)
    } else{
      arts.data <- json.data
    }
  }
  
  ## Update Progress Bar
  pb.i <- pb.i + 1
  setTxtProgressBar(pb, pb.i)
}
close(pb)

write.csv(arts.data,'Local Arts Index.csv')