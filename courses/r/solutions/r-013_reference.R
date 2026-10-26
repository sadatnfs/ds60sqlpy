# r-013: complete reference for the declared synthetic inputs.
make_multiplier <- function(factor) {
  force(factor)
  stopifnot(is.numeric(factor), length(factor) == 1L, is.finite(factor))
  function(x) x * factor
}
stopifnot(make_multiplier(4)(2) == 8)
a <- make_multiplier(2); b <- make_multiplier(3)
stopifnot(a(5) == 10, b(5) == 15)
make_threshold <- function(threshold) {
  force(threshold); function(x) x >= threshold
}
t <- 10; predicate <- make_threshold(t); t <- 100
stopifnot(predicate(20))
lazy_factory <- function(factor) function(x) x * factor
v <- 2; lazy <- lazy_factory(v); v <- 5
stopifnot(lazy(3) == 15)
bad <- tryCatch(
  {
    make_multiplier(NA_real_); FALSE
  },
  error = function(e) TRUE
)
stopifnot(bad)
cat("r-013 reference checks passed\n")
