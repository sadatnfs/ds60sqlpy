# r-005: complete reference for the declared synthetic inputs.
stopifnot(identical(c(4, 8)[c(2, 2, 1)], c(8, 8, 4)))
stopifnot(identical(c(2, 4, 6)[-2], c(2, 6)))
x <- c(A = 1, B = 2)
key <- "B"
stopifnot(!anyDuplicated(names(x)), key %in% names(x))
x[key] <- 9
stopifnot(identical(unname(x), c(1, 9)))
error <- tryCatch(
  {
    c(2, 4, 6)[c(1, -2)]; FALSE
  },
  error = function(e) TRUE
)
stopifnot(error, length(x[integer(0)]) == 0L)
stopifnot(anyDuplicated(c("A", "A")) > 0L)
cat("r-005 reference checks passed\n")
