census.geocode <- function(address){
  library(jsonlite)
  address <- URLencode(address)
  url <- paste0("http://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=",address,"&benchmark=Public_AR_Current&format=json")
  api <- fromJSON(url)
  if(is.null(api$result$addressMatches$coordinates)){
    return(list(lat=NA,lng=NA))
  }else{
    coords <- api$result$addressMatches$coordinates
    return(list(lat=coords$y,lng=coords$x))
  }
}
