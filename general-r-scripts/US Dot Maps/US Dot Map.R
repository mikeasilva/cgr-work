library(maps)
library(ggplot2)

m <- map('state')

step <- 1/2

plot.data <- data.frame(x=numeric(), y=numeric())
for(y in seq(m$range[3], m$range[4], step)){
  for(x in seq(m$range[1], m$range[2], step)){
    if(!is.na(map.where('state', x, y))){
      plot.data <- rbind(plot.data, data.frame(x,y))
    }
  }
}

ggplot(plot.data, aes(x,y)) +
  geom_point() + 
  theme(axis.line=element_blank(),axis.text.x=element_blank(),
                                          axis.text.y=element_blank(),axis.ticks=element_blank(),
                                          axis.title.x=element_blank(),
                                          axis.title.y=element_blank(),legend.position="none",
                                          panel.background=element_blank(),panel.border=element_blank(),panel.grid.major=element_blank(),
                                          panel.grid.minor=element_blank(),plot.background=element_blank()) +
  coord_map()
