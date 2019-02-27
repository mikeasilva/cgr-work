library(dplyr)
library(openxlsx)
library(tidyr)
library(ggplot2)

get_day <- function(time){
  t <- strsplit(time, "-")
  t <- t[[1]][1]
  switch(t,
         Sun = 7,
         Mon = 6,
         Tue = 5,
         Wed = 4,
         Thu = 3,
         Fri = 2,
         Sat = 1)
}

get_hour <- function(time){
  t <- strsplit(time, "-")
  t <- t[[1]][2]
  switch(t,
         "12AM" = "00",
         "1AM" = "01",
         "2AM" = "02",
         "3AM" = "03",
         "4AM" = "04",
         "5AM" = "05",
         "6AM" = "06",
         "7AM" = "07",
         "8AM" = "08",
         "9AM" = "09",
         "10AM" = "10",
         "11AM" = "11",
         "12PM" = "12",
         "1PM" = "13",
         "2PM" = "14",
         "3PM" = "15",
         "4PM" = "16",
         "5PM" = "17",
         "6PM" = "18",
         "7PM" = "19",
         "8PM" = "20",
         "9PM" = "21",
         "10PM" = "22",
         "11PM" = "23")

}

get_heatmap <- function(data){
  ggplot(data, aes(hour, day, fill=(-1*open))) +
    geom_tile(colour="white",size=0.25) +
    coord_fixed() +
    scale_fill_distiller(palette = "Spectral") +
    geom_text(aes(label=open)) +
    guides(fill=FALSE) +
    #labs(x="",y="") +
    scale_y_discrete(expand=c(0,0))+
    scale_x_discrete(expand=c(0,0))+
    theme_grey(base_size=0)+
    theme(
      plot.background=element_blank(),
      panel.border=element_blank(),
      axis.text=element_text(face="bold"),
      axis.ticks=element_line(size=0.4),
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      axis.title.x=element_blank(),
      axis.text.x=element_blank(),
      axis.ticks.x=element_blank(),
      axis.title.y=element_blank(),
      axis.text.y=element_blank(),
      axis.ticks.y=element_blank()
    )

}

df <- read.xlsx('G:/2018 Projects/813-Walmart-NW AR Food Insecurity Study/Maps/Data for Map.xlsx', 'hrs') %>%
  mutate(id = 1:n())



times <- df %>%
  select(-Latitude, -Longitude, -Type.of.Organization, -Category, -Hours.Verified, -Brokeout, -Consistent.Weekly, -Hours.of.Operation, -Always.Open) %>%
  gather("time","open", -id) %>%
  rowwise() %>%
  mutate(day = as.vector(as.character(get_day(time)))) %>%
  mutate(hour = get_hour(time))

orgs <- df %>%
  select(id, Latitude, Longitude, Type.of.Organization, Category, Hours.Verified, Brokeout, Consistent.Weekly, Always.Open) %>%
  merge(times)

orgs %>%
  filter(Consistent.Weekly==1) %>%
  group_by(day, hour) %>%
  summarise(open = sum(open)) %>%
  ungroup() %>%
  get_heatmap()

orgs %>%
  filter(Consistent.Weekly==1) %>%
  filter(Hours.Verified=="Yes") %>%
  group_by(day, hour) %>%
  summarise(open = sum(open)) %>%
  ungroup() %>%
  get_heatmap()


orgs %>%
  filter(Consistent.Weekly==1) %>%
  filter(Category == "Food Pantry") %>%
  filter(Hours.Verified=="Yes") %>%
  group_by(day, hour) %>%
  summarise(open = sum(open)) %>%
  ungroup() %>%
  get_heatmap()

orgs %>%
  filter(Consistent.Weekly==1) %>%
  filter(Category == "Delivery") %>%
  filter(Hours.Verified=="Yes") %>%
  group_by(day, hour) %>%
  summarise(open = sum(open)) %>%
  ungroup() %>%
  get_heatmap()

orgs %>%
  filter(Consistent.Weekly==1) %>%
  filter(Category == "Meals") %>%
  filter(Hours.Verified=="Yes") %>%
  group_by(day, hour) %>%
  summarise(open = sum(open)) %>%
  ungroup() %>%
  get_heatmap()
