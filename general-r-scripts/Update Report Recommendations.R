## Load all libraries needed
for (l in c("dplyr", "xml2", "tm", "SnowballC", "tidyr", "httr", "rjson")){
  # If the library is not installed, install it
  if (!is.element(l, .packages(all.available = TRUE))){
    install.packages(l)
  }
  # Load the library
  suppressMessages(library(l, character.only = TRUE))
}

# Number of nearest neighbors you want included
nearest_neighbors <- 3

## Build the list of reports to include
xml <- read_xml("http://HIDDEN/api/update-reports")
X1 <- xml %>%
  xml_children() %>%
  xml_children() %>%
  xml_name()

X2 <- xml %>%
  xml_children() %>%
  xml_children() %>%
  xml_text()
# Put it all together in a data frame
reports <- data.frame(X1, X2) %>%
  mutate(new_record = ifelse(X1 == "Project_x0023_", 1, 0)) %>%
  mutate(id = cumsum(new_record)) %>%
  mutate(keep = ifelse(X1 == "Reportfilename", 1, 0)) %>%
  mutate(keep = ifelse(X1 == "ReptonWebsite_x003F_", 1, keep)) %>%
  filter(keep == 1) %>%
  select(-keep, -new_record) %>%
  spread(X1, X2) %>%
  filter(ReptonWebsite_x003F_ == 1) %>%
  select(Reportfilename) %>%
  mutate(Reportfilename = as.character(Reportfilename))
# And vectorize it
reports <- reports$Reportfilename


## Read in all the report
root_dir <- "G:/Reports"

get_corpus <- function(full_path, report){
  document <- Corpus(URISource(full_path),
                     readerControl = list(reader = reader)) %>%
    tm_map(PlainTextDocument)  %>% # Create plain text document
    tm_map(content_transformer(tolower)) %>% # Standardize case
    tm_map(removeWords, stopwords("SMART")) %>% # Remove stopwords
    tm_map(removePunctuation) %>% # Remove punctuation marks
    tm_map(removeNumbers) %>% # Remove numbers
    tm_map(stripWhitespace) %>% # Remove extra whitespace
    tm_map(removePunctuation) %>% # Remove punctuation marks again
    tm_map(stemDocument) # Stem the documents
  meta(document, "report") <- report
  return(document)
}

reader <- readPDF(control = list(text = "-layout"))

for (d in list.dirs(root_dir, recursive = FALSE)){
  for (f in list.files(d, pattern = ".pdf")){
    if (f %in% reports){
      message(f)
      full_path <- paste0(d, "/", f)
      corpus <- suppressMessages(get_corpus(full_path, f))
      if (!exists("cgr_corpus")){
        cgr_corpus <- corpus
      } else {
        cgr_corpus <- c(cgr_corpus, corpus)
      }
    }
  }
}

## Find similar reports
message("Creating Document Term Matrix")
dtm <- DocumentTermMatrix(cgr_corpus)

min_docs <- 10
dtm <- removeSparseTerms(dtm, 1 - (min_docs / length(cgr_corpus)))

model_data <- as.matrix(dtm)
words <- rowSums(model_data)
model_data <- model_data / words


message("Calculating Cosine Simularity")
cos.sim <- function(ix){
  A <- model_data[ix[1], ]
  B <- model_data[ix[2], ]
  return(sum(A * B) / sqrt(sum(A ^ 2) * sum(B ^ 2)))
}

n <- nrow(model_data)
cmb <- expand.grid(i = 1:n, j = 1:n)
cosine_similarity <- data.frame(matrix(apply(cmb, 1, cos.sim), n, n))
reports <- meta(cgr_corpus)$report
names(cosine_similarity) <- reports
cosine_similarity$report <- reports

cosine_similarity <- cosine_similarity %>%
  gather(key = peer, value = cosine_similarity, -report) %>%
  na.omit() %>%
  filter(cosine_similarity < 1) %>%
  arrange(report, -cosine_similarity) %>%
  group_by(report) %>%
  top_n(nearest_neighbors) %>%
  ungroup() %>%
  mutate(id = row_number()) %>%
  rename(report_file_name = report) %>%
  rename(recommendation_file_name = peer) %>%
  select(id, report_file_name, recommendation_file_name, cosine_similarity)

## Post the json data
message("Saving")
# Clear out the old data
response <- GET("https://HIDDEN/api/clear_recomendations")
# Save recomendations in chunks of 50 reports
url <- "https://HIDDEN/api/recomendations"
n <- nearest_neighbors
nr <- nrow(cosine_similarity)
for(temp in split(cosine_similarity, rep(1:ceiling(nr/n), each=n, length.out=nr))){
  data <- toJSON(unname(split(temp, 1:nrow(temp))))
  body <- list(data = data)
  response <- POST(url, body = body, encode = "form")
  if(content(response, "text") != "Recomendations updated"){
    print("Something bad happened")
    head(temp)
  }
}
