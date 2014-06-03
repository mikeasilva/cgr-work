###############################################################################
# Functions used in the model
###############################################################################

# This function returns a data frame indicating the years of service by id
get.years.of.experience <- function(staff){
  years.of.experience <- staff[c("id", "experience")]
  names(years.of.experience)[2] <- "year.1"
  # Add a year of experience each year
  for(i in 2:projection.years){
    years.of.experience[i+1] <- years.of.experience[i] +1
    names(years.of.experience)[i+1] <- paste0("year.",i)
  }
  years.of.experience
}

# This function initalizes the positions data frame
initialize.positions <- function(staff){
  positions <- staff[c("id", "position")]
  names(positions)[2] <- "year.1"
  # Duplicate the position for all the years  
  for(i in 2:projection.years){
    positions[i+1] <- positions[2]
    names(positions)[i+1] <- paste0("year.",i)
  }
  positions
}

fix.years.of.experience <- function(years.of.experience){
  for(i in 1:ncol(years.of.experience)){
    years.of.experience[,i] <- as.numeric(years.of.experience[,i])
  }
  years.of.experience
}

retire <- function(positions, years.of.experience, retirement.threshold, force.size){
  # Determine when an officer crosses the retirement threshold
  retiring <- years.of.experience == retirement.threshold
  # Adjust the first year for any officers that were over the threshold
  retiring[,2] <- years.of.experience[2] >= retirement.threshold
  retiring[,1] <- FALSE
  
  for(i in 2:ncol(years.of.experience)){
    if(i > 2){
      # Start of this year with the same position as last year
      positions[,i] <- positions[,i-1]
    }
    # Determine which positions have a person retiring
    positions.needing.replacement <- positions[retiring[,i],i]
    #positions.needing.replacement <- as.data.frame(positions[retiring[,i],i])
    positions[retiring[,i],i] <- "retired"
    
    # Determine how many positions need to be replaced
    active.positions <- nrow(as.data.frame(positions[positions[,i] != "retired",i]))
    positions.to.add <- force.size - active.positions
    if(positions.to.add > 0){
      temp <- add.staff(positions.to.add, positions, years.of.experience, i)
      positions <- temp$positions
      years.of.experience <- temp$years.of.experience
    }
    
    # Promote to replace the retired officers
    positions.to.replace <- as.data.frame(table(positions.needing.replacement))
    
    if(nrow(positions.to.replace) > 0){
      positions.to.replace <- sort.positions.to.replace(positions.to.replace)
      positions <- replace.staff(positions, years.of.experience, positions.to.replace, i)
    }
  }
  
  #years.of.experience <- years.of.experience + 1
  list(positions=positions, years.of.experience=years.of.experience)
}

replace.staff <- function(positions, years.of.experience, positions.to.replace, i){
  
  for(k in 1:nrow(positions.to.replace)){
    promote.to <- as.character(positions.to.replace[k,1]) # Position to promote to
    promotion.times <- positions.to.replace[k,2] # How many times you need to find a person
    
    for(l in 1:promotion.times){
      candidate.pool <- list(id = positions[,1], position = positions[,i], years.of.experience = years.of.experience[,i])
      # Rules for replacement
      # Sergeant & Detective & Traffic Cop = police officer with highest years of experience
      # Sergeant Detective = dective with highest years of experience 
      if(promote.to == "sergeant"){
        y <- max(candidate.pool$years.of.experience[(candidate.pool$position == "police.officer" | candidate.pool$position == "police.officer.traffic") & candidate.pool$years.of.experience < retirement.threshold])
        id <- min(candidate.pool$id[(candidate.pool$position == "police.officer" | candidate.pool$position == "police.officer.traffic") & candidate.pool$years.of.experience == y])
      }
      else if(promote.to == "sergeant.detective"){
        y <- max(candidate.pool$years.of.experience[candidate.pool$position == "detective" & candidate.pool$years.of.experience < retirement.threshold])
        id <- min(candidate.pool$id[candidate.pool$position == "detective" & candidate.pool$years.of.experience == y])
      }
      else if(promote.to == "detective"){
        y <- max(candidate.pool$years.of.experience[(candidate.pool$position == "police.officer" | candidate.pool$position == "police.officer.traffic") & candidate.pool$years.of.experience < retirement.threshold])
        id <- min(candidate.pool$id[(candidate.pool$position == "police.officer" | candidate.pool$position == "police.officer.traffic") & candidate.pool$years.of.experience == y])
      }
      else if(promote.to == "police.officer.traffic"){
        y <- max(candidate.pool$years.of.experience[candidate.pool$position == "police.officer" & candidate.pool$years.of.experience < retirement.threshold])
        id <- min(candidate.pool$id[candidate.pool$position == "police.officer" & candidate.pool$years.of.experience == y])
      }
   
      # Get current position
      current.position <- positions[which(positions$id == id), i]
      # Promote the person
      positions[which(positions$id == id), i] <- promote.to
      # Drop the count by 1
      positions.to.replace[k,2] <- positions.to.replace[k,2] - 1
      # Add their position to the list
      if(current.position != "police.officer"){
        # Check to see if it is in the list
        in.list <- positions.to.replace[,1] %in% current.position
        if(nrow(positions.to.replace[in.list,]) > 0){
          # update the positions to replace list
          positions.to.replace[positions.to.replace[,1]==current.position,2] <- positions.to.replace[positions.to.replace[,1]==current.position,2] + 1
        } else{
          # Not in list so add it
          new.row <- data.frame(positions.needing.replacement = current.position, 
                                Freq = 1,
                                sort = 10)
          
          new.row.id <- max(as.numeric(row.names(positions.to.replace))) + 1
          row.names(new.row) <- new.row.id
          names(new.row) <- names(positions.to.replace)
          #positions.to.replace <- unname(positions.to.replace)
          
          positions.to.replace <- rbind(positions.to.replace, new.row)
        }
        # Delete all zero rows
        positions.to.replace <- positions.to.replace[which(positions.to.replace$Freq > 0),]
        # loop back into the function
        data <- replace.staff(positions, years.of.experience, positions.to.replace, i)
        return(data)
      }
    }
  }
  return(positions)
}

