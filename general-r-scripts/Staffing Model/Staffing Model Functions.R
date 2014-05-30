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

update.positions <- function(positions){ i
for(j in i:projection.years){
    positions[i] <- positions[i-1]
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
    positions.needing.replacement <- as.data.frame(positions[retiring[,i],i])
    positions[retiring[,i],i] <- "retired"
    
    # Determine how many positions need to be replaced
    active.positions <- nrow(as.data.frame(positions[positions[,i] != "retired",i]))
    positions.to.add <- force.size - active.positions
    if(positions.to.add > 0){
      temp <- add.staff(positions.to.add, positions, years.of.experience, i)
      positions <- temp$positions
      years.of.experience <- temp$years.of.experience
    }
    
    # Replace the retired officers
    
    # Code Here
      
  }
  
  #years.of.experience <- years.of.experience + 1
  list(positions=positions, years.of.experience=years.of.experience)
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