###############################################################################
# Model Assumptions
###############################################################################
health.insurance.inflation.factor.low <- 1.00608391608392  # 10th Percentile
health.insurance.inflation.factor.mid <- 1.05332482830292  # Median
health.insurance.inflation.factor.high <- 1.11878081519636 # 90th Percentile
other.insurance.inflation.factor <- 1.03612290461971  # Mean

base.year <- 2014
project.to <- 2029

projection.years <- project.to - base.year + 1  # How far out do we want to project
retirement <- 25  # Years of service when police retire

leave.no.trace <- TRUE  # Should we clean up the environment after?



###############################################################################
# Get Costs by position, years of service, and calendar year
###############################################################################
source('~/GitHub/cgr-work/general-r-scripts/Staffing Model/WEGO.R')
wego.high <- total.costs.high
wego.mid <- total.costs.mid
wego.low <- total.costs.low
source('~/GitHub/cgr-work/general-r-scripts/Staffing Model/WGPD.R')
wgpd.high <- total.costs.high
wgpd.mid <- total.costs.mid
wgpd.low <- total.costs.low

if(leave.no.trace){
  rm(total.costs.low)
  rm(total.costs.mid)
  rm(total.costs.high)
  rm(health.insurance.inflation.factor.low)
  rm(health.insurance.inflation.factor.mid)
  rm(health.insurance.inflation.factor.high)
  rm(other.insurance.inflation.factor)
}

###############################################################################
# Initialize positions and years of experience data frames
###############################################################################

source('~/GitHub/cgr-work/general-r-scripts/Staffing Model/Staffing Model Functions.R')
# Read in the police force data
police.force <- read.csv("G:/2014 Projects/412-East Goshen and WEGO Police Consolidation/data analysis/police.force.csv", stringsAsFactors = FALSE)
police.force$id <- as.numeric(police.force$id)

# Subset for police departments - Used for Status Quo Model
wego <- police.force[police.force$department == "WEGO",]
wgpd <- police.force[police.force$department == "WGPD",]

# Create Positions data frame
positions <- initialize.positions(police.force)
wego.positions <- initialize.positions(wego)
wgpd.positions <- initialize.positions(wgpd)

# Create Years of Experience data frame
years.of.experience <- get.years.of.experience(police.force)
wego.years.of.experience <- get.years.of.experience(wego)
wgpd.years.of.experience <- get.years.of.experience(wgpd)

###############################################################################
# Model changes to the police force
###############################################################################

# Size of Force parameter
force.size <- nrow(positions)
wego.force.size <- nrow(wego)
wgpd.force.size <- nrow(wgpd)
plus.5 <- force.size + 5
minus.12 <- force.size - 12
plus.7 <- force.size + 7
minus.11 <- force.size - 11
# Model retirement replacement
retirement.threshold <- retirement

temp.plus.5 <- retire(positions, years.of.experience, retirement.threshold, plus.5)
positions.plus.5 <- temp.plus.5$positions
years.of.experience.plus.5 <- temp.plus.5$years.of.experience

temp.minus.12 <- retire(positions, years.of.experience, retirement.threshold, minus.12)
positions.minus.12 <- temp.minus.12$positions
years.of.experience.minus.12 <- temp.minus.12$years.of.experience

temp <- retire(positions, years.of.experience, retirement.threshold, plus.7)
positions.plus.7 <- temp$positions
years.of.experience.plus.7 <- temp$years.of.experience

temp <- retire(positions, years.of.experience, retirement.threshold, minus.11)
positions.minus.11 <- temp$positions
years.of.experience.minus.11 <- temp$years.of.experience

temp <- retire(positions, years.of.experience, retirement.threshold, force.size)
positions <- temp$positions
years.of.experience <- temp$years.of.experience

temp <- retire(wego.positions, wego.years.of.experience, retirement.threshold, wego.force.size)
wego.positions <- temp$positions
wego.years.of.experience <- temp$years.of.experience

temp <- retire(wgpd.positions, wgpd.years.of.experience, retirement.threshold, wgpd.force.size)
wgpd.positions <- temp$positions
wgpd.years.of.experience <- temp$years.of.experience

if(leave.no.trace){
  # Remove Data
  rm(police.force)
  rm(retirement)
  rm(retirement.threshold)
  rm(temp)
  rm(temp.plus.5)
  rm(temp.minus.12)
  rm(temp.plus.7)
  rm(temp.minus.11)
  rm(projection.years)
  # Remove Value
  rm(force.size)
  # Remove Functions
  rm(add.staff)
  rm(fix.years.of.experience)
  rm(get.years.of.experience)
  rm(initialize.positions)
  rm(replace.staff)
  rm(retire)
  rm(sort.positions.to.replace)
}

