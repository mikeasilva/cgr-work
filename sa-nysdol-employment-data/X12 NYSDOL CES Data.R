# Download data from http://www.labor.state.ny.us/stats/ces.zip and load it into a data frame
temp.file <- tempfile()
download.file("http://www.labor.state.ny.us/stats/ces.zip",temp.file)
data <- read.csv(unz(temp.file, "ces_naics.txt"))
unlink(temp.file)
step.1 <- nrow(data)

# Select the subset by series code
seriescode.selection <- c(0, 15000000, 10000000, 20000000, 30000000, 41000000, 42000000, 43000000, 50000000, 55000000, 60000000, 65000000, 70000000, 80000000, 90000000)
data <- data[data$SERIESCODE %in% seriescode.selection, ]
step.2 <- nrow(data)

# Recode area
myarea <- function(x){
  if(x == 36) 
    return("nys")
  if(x == 10580) 
    return("alb")
  if(x == 13780) 
    return("bin")
  if(x == 15380) 
    return("buf")
  if(x == 21300) 
    return("elm")
  if(x == 24020) 
    return("gle")
  if(x == 27060) 
    return("ith")
  if(x == 28740) 
    return("kin")
  if(x == 35004) 
    return("li")
  if(x == 39100) 
    return("pou")
  if(x == 40380) 
    return("roc")
  if(x == 45060) 
    return("syr")
  if(x == 46540) 
    return("uti")
  if(x == 93561) 
    return("nyc")
  if(x == 93562) 
    return("prw")
  else
    return(NA)
}
data$myarea <- sapply(data$AREA, myarea)

# Recode series code
myseries <- function(x){
  if(x==0)
    return("tot")
  if(x==10000000)
    return("nmc")
  if(x==15000000) 
    return("nmc")
  if(x==20000000)
    return("nmc")
  if(x==30000000)
    return("man")
  if(x==41000000)
    return("tra")
  if(x==42000000)
    return("tra")
  if(x==43000000)
    return("twu")
  if(x==50000000)
    return("inf")
  if(x==55000000)
    return("fin")
  if(x==60000000)
    return("pbs")
  if(x==65000000)
    return("ehs")
  if(x==70000000)
    return("lei")
  if(x==80000000)
    return("oth")
  if(x==90000000)
    return("gov")
  else
    return(NA)
}
data$myseries <- sapply(data$SERIESCODE, myseries)

# Concatenate area ans series to form mycode
data$mycode <- paste(data$myarea,data$myseries, sep="")

# Rename variables
names(data)[names(data)=="YEAR"] <- "year"
names(data)[names(data)=="JAN"] <- "01"
names(data)[names(data)=="FEB"] <- "02"
names(data)[names(data)=="MAR"] <- "03"
names(data)[names(data)=="APR"] <- "04"
names(data)[names(data)=="MAY"] <- "05"
names(data)[names(data)=="JUN"] <- "06"
names(data)[names(data)=="JUL"] <- "07"
names(data)[names(data)=="AUG"] <- "08"
names(data)[names(data)=="SEP"] <- "09"
names(data)[names(data)=="OCT"] <- "10"
names(data)[names(data)=="NOV"] <- "11"
names(data)[names(data)=="DEC"] <- "12"

# Drop unwanted columns
drops <- c("SERIESCODE","INDUSTRY_TITLE", "AREATYPE", "AREA", "AREANAME", "ANNUAL","myarea","myseries")
data <- data[,!(names(data) %in% drops)]

# Normalize the data
library(reshape2)
mdata <- melt(data, id = c("mycode","year"), variable.name = "month", na.rm=TRUE)
mdata$mydate <- paste(mdata$year,"-",mdata$month,"-01", sep="")
mdata$mydate <- as.Date(mdata$mydate, "%Y-%m-%d")
mdata <- mdata[order(as.Date(mdata$mydate, format="%Y-%m-%d")),]
nonSA.data <- dcast(mdata, year + month ~ mycode, value.var = "value", fun.aggregate=sum)
#nonSA2.data <- dcast(mdata, mycode + year ~ month, value.var = "value", fun.aggregate=sum)

# Write the file
write.csv(nonSA.data, file = "NYS Metro CES nonSA.csv")
#write.csv(nonSA2.data, file = "NYS Metro CES nonSA2.csv")

# Hack right now
# I need to step through all the series
newdata <- mdata[ which(mdata$mycode=='nystot'), ]
employ<-ts(newdata$value,frequency=12,start(1990,1))
deseason<-stl(employ,s.window="periodic")

library("x12")
x12path("C:/x12a/x12a.exe")
sa.employ <- x12(employ)