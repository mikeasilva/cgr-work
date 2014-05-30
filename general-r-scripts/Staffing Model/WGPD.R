###############################################################################
# WGPD Model Assumptions
###############################################################################
if(!exists("retirement")){
  retirement <- 25 # Years of service when police retire
}

if(!exists("projection.years")){
  projection.years <- 15  # How far out do we want to project
}
health.insurance.avg.premium <- 32472.76
other.insurance.avg.premium <- 0

base.pay.inflation.factor <- 1.03  # Average change in salary schedule
clothing.allowance.inflation.factor <- 1.03  # Ditto (for now)

if(!exists("health.insurance.inflation.factor.low")){
  health.insurance.inflation.factor.low <- 1.00608391608392
  health.insurance.inflation.factor.mid <- 1.05332482830292
  health.insurance.inflation.factor.high <- 1.11878081519636
  other.insurance.inflation.factor <- 1.03612290461971
}

leave.time.in.hours <- c(40,32,80,160)  # Number of hours of leave time
additional.personal.time <- 8
additional.personal.time.threshold <- 10
names(leave.time.in.hours) <- c("berevement", "personal", "holidays", "sick")

get.total.leave.time <- function(years.of.service){
  if(years.of.service <= additional.personal.time.threshold)
    total.leave.time <- sum(leave.time.in.hours)
  else{
    total.leave.time <- sum(leave.time.in.hours) + ((years.of.service - additional.personal.time.threshold) * additional.personal.time)
  }
  return(total.leave.time)
}

get.base.pay <- function(position, years.of.service){
  if(position == "sergeant" || position == "sergeant.detective")
    salary <- 95768
  else{
    if(years.of.service > 3){
      salary <- 87861
    }      
    else if(years.of.service == 3){
      salary <- 84461
    }
    else if(years.of.service == 2){
      salary <- 82026
    }
    else {
      salary <- 50000
    }
  }
  if(position == "detective" || position == "sergeant.detective" || position == "police.officer.traffic")
    salary <- salary + 1800
  return(salary)
}

get.longevity.pay.rate <- function(years.of.service){
  if(years.of.service >= 21)
    return(0.06)
  if(years.of.service >= 16)
    return(0.05)
  if(years.of.service >= 11)
    return(0.035)
  if(years.of.service >= 6)
    return(0.025)
  else
    return(0)
}

get.clothing.allowance <- function(position){
  clothing.allowance <- 1000
  if(position == "detective" || position == "sergeant.detective"){
    clothing.allowance <- clothing.allowance + 600
  }
  return(clothing.allowance)
}


###############################################################################
# Begin Building Lookup Tables
###############################################################################

# Begin building base pay projections
base.pay <- data.frame(position = c(
  rep("police.officer",retirement), 
  rep("police.officer.traffic",retirement), 
  rep("detective",retirement), 
  rep("sergeant",retirement), 
  rep("sergeant.detective",retirement)
),
years.of.service=c(
  0:(retirement-1),
  0:(retirement-1), 
  0:(retirement-1), 
  0:(retirement-1), 
  0:(retirement-1)
)
)

# Quickly create other data frames after the base pay pattern
clothing.allowance <- base.pay
other.insurance <- base.pay
health.insurance.low <- base.pay
health.insurance.mid <- base.pay
health.insurance.high <- base.pay

###############################################################################
# Project Cost Adjusting for Inflation
###############################################################################

# Using the get.base.pay function to get the year 1 base pay
base.pay$year.1 <- apply(base.pay, 1, function(x) get.base.pay(x[1], as.numeric(x[2])))
# Adjusting the year 1 base pay by the inflation factor assumption
for(i in 2:projection.years){
  base.pay[i+2] <- base.pay[i+1] * base.pay.inflation.factor
  names(base.pay)[i+2] <- paste0("year.",i)
}

# Clothing Allowance
clothing.allowance$year.1 <- apply(clothing.allowance, 1, function(x) get.clothing.allowance(x[1]))
# Adjusting the year 1 clothing allowance by the inflation factor assumption
for(i in 2:projection.years){
  clothing.allowance[i+2] <- clothing.allowance[i+1] * clothing.allowance.inflation.factor
}