###############################################################################
# Now that we have modled the positions and years of experience of the police 
# force, let's estimate the costs
###############################################################################

wego.status.quo.low.total.costs <- get.total.cost.table(wego.positions, wego.years.of.experience, wego.low)
wego.status.quo.mid.total.costs <- get.total.cost.table(wego.positions, wego.years.of.experience, wego.mid)
wego.status.quo.high.total.costs <- get.total.cost.table(wego.positions, wego.years.of.experience, wego.high)

wgpd.status.quo.low.total.costs <- get.total.cost.table(wgpd.positions, wgpd.years.of.experience, wgpd.low)
wgpd.status.quo.mid.total.costs <- get.total.cost.table(wgpd.positions, wgpd.years.of.experience, wgpd.mid)
wgpd.status.quo.high.total.costs <- get.total.cost.table(wgpd.positions, wgpd.years.of.experience, wgpd.high)

status.quo.low.total.costs <- rbind(wego.status.quo.low.total.costs, wgpd.status.quo.low.total.costs)
status.quo.mid.total.costs <- rbind(wego.status.quo.mid.total.costs, wgpd.status.quo.mid.total.costs)
status.quo.high.total.costs <- rbind(wego.status.quo.high.total.costs, wgpd.status.quo.high.total.costs)

wego.plus.5.low.total.costs <- get.total.cost.table(positions.plus.5, years.of.experience.plus.5, wego.low)
wego.plus.5.mid.total.costs <- get.total.cost.table(positions.plus.5, years.of.experience.plus.5, wego.mid)
wego.plus.5.high.total.costs <- get.total.cost.table(positions.plus.5, years.of.experience.plus.5, wego.high)

wgpd.plus.5.low.total.costs <- get.total.cost.table(positions.plus.5, years.of.experience.plus.5, wgpd.low)
wgpd.plus.5.mid.total.costs <- get.total.cost.table(positions.plus.5, years.of.experience.plus.5, wgpd.mid)
wgpd.plus.5.high.total.costs <- get.total.cost.table(positions.plus.5, years.of.experience.plus.5, wgpd.high)

wego.minus.12.low.total.costs <- get.total.cost.table(positions.minus.12, years.of.experience.minus.12, wego.low)
wego.minus.12.mid.total.costs <- get.total.cost.table(positions.minus.12, years.of.experience.minus.12, wego.mid)
wego.minus.12.high.total.costs <- get.total.cost.table(positions.minus.12, years.of.experience.minus.12, wego.high)

wgpd.minus.12.low.total.costs <- get.total.cost.table(positions.minus.12, years.of.experience.minus.12, wgpd.low)
wgpd.minus.12.mid.total.costs <- get.total.cost.table(positions.minus.12, years.of.experience.minus.12, wgpd.mid)
wgpd.minus.12.high.total.costs <- get.total.cost.table(positions.minus.12, years.of.experience.minus.12, wgpd.high)

wego.plus.7.low.total.costs <- get.total.cost.table(positions.plus.7, years.of.experience.plus.7, wego.low)
wego.plus.7.mid.total.costs <- get.total.cost.table(positions.plus.7, years.of.experience.plus.7, wego.mid)
wego.plus.7.high.total.costs <- get.total.cost.table(positions.plus.7, years.of.experience.plus.7, wego.high)

wgpd.plus.7.low.total.costs <- get.total.cost.table(positions.plus.7, years.of.experience.plus.7, wgpd.low)
wgpd.plus.7.mid.total.costs <- get.total.cost.table(positions.plus.7, years.of.experience.plus.7, wgpd.mid)
wgpd.plus.7.high.total.costs <- get.total.cost.table(positions.plus.7, years.of.experience.plus.7, wgpd.high)

wego.minus.11.low.total.costs <- get.total.cost.table(positions.minus.11, years.of.experience.minus.11, wego.low)
wego.minus.11.mid.total.costs <- get.total.cost.table(positions.minus.11, years.of.experience.minus.11, wego.mid)
wego.minus.11.high.total.costs <- get.total.cost.table(positions.minus.11, years.of.experience.minus.11, wego.high)

wgpd.minus.11.low.total.costs <- get.total.cost.table(positions.minus.11, years.of.experience.minus.11, wgpd.low)
wgpd.minus.11.mid.total.costs <- get.total.cost.table(positions.minus.11, years.of.experience.minus.11, wgpd.mid)
wgpd.minus.11.high.total.costs <- get.total.cost.table(positions.minus.11, years.of.experience.minus.11, wgpd.high)

