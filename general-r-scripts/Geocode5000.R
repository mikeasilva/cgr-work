#allzips <- read.csv('~/allzips.csv', colClasses = "character")
# Remove all but the zip code
#allzips <- allzips$Zip.Code
# Remove the duplicates
#allzips <- allzips[!duplicated(allzips)]

geocode5000 <- function(address.vector, api.key = FALSE){
  # Initialize the variables
  if(api.key == FALSE){
    use.api.key <- FALSE
  } else {
    use.api.key <- TRUE
  }
  start.index = 1
  
  # Initialize the tempfile
  tempfilename <- 'geocoded.rds'
  if (file.exists(tempfilename)){
    print("Found temp file - resuming from index:")
    geocoded <- readRDS(tempfilename)
    start.index <- nrow(geocoded)
    print(start.index)
  }
  else{
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
  }
  # This function helps insert rows into the geocoded data frame
  # Source: http://stackoverflow.com/questions/11561856/add-new-row-to-dataframe
  insertRow <- function(existing.data.frame, new.row, row) {
    existing.data.frame[row,] <- new.row
    existing.data.frame
  }
  
  # This function returns a vector that contains geocoded data
  geocodeMe <- function(address){
    # Make the request
    if(use.api.key == FALSE){
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
  
  total <- length(address.vector)
  
  # Check to make sure request isn't too big
  if(total > 5000){
    number.removed <- total - 5000
    message("Warning: request list too large. Truncating by ",number.removed,"requests.")
    total <- 5000
  }
  
  pb <- txtProgressBar(min = 0, max = total, style = 3)
  
  # Loop through the addresses
  for (i in seq(start.index, total)){
    #message("Geocode request number ",i," of ",total,"...", appendLF = FALSE)
    
    # Get the gecoded info
    result <- geocodeMe(address.vector[i])
    
    # Append it to the data frame
    geocoded <- insertRow(geocoded, result, i)
    
    # Save it to the temp files
    saveRDS(geocoded, tempfilename)
    
    # Display the progress
    setTxtProgressBar(pb, i)
  }
  write.table(geocoded, file="~/geocoded.csv", sep=",", row.names=FALSE)

}