# Other Insurance
other.insurance$year.1 <- other.insurance.avg.premium
# Adjusting the year 1 other insurance by the inflation factor assumption
for(i in 2:projection.years){
  other.insurance[i+2] <- other.insurance[i+1] * other.insurance.inflation.factor
}

# Health Insurance
health.insurance.low$year.1 <- health.insurance.avg.premium
health.insurance.mid$year.1 <- health.insurance.avg.premium
health.insurance.high$year.1 <- health.insurance.avg.premium
# Adjusting the year 1 health insurance by the inflation factor assumptions
for(i in 2:projection.years){
  health.insurance.low[i+2] <- health.insurance.low[i+1] * health.insurance.inflation.factor.low
  health.insurance.mid[i+2] <- health.insurance.mid[i+1] * health.insurance.inflation.factor.mid
  health.insurance.high[i+2] <- health.insurance.high[i+1] * health.insurance.inflation.factor.high
}

# Clean up the column names
names(clothing.allowance) <- names(base.pay)
names(other.insurance) <- names(base.pay)
names(health.insurance.low) <- names(base.pay)
names(health.insurance.mid) <- names(base.pay)
names(health.insurance.high) <- names(base.pay)

###############################################################################
# Aggregate Costs
###############################################################################

longevity.pay.rates <- apply(base.pay, 1, function(x) get.longevity.pay.rate(as.numeric(x[2])))
longevity.pay <- base.pay[,3:length(base.pay)] * longevity.pay.rates

base.pay.plus.longevity <- base.pay[,1:2]
base.pay.plus.longevity <- cbind(base.pay.plus.longevity, longevity.pay + base.pay[,3:length(base.pay)])

wage.rate <- base.pay[,1:2]
wage.rate <- cbind(wage.rate, base.pay.plus.longevity[,3:length(base.pay.plus.longevity)]/2080)

leave.time <- base.pay[,1:2]
total.leave.time <- base.pay[,1:2]
total.leave.time$hours <- apply(total.leave.time, 1, function(x) get.total.leave.time(as.numeric(x[2])))

leave.time <- cbind(leave.time, wage.rate[,3:length(wage.rate)] * total.leave.time[,3])

total.costs <- base.pay[,1:2]
total.costs.low <- cbind(total.costs,
                         base.pay[,3:length(base.pay)] + 
                           longevity.pay + 
                           clothing.allowance[,3:length(clothing.allowance)] +
                           other.insurance[,3:length(other.insurance)] +
                           health.insurance.low[,3:length(health.insurance.low)] +
                           leave.time[,3:length(leave.time)]
)
total.costs.mid <- cbind(total.costs,
                         base.pay[,3:length(base.pay)] + 
                           longevity.pay + 
                           clothing.allowance[,3:length(clothing.allowance)] +
                           other.insurance[,3:length(other.insurance)] +
                           health.insurance.mid[,3:length(health.insurance.mid)] +
                           leave.time[,3:length(leave.time)]
)
total.costs.high <- cbind(total.costs,
                          base.pay[,3:length(base.pay)] + 
                            longevity.pay + 
                            clothing.allowance[,3:length(clothing.allowance)] +
                            other.insurance[,3:length(other.insurance)] +
                            health.insurance.high[,3:length(health.insurance.high)] +
                            leave.time[,3:length(leave.time)]
)
rm(total.costs)

# If leave.no.trace is true, remove stuff from the environment
if(exists("leave.no.trace") && leave.no.trace){
  # Data
  rm(base.pay)
  rm(base.pay.plus.longevity)
  rm(clothing.allowance)
  rm(health.insurance.low)
  rm(health.insurance.mid)
  rm(health.insurance.high)
  rm(leave.time)
  rm(longevity.pay)
  rm(other.insurance)
  rm(total.leave.time)
  rm(wage.rate)
  # Values
  rm(additional.personal.time)
  rm(additional.personal.time.threshold)
  rm(base.pay.inflation.factor)
  rm(clothing.allowance.inflation.factor)
  rm(health.insurance.avg.premium)
  rm(i)
  rm(leave.time.in.hours)
  rm(longevity.pay.rates)
  rm(other.insurance.avg.premium)
  # Functions
  rm(get.base.pay)
  rm(get.clothing.allowance)
  rm(get.longevity.pay.rate)
  rm(get.total.leave.time)
}