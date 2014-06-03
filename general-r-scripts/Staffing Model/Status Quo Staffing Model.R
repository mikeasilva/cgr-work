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

# Subset for police departments
wego <- police.force[police.force$department == "WEGO",]
wgpd <- police.force[police.force$department == "WGPD",]

# Create Positions
positions <- initialize.positions(police.force)
wego.positions <- initialize.positions(wego)
wgpd.positions <- initialize.positions(wgpd)

# Create Years of Experience
years.of.experience <- get.years.of.experience(police.force)
wego.years.of.experience <- get.years.of.experience(wego)
wgpd.years.of.experience <- get.years.of.experience(wgpd)

# Size of Force
force.size <- nrow(positions)
wego.force.size <- nrow(wego)
wgpd.force.size <- nrow(wgpd)

retirement.threshold <- retirement

# Model retirement replacement
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

wego.low.total.costs <- get.total.cost.table(positions, years.of.experience, wego.low)
wego.mid.total.costs <- get.total.cost.table(positions, years.of.experience, wego.mid)
wego.high.total.costs <- get.total.cost.table(positions, years.of.experience, wego.high)

wgpd.low.total.costs <- get.total.cost.table(positions, years.of.experience, wgpd.low)
wgpd.mid.total.costs <- get.total.cost.table(positions, years.of.experience, wgpd.mid)
wgpd.high.total.costs <- get.total.cost.table(positions, years.of.experience, wgpd.high)

wego.status.quo.low.total.costs <- get.total.cost.table(wego.positions, wego.years.of.experience, wego.low)
wego.status.quo.mid.total.costs <- get.total.cost.table(wego.positions, wego.years.of.experience, wego.mid)
wego.status.quo.high.total.costs <- get.total.cost.table(wego.positions, wego.years.of.experience, wego.high)

wgpd.status.quo.low.total.costs <- get.total.cost.table(wgpd.positions, wgpd.years.of.experience, wgpd.low)
wgpd.status.quo.mid.total.costs <- get.total.cost.table(wgpd.positions, wgpd.years.of.experience, wgpd.mid)
wgpd.status.quo.high.total.costs <- get.total.cost.table(wgpd.positions, wgpd.years.of.experience, wgpd.high)

status.quo.low.total.costs <- rbind(wego.status.quo.low.total.costs, wgpd.status.quo.low.total.costs)
status.quo.mid.total.costs <- rbind(wego.status.quo.mid.total.costs, wgpd.status.quo.mid.total.costs)
status.quo.high.total.costs <- rbind(wego.status.quo.high.total.costs, wgpd.status.quo.high.total.costs)

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

status.quo <- get.cost.summaries(status.quo.low.total.costs, 
                                 status.quo.mid.total.costs,
                                 status.quo.high.total.costs)

wego.contract <- get.cost.summaries(wego.low.total.costs,
                                    wego.mid.total.costs,
                                    wego.high.total.costs)

wgpd.contract <- get.cost.summaries(wgpd.low.total.costs,
                                    wgpd.mid.total.costs,
                                    wgpd.high.total.costs)
x <- base.year:(base.year + ncol(status.quo) - 1)

get.line.chart(status.quo, x, "Status Quo Model")
get.line.chart(wego.contract, x, "Combined Police Force - WEGO Contract")
get.line.chart(wgpd.contract, x, "Combined Police Force - WGPD Contract")