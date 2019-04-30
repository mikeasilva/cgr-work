library(readxl)
library(openxlsx)
library(stringr)
library(dplyr)

start_year <- 2012
end_year <- 2019    

base_dir <- "Remaining Budget"

skip_me <- c("Remaining Budget Report 2-28-13.xls", "Remaining Budget Report 12-31-14.xls", "Remaining Budget 2-29-16.xls", "Remaining Budget 3-31-2016.xlsx")

get_month_and_day <- function(f){
  f %>%
    str_replace("Remaining Budget Report ", "") %>%
    str_replace("Remaining Budget ", "") %>%
    str_replace("Jan", "1") %>%
    str_replace("Feb", "2") %>%
    str_replace("Mar", "3") %>%
    str_replace("April", "4") %>%
    str_replace("May", "5") %>%
    str_replace("June", "6") %>%
    str_replace("Jul", "7") %>%
    str_replace("Aug", "8") %>%
    str_replace("Sep", "9") %>%
    str_replace("Oct", "10") %>%
    str_replace("Nov", "11") %>%
    str_replace("Dec", "12") %>%
    str_replace(" ", "-") %>%
    str_split("-")
}

for (dir in list.dirs(base_dir)){
  year <- as.numeric(str_split(dir, "/")[[1]][5])
  if(dir != base_dir && (year >= start_year && year <= end_year)){
    message(dir)
    for (f in list.files(dir, "xls")){
      if (!(f %in% skip_me)){
        month_and_day <- get_month_and_day(f)
        f_date <- paste0(year,"/", month_and_day[[1]][1], "/", month_and_day[[1]][2]) %>%
          as.Date()

        temp <- suppressMessages(read_excel(paste0(dir,"/",f), skip = 2)) %>%
          select("Project Number", "Project Name", "Project Manager", Budget, "Cost to Date", "Remain Budget") %>%
          rename(Project.Number = "Project Number",
                 Project.Name= "Project Name",
                 Project.Manager = "Project Manager",
                 Cost.to.Date = "Cost to Date",
                 Remain.Budget = "Remain Budget") %>%
          mutate( Budget = as.numeric(Budget),
                  Cost.to.Date = as.numeric(Cost.to.Date),
                  Remain.Budget = as.numeric(Remain.Budget),
                  date = f_date)
        if(exists("cgr")){
          cgr <- cgr %>%
            bind_rows(temp)
        } else {
          cgr <- temp
        }
      }
    }
  }
}

write.xlsx(cgr, "Remaining Budgets.xlsx")