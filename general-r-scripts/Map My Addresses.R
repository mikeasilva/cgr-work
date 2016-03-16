library(ggmap)

geocodeMe <- function(address){
  # Make the request
  if(!exists('api.key')){
    library(ggmap)
    geo_reply = geocode(address, output="all", override_limit=TRUE, messaging=FALSE)
  } else {
    library(rjson)
    url <- paste0("https://maps.googleapis.com/maps/api/geocode/json?address=",address,"&sensor=false&key=",api.key)
    geo_reply <- fromJSON(file=url, method='C')
  }
  
  # initialize return varriables
  location.type <- lat <- lng <- formatted.address <- administrative.area.level.1 <- administrative.area.level.2 <- administrative.area.level.3 <- accuracy <- NA
  status <- geo_reply$status
  
  if(status == "OVER_QUERY_LIMIT"){
    message("OVER QUERY LIMIT - ", appendLF = FALSE)
    if(use.api.key == FALSE){
      message("Pausing for 1 hour at:",as.character(Sys.time()))
      Sys.sleep(60*60)
      return (geocodeMe(address))
    } else {
      # 2500 requests with API key used up so switch modes
      message("Switching to requests without API key")
      use.api.key <<- FALSE
      return (geocodeMe(address))
    }
  }
  
  if (status == "OK"){
    # Get a clean address
    formatted.address <- geo_reply$results[[1]]$formatted_address
    
    # Get lat & lng
    location.type <- geo_reply$results[[1]]$geometry$location_type
    lat <- geo_reply$results[[1]]$geometry$location$lat
    lng <- geo_reply$results[[1]]$geometry$location$lng
    
    accuracy <- tryCatch(geo_reply$results[[1]]$types[[1]], error=function(e) NA)
    
    # Loop through the address components
    ac <- geo_reply$results[[1]]$address_components
    for(ii in seq(1, length(ac))){
      if(ac[[ii]]$types[1] == "administrative_area_level_3"){
        administrative.area.level.3 <- ac[[ii]]$short_name
      }
      if(ac[[ii]]$types[1] == "administrative_area_level_2"){
        administrative.area.level.2 <- ac[[ii]]$short_name
      }
      if(ac[[ii]]$types[1] == "administrative_area_level_1"){
        administrative.area.level.1 <- ac[[ii]]$short_name
      }
    }
  }
  
  # Return the data a vector
  return(c(address, status, location.type, lat, lng, formatted.address, administrative.area.level.1, administrative.area.level.2, administrative.area.level.3, accuracy))  
}

# This function helps insert rows into the geocoded data frame
# Source: http://stackoverflow.com/questions/11561856/add-new-row-to-dataframe
insertRow <- function(existing.data.frame, new.row, row) {
  existing.data.frame[row,] <- new.row
  existing.data.frame
}

# Initialize the data frame that will hold the geocoded info
geocoded <- data.frame("Address" = as.character(), 
                       "Status" = as.character(), 
                       "Location Type" = as.character(), 
                       "Lat" = as.character(), 
                       "Lng" = as.character(), 
                       "Formatted Address" = as.character(),
                       "Level 1" = as.character(), 
                       "Level 2" = as.character(), 
                       "Level 3" = as.character(),
                       "Accuracy" = as.character(),
                       stringsAsFactors=FALSE)


# Read in the data
data.filename <- 'map_my_addresses.csv'
df <- read.csv(data.filename, nrows = 1)
df <- read.csv(data.filename, colClasses = rep('character',ncol(df)))
# Create the Full Address
df$FullAddress <- paste(df$Address,df$City,df$State,',',df$Zip)

# Geocode the results and insert them into the data frame
for (i in seq(1, nrow(df))){
  result <- geocodeMe(df[i,]$FullAddress)
  geocoded <- insertRow(geocoded, result, i)
}

df <- df[,c('Name','FullAddress')]
names(df) <- c('Name','Address')
geocoded <- merge(df, geocoded)
# Convert the data types
geocoded$Lat <- as.numeric(geocoded$Lat)
geocoded$Lng <- as.numeric(geocoded$Lng)

# Map the Geocoded Data
map <- get_map(location = c(lon = mean(geocoded$Lng), lat = mean(geocoded$Lat)), zoom = 13, source = "stamen", maptype = "terrain")
ggmap(map, extent = "device") + 
  geom_point(aes(Lng,Lat), data=geocoded, color="red", size=3) + 
  geom_text(aes(x=Lng,y=Lat,label=Name), data=geocoded, fontface = "bold", vjust = 0, nudge_y = 0.001) + 
  geom_label(aes(-77.565, 43.13, label="Map Key\nN.S. = Northstar"))
