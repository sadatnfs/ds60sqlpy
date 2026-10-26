# r-020: complete reference for the declared synthetic inputs.
weighted_average <- function(x, w) {
  stopifnot(is.numeric(x), is.numeric(w), length(x) == length(w), length(x) > 0L)
  stopifnot(all(is.finite(x)), all(is.finite(w)), all(w >= 0), sum(w) > 0)
  sum(x * w) / sum(w)
}
stopifnot(weighted_average(c(10, 20), c(1, 3)) == 17.5)
stopifnot(weighted_average(c(10, 20), c(5, 15)) == 17.5)
rejected <- function(x, w) tryCatch(
  {
    weighted_average(x, w); FALSE
  },
  error = function(e) TRUE
)
stopifnot(rejected(c(10, 20), 1), rejected(c(10, 20), c(0, 0)), rejected(numeric(0), numeric(0)))
stopifnot(rejected(c(10, NA_real_), c(1, 1)))
set.seed(17); first <- runif(4)
set.seed(17); second <- runif(4)
stopifnot(identical(first, second), all(first >= 0 & first <= 1))
cat("r-020 reference checks passed\n")
