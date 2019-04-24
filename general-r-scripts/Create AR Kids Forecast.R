library(dplyr)
library(tibble)
library(fpp2)
library(openxlsx)

#clear
rm(list = ls())

file <- "Bridged-Race Population Estimates 1990-2017.txt"


get_age_group <- function(x){
  if(x %in% c("0", "1", "2")){return("Under 3")}
  if(x %in% c("3","4")){return("3 or 4")}
  return("Drop")
}

get_forecast <- function(df, start_year, a, cc){
  forecast <- df %>%
    filter(age_group == a) %>%
    select(population) %>%
    ts(., start = start_year, frequency = 1) %>%
    holt(., h = 2) %>%
    summary() %>%
    rename(population = "Point Forecast") %>%
    rownames_to_column("year") %>%
    mutate(County.Code = cc,
           year = as.numeric(year),
           age_group = a) %>%
    select(County.Code, age_group, population, year)
  return(forecast)
}

df <- read.delim(file, colClasses=c("character"), stringsAsFactors = FALSE) %>%
  rowwise() %>%
  mutate(age_group = get_age_group(Age.Code),
         population = as.numeric(Population),
         year = as.numeric(Yearly.July.1st.Estimates)) %>%
  filter(age_group != "Drop") %>%
  ungroup() %>%
  group_by(County.Code, age_group, year) %>%
  summarise(population = sum(population)) %>%
  ungroup()

for(cc in unique(df$County.Code)){
  print(cc)
  temp <- df %>%
    filter(County.Code == cc)
  
  start_year <- min(df$year)
  
  forecast1 <- get_forecast(temp, start_year, "Under 3", cc)
  forecast2 <- get_forecast(temp, start_year, "3 or 4", cc)
  
  temp <- temp %>%
    select(County.Code, age_group, population, year) %>%
    bind_rows(forecast1) %>%
    bind_rows(forecast2)
  
  if(exists("final.df")){
    final.df <- bind_rows(final.df, temp)
  } else {
    final.df <- temp
  }
}

final.df %>%
  arrange(County.Code, age_group, year) %>%
  write.xlsx(., "AR Kids Forecast.xlsx")