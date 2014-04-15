# Load the libraries needed for the analysis
library(reshape2)
library(x12)
# Set path to x12-ARIMA binary
x12path("C:/x12a/x12a.exe")

# Download data from http://www.labor.state.ny.us/stats/ces.zip and load it into a data frame
temp.file <- tempfile()
download.file("http://www.labor.state.ny.us/stats/ces.zip",temp.file)
ces_naics <- read.csv(unz(temp.file, "ces_naics.txt"))
ces_minor <- read.csv(unz(temp.file, "ces_minor.txt"))
unlink(temp.file)
rm(temp.file)

# Select the Rochester MSA data
roc.msa <- 040380
ces_naics <- ces_naics[which(ces_naics$AREA == roc.msa),]

# Select the minor area's data
genesee.county <- 000037
seneca.county <- 000099
wyoming.county <- 000121
yates.county <- 000123
ces_minor <- ces_minor[which(ces_minor$AREA == genesee.county | ces_minor$AREA == seneca.county | ces_minor$AREA == wyoming.county | ces_minor$AREA == yates.county),]

ces <- rbind(ces_naics, ces_minor)

# Remove unneeded variables
rm(ces_naics, ces_minor, roc.msa, genesee.county, seneca.county, wyoming.county, yates.county)

# Recode series code
myseries <- function(x){
  if(x==0)
    return("flrtot")
  if(x==10000000)
    return("flrnmc")
  if(x==15000000) 
    return("flrnmc")
  if(x==20000000)
    return("flrnmc")
  if(x==30000000)
    return("flrman")
  if(x==41000000)
    return("flrtra")
  if(x==42000000)
    return("flrtra")
  if(x==43000000)
    return("flrtwu")
  if(x==50000000)
    return("flrinf")
  if(x==55000000)
    return("flrfin")
  if(x==60000000)
    return("flrpbs")
  if(x==65000000)
    return("flrehs")
  if(x==70000000)
    return("flrlei")
  if(x==80000000)
    return("flroth")
  if(x==90000000)
    return("flrgov")
  else
    return(NA)
}

ces$mycode <- sapply(ces$SERIESCODE, myseries)

# Rename variables
names(ces)[names(ces)=="YEAR"] <- "year"
names(ces)[names(ces)=="JAN"] <- "01"
names(ces)[names(ces)=="FEB"] <- "02"
names(ces)[names(ces)=="MAR"] <- "03"
names(ces)[names(ces)=="APR"] <- "04"
names(ces)[names(ces)=="MAY"] <- "05"
names(ces)[names(ces)=="JUN"] <- "06"
names(ces)[names(ces)=="JUL"] <- "07"
names(ces)[names(ces)=="AUG"] <- "08"
names(ces)[names(ces)=="SEP"] <- "09"
names(ces)[names(ces)=="OCT"] <- "10"
names(ces)[names(ces)=="NOV"] <- "11"
names(ces)[names(ces)=="DEC"] <- "12"

# Drop unwanted columns
ces <- ces[,!(names(ces) %in% c("SERIESCODE","INDUSTRY_TITLE", "AREATYPE", "AREA", "AREANAME", "ANNUAL") )]

# Create long data frame
mdata <- melt(ces, id = c("mycode","year"), variable.name = "month", na.rm=TRUE)
# Remove the unclassified series
mdata <- mdata[!is.na(mdata$mycode),]

# Create Date
mdata$mydate <- as.Date(paste(mdata$year,"-",mdata$month,"-01", sep=""), "%Y-%m-%d")
# Grab statistics for later
min.year = min(mdata$year)
max.date = max(mdata$mydate)

# Aggregate (sum) the data
mdata <- aggregate(value~mycode+year+month+mydate, data=mdata, FUN="sum")

nonSA.data <- dcast(mdata, year + month ~ mycode, value.var = "value", fun.aggregate=sum)
# Write the file
write.csv(nonSA.data, file = "Finger Lakes Region CES nonSA.csv")

# Remove variables that are not needed
rm(ces,nonSA.data)

# Time series objects will be stored in this list
x12.batch.data = list()
mycodes <- unique(mdata$mycode)

for(code in mycodes)
{
  temp.data <- mdata[ which(mdata$mycode==code), ]
  x12.batch.data <- c(x12.batch.data, list(ts(temp.data$value,frequency=12,start(min.year,1))))
}

rm(code, temp.data)

# Change working directory for X-12 output
setwd("./x12")
# Apply the X-12 seasonal adjustment
x12.batch.data <- new("x12Batch", x12.batch.data, mycodes)
x12.batch.data <- x12(x12.batch.data)

#x12.results = list()
i <- 1
# Initialize seasonally adjusted data frame
sa.df <- data.frame(year=as.Date(character()), month=character(), value=character(), mycode=character()) 
for(x12 in x12.batch.data@x12List@.Data){
  #x12.results <- c(x12.results, list(x12@x12Output@d11))
  # Get the X-12 seasonally adjusted time series as a data frame
  sa <- tapply(x12@x12Output@d11, list(year = floor(time(x12@x12Output@d11)), month = month.abb[cycle(x12@x12Output@d11)]), c)
  # Make it long
  sa <- melt(sa, id = c("year"), variable.name = "month", na.rm=TRUE)
  # Fix the year
  sa$year <- sa$year + min.year - 1
  # Add in the code
  sa$mycode <- mycodes[i]
  # Append it to the seasonally adjusted data frame
  sa.df <- rbind(sa.df, sa)
  # Update the index for mycode[i]
  i <- i + 1
}
# Create a date column (for sorting)
sa.df$mydate <- paste(sa.df$year,"-",match(sa.df$month, month.abb),"-01", sep="")
sa.df$mydate <- as.Date(sa.df$mydate, "%Y-%m-%d")

# Build final matrix
SA.data <- dcast(sa.df, mydate + year + month ~ mycode, value.var = "value", fun.aggregate=sum)
# Drop sorting variable
#SA.data <- SA.data[,!(names(data) %in% c("mydate"))]
# Move up out of the x12 directory
setwd("../")
# Write the final file
write.csv(SA.data, file = "Finger Lakes Region CES SA.csv")
