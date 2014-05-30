###############################################################################
# Model Assumptions
###############################################################################
health.insurance.inflation.factor.low <- 1.00608391608392
health.insurance.inflation.factor.mid <- 1.05332482830292
health.insurance.inflation.factor.high <- 1.11878081519636
other.insurance.inflation.factor <- 1.03612290461971

projection.years <- 15  # How far out do we want to project
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

source('~/GitHub/cgr-work/general-r-scripts/Staffing Model/Staffing Model Functions.R')
# Read in the police force data
police.force <- read.csv("G:/2014 Projects/412-East Goshen and WEGO Police Consolidation/data analysis/police.force.csv", stringsAsFactors = FALSE)
police.force$id <- as.numeric(police.force$id)

positions <- initialize.positions(police.force)
years.of.experience <- get.years.of.experience(police.force)
force.size <- nrow(positions)
temp <- retire(positions, years.of.experience, retirement, force.size)

positions <- temp$positions
years.of.experience <- temp$years.of.experience

if(leave.no.trace)
  rm(temp)