add.staff <- function(positions.to.add, positions, years.of.experience, i){
  for(j in 1:positions.to.add){
    # Build the row that will be appended to the data frames
    
    # Get the next number for the id
    new.id <- max(positions$id) + 1
    
    # Determine how many columns are "in the past"
    cols.in.past <- i - 2
    # Only one column is "in the present"
    cols.in.present <- 1
    # Determine how many columns are "in the future"
    cols.in.future <- ncol(years.of.experience) - cols.in.past - cols.in.present
    
    # Append row to positions data frame
    past.positions <- rep("N/A",cols.in.past)  # fill the past with N/A's 
    present.and.future.positions <- rep("police.officer", cols.in.future + cols.in.present)
    new.row <- c(new.id, past.positions, present.and.future.positions)
    positions <- rbind(positions, new.row)
    positions$id <- as.numeric(positions$id)
    
    # Append row to years.of.experience data frame
    past.experience <- rep(-1, cols.in.past)  # fill the past with -1's
    present.and.future.experience <- 1:(ncol(years.of.experience) - cols.in.past)
    # This causes trouble because these numbers will be type casted as characters
    new.row <- c(new.id, past.experience, present.and.future.experience)
    years.of.experience <- rbind(years.of.experience, new.row)
  }
# Fix the type cast issue
years.of.experience <- fix.years.of.experience(years.of.experience)

# Return the data frame
list(positions=positions, years.of.experience=years.of.experience)
}

sort.positions.to.replace <- function(positions.to.replace){
  # Let's check the table for promotable positions
  promotable.positions <- c("sergeant","sergeant.detective","detective","police.officer.traffic")
  positions.to.replace <- positions.to.replace[positions.to.replace$positions.needing.replacement %in% promotable.positions,]
  sort.order<- list(position = promotable.positions,
                    order = 1:length(promotable.positions))
  
  positions.to.replace$sort.order <- apply(positions.to.replace, 1, function(x) {
    sort.order$order[sort.order$position == x[1]]
  })
  
  positions.to.replace <- positions.to.replace[order(positions.to.replace$sort.order), ]
  return(positions.to.replace)
  
}

get.cost <- function(position, year, cost, column){
  if(position=="N/A" || position == "retired"){
    return(0)
  }else {
    return(cost[cost$position == position & cost$years.of.service == year, column+1])
  }
}

get.total.cost.table <- function(positions, years.of.experience, cost.table){
  # Create a data frame to hold the costs
  ncols <- ncol(positions)
  nrows <- nrow(positions)
  dummy.data <- rep(1.0000000000, (ncols - 1) * nrows)
  temp <- as.data.frame(matrix(dummy.data, nrows))
  total.costs <- cbind(positions[,1], temp)
  rm(temp)
  names(total.costs) <- names(positions)
  
  for(col in 2:ncols){
    for(row in 1:nrows){
      position <- positions[row, col]
      year <- years.of.experience[row, col]
      total.costs[row,col] <- get.cost(position, year, cost.table, col)
    }
  }
  return(total.costs)
}

get.cost.summaries <- function(low.costs, mid.costs, high.costs){
  # Sumarize
  low <- colSums(low.costs)
  mid <- colSums(mid.costs)
  high <- colSums(high.costs)
  
  data <- as.data.frame(t(data.frame(Low = low, Mid = mid, High = high)))
  keep <- names(data) %in% c("id") 
  return(data[!keep])
}

get.line.chart <- function(data, names, title){
  library(reshape2, ggplot2)
  names(data) <- names
  data$Estimate <- row.names(data)
  melted.data <- melt(data, id.vars="Estimate", value.name="Cost", variable.name="Year")
  melted.data$Cost <- melted.data$Cost / 1000000
  ggplot(data=melted.data, aes(x=Year, y=Cost, group = Estimate, colour = Estimate)) +
    geom_line() + ggtitle(title)
}