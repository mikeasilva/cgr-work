require(rjson)  
## This function takes an API url and returns a data frame containing the data
ACS_API <- function(year, acs.year=1, est.cols, char.cols=NA, acs.for, api.key, clean.up=TRUE){
  
  ## Build the API URL
  base.url <- paste0('http://api.census.gov/data/',year,'/acs',acs.year)
  ## The Get portion of the API URL
  get.string <- ''
  if(length(char.cols)>1 || !is.na(char.cols)){
    for (c in char.cols){
      get.string <- paste0(get.string, c, ',')
    }
  }
  for(e in est.cols){
    get.string <- paste0(get.string, e, 'E,', e, 'M,')
  }
  get.string <- substr(get.string, 1, nchar(get.string)-1)
  
  api.url <- paste0(base.url, '?get=', get.string, '&for=', acs.for, '&key=', api.key)
  
  
  ## Request the data
  data <- fromJSON(file=api.url, method='C')
  ## Convert List to Data Frame
  data <- data.frame(matrix(unlist(data), nrow=length(data), byrow=T))
  ## Convert factors to characters
  data <- data.frame(lapply(data, as.character), stringsAsFactors=FALSE)
  ## Clean up the names
  names(data) <- data[1,]
  ## Remove 1st Row (since it is the variable name)
  data <- data[2:nrow(data),]
  if(length(char.cols)>1 || !is.na(char.cols)){
    ## Change characters to numbers
    col.to.convert <- names(data)[!names(data) %in% char.cols]
    for(ctc in col.to.convert){
      data[,ctc] <- as.numeric(data[,ctc])
    }
  }
  
  ## Only return the data selected
  if(clean.up){
    keep <- strsplit(get.string, ",")
    data <- data[keep[[1]]]
  }
  
  ## Return the data frame
  return(data)
}