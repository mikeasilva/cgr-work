# Load the libraries needed for the analysis
library(reshape2)
library(x12)
# Set path to x12-ARIMA binary
x12path("C:/x12a/x12a.exe")

# Download data from http://www.labor.state.ny.us/stats/ces.zip and load it into a data frame
temp.file <- tempfile()
download.file("http://www.labor.state.ny.us/stats/ces.zip",temp.file)
data <- read.csv(unz(temp.file, "ces_naics.txt"))
unlink(temp.file)

# Select the subset by series code
seriescode.selection <- c(0, 15000000, 10000000, 20000000, 30000000, 41000000, 42000000, 43000000, 50000000, 55000000, 60000000, 65000000, 70000000, 80000000, 90000000)
data <- data[data$SERIESCODE %in% seriescode.selection, ]

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

# Concatenate area and series to form mycode
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
mdata <- melt(data, id = c("mycode","year"), variable.name = "month", na.rm=TRUE)
mdata$mydate <- paste(mdata$year,"-",mdata$month,"-01", sep="")
mdata$mydate <- as.Date(mdata$mydate, "%Y-%m-%d")
mdata <- mdata[order(as.Date(mdata$mydate, format="%Y-%m-%d")),]
nonSA.data <- dcast(mdata, year + month ~ mycode, value.var = "value", fun.aggregate=sum)

# Write the file
write.csv(nonSA.data, file = "NYS Metro CES nonSA.csv")

# Initialize seasonally adjusted data frame
sa.df <- data.frame(year=as.Date(character()), month=character(), value=character(), mycode=character()) 
# Get the list of mycode
mycodes <- c("albehs",  "albfin",  "albgov",  "albinf",	"alblei",	"albman",	"albnmc",	"alboth",	"albpbs",	"albtot",	"albtra",	"albtwu",	"binehs",	"binfin",	"bingov",	"bininf",	"binlei",	"binman",	"binnmc",	"binoth",	"binpbs",	"bintot",	"bintra",	"bintwu",	"bufehs",	"buffin",	"bufgov",	"bufinf",	"buflei",	"bufman",	"bufnmc",	"bufoth",	"bufpbs",	"buftot",	"buftra",	"buftwu",	"elmehs",	"elmfin",	"elmgov",	"elminf",	"elmlei",	"elmman",	"elmnmc",	"elmoth",	"elmpbs",	"elmtot",	"elmtra",	"elmtwu",	"gleehs",	"glefin",	"glegov",	"gleinf",	"glelei",	"gleman",	"glenmc",	"gleoth",	"glepbs",	"gletot",	"gletra",	"gletwu",	"ithehs",	"ithfin",	"ithgov",	"ithinf",	"ithlei",	"ithman",	"ithnmc",	"ithoth",	"ithpbs",	"ithtot",	"ithtra",	"ithtwu",	"kinehs",	"kinfin",	"kingov",	"kininf",	"kinlei",	"kinman",	"kinnmc",	"kinoth",	"kinpbs",	"kintot",	"kintra",	"kintwu",	"liehs",	"lifin",	"ligov",	"liinf",	"lilei",	"liman",	"linmc",	"lioth",	"lipbs",	"litot",	"litra",	"litwu",	"nycehs",	"nycfin",	"nycgov",	"nycinf",	"nyclei",	"nycman",	"nycnmc",	"nycoth",	"nycpbs",	"nyctot",	"nyctra",	"nyctwu",	"nysehs",	"nysfin",	"nysgov",	"nysinf",	"nyslei",	"nysman",	"nysnmc",	"nysoth",	"nyspbs",	"nystot",	"nystra",	"nystwu",	"pouehs",	"poufin",	"pougov",	"pouinf",	"poulei",	"pouman",	"pounmc",	"pouoth",	"poupbs",	"poutot",	"poutra",	"poutwu",	"prwehs",	"prwfin",	"prwgov",	"prwinf",	"prwlei",	"prwman",	"prwnmc",	"prwoth",	"prwpbs",	"prwtot",	"prwtra",	"prwtwu",	"rocehs",	"rocfin",	"rocgov",	"rocinf",	"roclei",	"rocman",	"rocnmc",	"rocoth",	"rocpbs",	"roctot",	"roctra",	"roctwu",	"syrehs",	"syrfin",	"syrgov",	"syrinf",	"syrlei",	"syrman",	"syrnmc",	"syroth",	"syrpbs",	"syrtot",	"syrtra",	"syrtwu",	"utiehs",	"utifin",	"utigov",	"utiinf",	"utilei",	"utiman",	"utinmc",	"utioth",	"utipbs",	"utitot",	"utitra",	"utitwu")
# Loop through the codes
for (i in 1:length(mycodes)) {
  # X-12-ARIMA loop
  temp.data <- mdata[ which(mdata$mycode==mycodes[i]), ]
  min.year <- min(temp.data$year)
  # Get the employment time series
  employ<-ts(temp.data$value,frequency=12,start(min.year,1))
  # Apply the X-12 seasonal adjustment
  x12.employ <- x12(employ)
  # Get the seasonally adjusted varriable
  sa.employ <- x12.employ@d11
  sa <- tapply(sa.employ, list(year = floor(time(sa.employ)), month = month.abb[cycle(sa.employ)]), c)
  mdata2 <- melt(sa, id = c("year"), variable.name = "month", na.rm=TRUE)
  mdata2$year <- mdata2$year + min.year - 1
  mdata2$mycode <- mycodes[i]
  sa.df <- rbind(sa.df, mdata2)
}

# Recode month
sa.df$month <- match(sa.df$month, month.abb)
sa.df$mydate <- paste(sa.df$year,"-",sa.df$month,"-01", sep="")
sa.df$mydate <- as.Date(sa.df$mydate, "%Y-%m-%d")
SA.data <- dcast(sa.df, mydate + year + month ~ mycode, value.var = "value", fun.aggregate=sum)
SA.data <- SA.data[,!(names(data) %in% c("mydate"))]
write.csv(SA.data, file = "NYS Metro CES SA.csv")