wgpd.low.total.costs <- get.total.cost.table(positions, years.of.experience, wgpd.low)
wgpd.mid.total.costs <- get.total.cost.table(positions, years.of.experience, wgpd.mid)
wgpd.high.total.costs <- get.total.cost.table(positions, years.of.experience, wgpd.high)

wego.low.total.costs <- get.total.cost.table(positions, years.of.experience, wego.low)
wego.mid.total.costs <- get.total.cost.table(positions, years.of.experience, wego.mid)
wego.high.total.costs <- get.total.cost.table(positions, years.of.experience, wego.high)

if(leave.no.trace){
  # Remove data
  rm(positions)
  rm(wego)
  rm(wego.high)
  rm(wego.low)
  rm(wego.mid)
  rm(wego.positions)
  rm(wego.years.of.experience)
  rm(wgpd)
  rm(wgpd.high)
  rm(wgpd.mid)
  rm(wgpd.low)
  rm(wgpd.positions)
  rm(wgpd.years.of.experience)
  rm(years.of.experience)
  # Remove Values
  rm(wego.force.size)
  rm(wgpd.force.size)
  # Remove Functions
  rm(get.cost)
  rm(get.total.cost.table) 
}

###############################################################################
# Summarizing the data
###############################################################################

status.quo <- get.cost.summaries(status.quo.low.total.costs, 
                                 status.quo.mid.total.costs,
                                 status.quo.high.total.costs)

wego.status.quo <- get.cost.summaries(wego.status.quo.low.total.costs,
                                      wego.status.quo.mid.total.costs,
                                      wego.status.quo.high.total.costs)

wgpd.status.quo <- get.cost.summaries(wgpd.status.quo.low.total.costs,
                                      wgpd.status.quo.mid.total.costs,
                                      wgpd.status.quo.high.total.costs)

wego.contract <- get.cost.summaries(wego.low.total.costs,
                                    wego.mid.total.costs,
                                    wego.high.total.costs)

wgpd.contract <- get.cost.summaries(wgpd.low.total.costs,
                                    wgpd.mid.total.costs,
                                    wgpd.high.total.costs)

wego.plus.5.contract <- get.cost.summaries(wego.plus.5.low.total.costs,
                                           wego.plus.5.mid.total.costs,
                                           wego.plus.5.high.total.costs)

wgpd.plus.5.contract <- get.cost.summaries(wgpd.plus.5.low.total.costs,
                                           wgpd.plus.5.mid.total.costs,
                                           wgpd.plus.5.high.total.costs)

wego.minus.12.contract <- get.cost.summaries(wego.minus.12.low.total.costs,
                                             wego.minus.12.mid.total.costs,
                                             wego.minus.12.high.total.costs)

wgpd.minus.12.contract <- get.cost.summaries(wgpd.minus.12.low.total.costs,
                                             wgpd.minus.12.mid.total.costs,
                                             wgpd.minus.12.high.total.costs)

wego.plus.7.contract <- get.cost.summaries(wego.plus.7.low.total.costs,
                                           wego.plus.7.mid.total.costs,
                                           wego.plus.7.high.total.costs)

wgpd.plus.7.contract <- get.cost.summaries(wgpd.plus.7.low.total.costs,
                                           wgpd.plus.7.mid.total.costs,
                                           wgpd.plus.7.high.total.costs)

wego.minus.11.contract <- get.cost.summaries(wego.minus.11.low.total.costs,
                                             wego.minus.11.mid.total.costs,
                                             wego.minus.11.high.total.costs)

wgpd.minus.11.contract <- get.cost.summaries(wgpd.minus.11.low.total.costs,
                                             wgpd.minus.11.mid.total.costs,
                                             wgpd.minus.11.high.total.costs)
###############################################################################
# Drawing and Saving Line Charts
###############################################################################

x <- base.year:(base.year + ncol(status.quo) - 1)

library(reshape2)
library(ggplot2)

status.quo.plot <- get.line.chart(status.quo, x, "Department Cost Combined")
wego.status.quo.plot <- get.line.chart(wego.status.quo, x, "Department Cost - WEGO")
wgpd.status.quo.plot <- get.line.chart(wgpd.status.quo, x, "Department Cost - WGPD")

