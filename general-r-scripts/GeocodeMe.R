library(ggmap)

data <- read.csv('~/zips2.csv', colClasses = "character")

# This function returns a vector that contains geocoded data
geocodeMe <- function(address){
  # Make the request
  geo_reply = geocode(address, output='all', messaging=TRUE, override_limit=TRUE)
  
  # initialize return varriables
  location.type <- lat <- lng <- formatted.address <- administrative.area.level.1 <- administrative.area.level.2 <- administrative.area.level.3 <- NA
  status <- geo_reply$status
  
  if(status == "OVER_QUERY_LIMIT"){
    print("OVER QUERY LIMIT - Pausing for 1 hour at:") 
    time <- Sys.time()
    print(as.character(time))
    Sys.sleep(60*60)
    return (geocodeMe(address))
  }
  
  if (status == "OK"){
    # Get a clean address
    formatted.address <- geo_reply$results[[1]]$formatted_address
    
    # Get lat & lng
    location.type <- geo_reply$results[[1]]$geometry$location_type
    lat <- geo_reply$results[[1]]$geometry$location$lat
    lng <- geo_reply$results[[1]]$geometry$location$lat
    
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
  return(c(address, status, location.type, lat, lng, formatted.address, administrative.area.level.1, administrative.area.level.2, administrative.area.level.3))  
}

# This function adds a row to a data frame
insertRow <- function(existing.data.frame, new.row, row) {
  existing.data.frame[seq(row+1,nrow(existing.data.frame)+1),] <- existing.data.frame[seq(row,nrow(existing.data.frame)),]
  existing.data.frame[row,] <- new.row
  existing.data.frame
}

addresses <- data$Zip
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
                       stringsAsFactors=FALSE)

# Loop through the addresses
for (i in seq(1, length(addresses))){
  # Display the progress
  message(i," of ",length(addresses),">", appendLF = FALSE)
  
  # Get the gecoded info
  result <- geocodeMe(addresses[i])
  
  # Append it to the data frame
  geocoded <- insertRow(geocoded, result, i)
}

# Write all the data to a csv
write.table(geocoded, file="geocoded.csv", sep=",", row.names=FALSE)
