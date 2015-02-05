prime.numbers <- function(limit){
  n <- 2:limit
  i <- 1
  while(i < length(n)){
    p <- n[i]
    not.prime <- n[which(n %% p==0)]
    not.prime <- not.prime[! not.prime %in% p]
    n <- n[! n %in% not.prime]
    i <- i + 1
  }
  n
}