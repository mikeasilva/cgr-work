## 
# WEGO.R
#
# Written By: Mike Silva (msilva@cgr.org)
#
# This R Script processes WEGO and West Goshen PA Police Department Calls for 
# Service data.  It treats these two police departments as a merged entity.
# There are metrics for All calls for service and "Real" calls for service,
# which excludes admin and special patrols.
##

library(data.table)

# Read in the CSV
dt1 <- read.csv("G:/2014 Projects/412-East Goshen and WEGO Police Consolidation/data analysis/calls for service/wego-5-8-2014.csv")
dt2 <- read.csv("G:/2014 Projects/412-East Goshen and WEGO Police Consolidation/data analysis/calls for service/westgoshen-5-8-2014.csv")

# Select only the columns we want to keep
keep <- c("time","CGR.Month", "CGR.Day.1", "CGR.Year", "Include.in.Counts","Counts...Admin.and.Special.Patrols")
dt1 <- dt1[keep]
dt1$agency <- "WEGO"
dt2 <- dt2[keep]
dt2$agency <- "West Goshen"

# Load data into data table
calls <- as.data.table(rbind(dt1, dt2))

# Fix the hour
calls$h <- sapply(strsplit(as.character(calls$time),":"),
                  function(x) {
                    x <- as.numeric(x)
                    if(x[1] >9 ){
                      x[1]
                    }else {
                      paste0("0",x[1])
                    }
                  }
                )

calls$Full.Time <- paste0(calls$h,":00:00")

# Build sorting variable
calls$CGR.Date <- paste(calls$CGR.Month, calls$CGR.Day.1, calls$CGR.Year, 
                        calls$Full.Time)

# Summarize data
calls<- as.data.frame(calls[,list(all=sum(Include.in.Counts)
                                  , real=sum(Counts...Admin.and.Special.Patrols))
                            , by='CGR.Date'])

# Change string into date time
calls$Date.Time <- strptime(calls$CGR.Date, "%B %d %Y %H:%M:%S")
calls$Hour <- format(as.POSIXct(calls$Date.Time, format="%Y-%m-%d %H:%M")
                     , format="%H:00")

# Recode hour as integer
calls$x <- sapply(strsplit(calls$Hour,":"),
                  function(x) {
                    x <- as.numeric(x)
                    x[1]+x[2]/60
                  }
)

# Draw boxplots
boxplot(all~x,data=calls, main="All Calls for Service", 
        xlab="Hour of the Day", ylab="Number of Calls")
boxplot(real~x,data=calls, main="Real Calls for Service", 
        xlab="Hour of the Day", ylab="Number of Calls")

# Build summary data frame
df <- data.frame()
for (i in 0:max(calls$all)) {
  df[i+1,1] <- i
  df[i+1,2] <- nrow(calls[calls$all == i,])
  df[i+1,3] <- nrow(calls[calls$all >= i,])
  df[i+1,4] <- nrow(calls[calls$real == i,])
  df[i+1,5] <- nrow(calls[calls$real >= i,])
}
names(df) <- c("Number of Calls", 
               "Count of All Calls", "Count of All Calls >= Number of Calls", 
               "Count of Real Calls", "Count of Real Calls >= Number of Calls")
# Display the occurances when the number of calls are >= 5
library(ggplot2)
ggplot(calls[calls$real >= 5,], aes(x=factor(x))) + 
  geom_bar() + 
  xlab("Hour of the Day") + 
  ylab("One Hour with 5+ Calls for Service")


# Get the summary
message("All Calls")
table(calls$all)
tapply(calls$all, calls$Hour, summary)

message("Real Calls")
table(calls$real)
tapply(calls$real, calls$Hour, summary)

message("Summary Data Frame")
df