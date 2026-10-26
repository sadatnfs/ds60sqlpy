# r-012: complete reference for the declared synthetic inputs.
after_fee <- function(amount, rate = 0.1) {
  if (!is.numeric(amount) || !is.numeric(rate) || length(rate) != 1L || !is.finite(rate) || rate < 0 || rate > 1) stop("invalid fee inputs", call. = FALSE)
  amount * (1 - rate)
}
stopifnot(after_fee(50) == 45, after_fee(50, rate = 0) == 50)
summary <- function(x) list(count = length(x), total = sum(x))
stopifnot(identical(summary(c(2, 4)), list(count = 2L, total = 6)))
bad <- tryCatch(
  {
    after_fee(50, c(0.1, 0.2)); FALSE
  },
  error = function(e) TRUE
)
stopifnot(bad, identical(after_fee(numeric(0)), numeric(0)))
stopifnot(after_fee(50, rate = 0.2) != after_fee(50))
bad_type <- tryCatch(
  {
    after_fee(10, TRUE); FALSE
  },
  error = function(e) TRUE
)
stopifnot(bad_type)
cat("r-012 reference checks passed\n")