wego.contract.plot <- get.line.chart(wego.contract, x, "47 Person Police Force - WEGO Contract")
wgpd.contract.plot <- get.line.chart(wgpd.contract, x, "47 Person Police Force - WGPD Contract")
wego.plus.5.contract.plot <- get.line.chart(wego.plus.5.contract, x, "52 Person Police Force - WEGO Contract")
wgpd.plus.5.contract.plot <- get.line.chart(wgpd.plus.5.contract, x, "52 Person Police Force  - WGPD Contract")
wego.minus.12.contract.plot <- get.line.chart(wego.minus.12.contract, x, "35 Person Police Force - WEGO Contract")
wgpd.minus.12.contract.plot <- get.line.chart(wgpd.minus.12.contract, x, "35 Person Police Force  - WGPD Contract")
wego.plus.7.contract.plot <- get.line.chart(wego.plus.7.contract, x, "54 Person Police Force - WEGO Contract")
wgpd.plus.7.contract.plot <- get.line.chart(wgpd.plus.7.contract, x, "54 Person Police Force  - WGPD Contract")
wego.minus.11.contract.plot <- get.line.chart(wego.minus.11.contract, x, "36 Person Police Force - WEGO Contract")
wgpd.minus.11.contract.plot <- get.line.chart(wgpd.minus.11.contract, x, "36 Person Police Force  - WGPD Contract")

path <- "G:/2014 Projects/412-East Goshen and WEGO Police Consolidation/data analysis/cost projections/"

ggsave(filename=paste0(path,"status quo.png"), plot=status.quo.plot)
ggsave(filename=paste0(path,"wego status quo.png"), plot=wego.status.quo.plot)
ggsave(filename=paste0(path,"wgpd status quo.png"), plot=wgpd.status.quo.plot)
ggsave(filename=paste0(path,"47 person wego contract.png"), plot=wego.contract.plot)
ggsave(filename=paste0(path,"47 person wgpd contract.png"), plot=wgpd.contract.plot)
ggsave(filename=paste0(path,"52 person wego contract.png"), plot=wego.plus.5.contract.plot)
ggsave(filename=paste0(path,"52 person wgpd contract.png"), plot=wgpd.plus.5.contract.plot)
ggsave(filename=paste0(path,"35 person wego contract.png"), plot=wego.minus.12.contract.plot)
ggsave(filename=paste0(path,"35 person wgpd contract.png"), plot=wgpd.minus.12.contract.plot)
ggsave(filename=paste0(path,"54 person wego contract.png"), plot=wego.plus.7.contract.plot)
ggsave(filename=paste0(path,"54 person wgpd contract.png"), plot=wgpd.plus.7.contract.plot)
ggsave(filename=paste0(path,"36 person wego contract.png"), plot=wego.minus.11.contract.plot)
ggsave(filename=paste0(path,"36 person wgpd contract.png"), plot=wgpd.minus.11.contract.plot)

###############################################################################
# Export data to XLSX file
###############################################################################
library(xlsx)
  
wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="status.quo")
addDataFrame(status.quo, sheet)  
saveWorkbook(wb, paste0(path,"status quo.xlsx"))

wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="wego.status.quo")
addDataFrame(wego.status.quo, sheet)  
saveWorkbook(wb, paste0(path,"wego status quo.xlsx"))

wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="wgpd.status.quo")
addDataFrame(wgpd.status.quo, sheet)  
saveWorkbook(wb, paste0(path,"wgpd status quo.xlsx"))
             
wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="47.wego.contract")
addDataFrame(wego.contract, sheet)
saveWorkbook(wb, paste0(path,"47 person wego contract.xlsx"))

wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="47.wgpd.contract")
addDataFrame(wgpd.contract, sheet)
saveWorkbook(wb, paste0(path,"47 person wgpd contract.xlsx"))
             
wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="52.wego.contract")
addDataFrame(wego.plus.5.contract, sheet)
saveWorkbook(wb, paste0(path,"52 person wego contract.xlsx"))
             
wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="52.wgpd.contract")
addDataFrame(wgpd.plus.5.contract, sheet)
saveWorkbook(wb, paste0(path,"52 person wgpd contract.xlsx"))
               
wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="35.wego.contract")
addDataFrame(wego.minus.12.contract, sheet)
saveWorkbook(wb, paste0(path,"35 person wego contract.xlsx"))
               
wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="35.wgpd.contract")
addDataFrame(wgpd.minus.12.contract, sheet)
saveWorkbook(wb, paste0(path,"35 person wgpd contract.xlsx"))

wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="54.wego.contract")
addDataFrame(wego.plus.7.contract, sheet)
saveWorkbook(wb, paste0(path,"54 person wego contract.xlsx"))

wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="54.wgpd.contract")
addDataFrame(wgpd.plus.7.contract, sheet)
saveWorkbook(wb, paste0(path,"54 person wgpd contract.xlsx"))

wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="36.wego.contract")
addDataFrame(wego.minus.11.contract, sheet)
saveWorkbook(wb, paste0(path,"36 person wego contract.xlsx"))

wb <- createWorkbook()
sheet <- createSheet(wb, sheetName="36.wgpd.contract")
addDataFrame(wgpd.minus.11.contract, sheet)
saveWorkbook(wb, paste0(path,"36 person wgpd contract.xlsx"))