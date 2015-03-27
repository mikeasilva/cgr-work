library(ggplot2)

ApplyQuintiles <- function(x) {
  cut(x, breaks=c(quantile(data$destination, probs = seq(0, 1, by = 0.20))), 
      labels=c("0-20","20-40","40-60","60-80","80-100"), include.lowest=TRUE)
}

#extract reference data
mapstates <- map_data("state")
data <- read.csv('2007 ROC Commodities Flow.csv')

data$quintiles <- sapply(data$destination, ApplyQuintiles)

#merge data with ggplot county coordinates
mergedata <- merge(mapstates, data, by.x = "region", by.y = "state.name")
mergedata <- mergedata[order(mergedata$order),]

#draw map
map <- ggplot(mergedata, aes(long,lat,group=group)) + geom_polygon(aes(fill=quintiles))
map <- map + scale_fill_brewer(palette="Blues") +
  coord_map(project="globular") +
  theme(legend.position = "none", axis.ticks = element_blank(), axis.text = element_blank(), axis.title=element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank())

#add state borders
map <- map + geom_path(data = mapstates, colour = "white", size = .5)

map

#ggplot(mapstates, aes(long,lat,group=group)) + geom_path() + coord_map(project="globular")
