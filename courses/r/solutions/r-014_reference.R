# r-014: complete reference for the declared synthetic inputs.
stopifnot(identical(vapply(list(c(1, 2), c(3)), sum, numeric(1)), c(3, 3)))
groups <- list(A = c(1, 2), empty = numeric(0))
stopifnot(vapply(groups, sum, numeric(1))[["empty"]] == 0)
summary <- lapply(groups, function(x) list(n = length(x), mean = if (length(x)) mean(x) else NA_real_))
stopifnot(summary$A$mean == 1.5, is.na(summary$empty$mean))
bad <- tryCatch(
  {
    vapply(list(1), function(x) c(x, x), numeric(1)); FALSE
  },
  error = function(e) TRUE
)
stopifnot(bad, identical(vapply(list(), sum, numeric(1)), numeric(0)))
stopifnot(identical(c(3, 1, 2) |> sort() |> head(2), c(1, 2)))
cat("r-014 reference checks passed\n")
