# r-006: complete reference for the declared synthetic inputs.
stopifnot(length(c(NULL, NA_real_)) == 1L)
x <- c(NA_real_, NA_real_, 0)
stopifnot(sum(!is.na(x)) == 1, mean(x, na.rm = TRUE) == 0)
x <- c(2, Inf, NA_real_, 4)
stopifnot(identical(x[is.finite(x)], c(2, 4)))
all_missing <- c(NA_real_, NA_real_)
reported <- if (all(is.na(all_missing))) NA_real_ else sum(all_missing, na.rm = TRUE)
stopifnot(is.na(reported), is.na(NA_real_), is.na(NaN), !is.nan(NA_real_), is.nan(NaN))
ratio <- function(a, b) {
  if (!is.finite(b) || b == 0) return(NA_real_); a / b
}
stopifnot(is.na(ratio(1, 0)), ratio(4, 2) == 2)
cat("r-006 reference checks passed\n")
