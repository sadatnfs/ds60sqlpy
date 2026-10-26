# r-032: complete reference for the declared synthetic inputs.
groups <- list(A = 10, B = c(20, 30, 40))
sums <- vapply(groups, sum, numeric(1)); counts <- vapply(groups, length, integer(1))
stopifnot(sum(sums) / sum(counts) == 25)
groups$B <- c(groups$B, 50)
stopifnot(sum(unlist(groups)) / length(unlist(groups)) == 30)
summarize <- function(x) {
  valid <- !is.na(x); c(rows = length(x), observed = sum(valid), missing = sum(!valid), sum = sum(x[valid]), mean = if (any(valid)) mean(x[valid]) else NA_real_)
}
stopifnot(summarize(c(NA_real_, NA_real_))[["observed"]] == 0, is.na(summarize(numeric(0))[["mean"]]))
a <- c("U1", "U2"); b <- c("U2", "U3")
stopifnot(length(unique(c(a, b))) == 3, length(unique(a)) + length(unique(b)) == 4)
stopifnot(median(c(0, 100, 101)) != mean(c(median(0), median(c(100, 101)))))
cat("r-032 reference checks passed\n")
