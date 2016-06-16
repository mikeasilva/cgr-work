library(dplyr)

# Function to handle reading in SAHIE CSV files
read.sahie.csv <- function(file.name){
  message(paste('Working on',file.name))
  csv <- read.csv(file.name, skip=78, nrows = 10)
  read.csv(file.name, skip=78, na.strings='N/A', stringsAsFactors=FALSE, colClasses=rep('character',ncol(csv)))
}

# Change the working directory to where the CSV files are found
setwd('H:/Data Warehouse/Census Bureau/SAHIE (Insurance)/CSVs/')

# Read in the SAHIE CSVs appending them to the previous one, 
# change the variable types then write it out as a CSV
df <- lapply(dir(),read.sahie.csv) %>%
  do.call('rbind', .) %>%
  mutate(year = as.numeric(year)) %>%
  mutate(NIPR = as.numeric(NIPR)) %>%
  mutate(nipr_moe = as.numeric(nipr_moe)) %>%
  mutate(NUI = as.numeric(NUI)) %>%
  mutate(nui_moe = as.numeric(nui_moe)) %>%
  mutate(NIC = as.numeric(NIC)) %>%
  mutate(nic_moe = as.numeric(nic_moe)) %>%
  mutate(PCTUI = as.numeric(PCTUI)) %>%
  mutate(pctui_moe = as.numeric(pctui_moe)) %>%
  mutate(PCTIC = as.numeric(PCTIC)) %>%
  mutate(pctic_moe = as.numeric(pctic_moe)) %>%
  mutate(PCTELIG = as.numeric(PCTELIG)) %>%
  mutate(pctelig_moe = as.numeric(pctelig_moe)) %>%
  mutate(PCTLIIC = as.numeric(PCTLIIC)) %>%
  mutate(pctliic_moe = as.numeric(pctliic_moe))

setwd('../')
write.csv(df, 'Census_SAHIE_Data_UPDATE.csv', row.names=FALSE)
