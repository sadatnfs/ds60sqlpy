# r-041: complete reference for the declared synthetic inputs.
describe <- function(x) {
  valid <- !is.na(x)
  c(
    rows = length(x), observed = sum(valid), missing = sum(!valid),
    mean = if (any(valid)) mean(x[valid]) else NA_real_,
    median = if (any(valid)) median(x[valid]) else NA_real_
  )
}
a <- describe(c(0, NA_real_, 2, NA_real_))
stopifnot(a[["rows"]] == 4, a[["observed"]] == 2, a[["missing"]] == 2, a[["mean"]] == 1)
b <- describe(c(1, NA_real_, 4, 6, NA_real_, 8))
stopifnot(b[["observed"]] == 4, b[["mean"]] == 19 / 4)
groups <- list(A = c(1, NA_real_), B = c(4, 6, NA_real_))
summaries <- lapply(groups, describe)
stopifnot(summaries$A[["observed"]] == 1, summaries$B[["observed"]] == 2)
stopifnot(summaries$A[["mean"]] == 1, summaries$B[["mean"]] == 5)
weighted <- sum(vapply(summaries, function(s) s[["mean"]] * s[["observed"]], numeric(1))) /
  sum(vapply(summaries, function(s) s[["observed"]], numeric(1)))
stopifnot(isTRUE(all.equal(weighted, 11 / 3)))
x <- c(1, NA_real_, 4, 6, NA_real_)
filled <- replace(x, is.na(x), 0)
stopifnot(mean(filled) == 11 / 5, !isTRUE(all.equal(mean(filled), weighted)))
empty <- describe(c(NA_real_, NA_real_))
stopifnot(empty[["observed"]] == 0, is.na(empty[["mean"]]))
tail <- c(1, 2, 2, 3, 100)
stopifnot(isTRUE(all.equal(mean(tail), 21.6)), median(tail) == 2)
cat("r-041 reference checks passed\n")
