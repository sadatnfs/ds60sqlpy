# r-004: complete reference for the declared synthetic inputs.
stopifnot(is.na(TRUE & NA), identical(FALSE & NA, FALSE))
x <- c(5, 12, NA_real_, 20)
stopifnot(identical(x[!is.na(x) & x >= 15], 20))
mask <- !is.na(x) & x >= 10 & x <= 20
stopifnot(identical(x[mask], c(12, 20)))
stopifnot(identical(is.na(x), c(FALSE, FALSE, TRUE, FALSE)))
empty <- numeric(0)
stopifnot(!(length(empty) > 0 && empty[[1]] > 0))
stopifnot(is.na(all(c(TRUE, NA))), isTRUE(all(c(TRUE, NA), na.rm = TRUE)))
cat("r-004 reference checks passed\n")
