# r-042: complete reference for the declared synthetic inputs.
mean_se <- function(x) {
  if (length(x) < 2L || anyNA(x) || any(!is.finite(x))) stop("at least two finite observations required")
  sd(x) / sqrt(length(x))
}
x <- c(2, 4, 6, 8)
stopifnot(mean(x) == 5, isTRUE(all.equal(mean_se(x)^2, 5 / 3)))
stopifnot(mean(x + 3) == 8, isTRUE(all.equal(mean_se(x + 3), mean_se(x))))
indices <- expand.grid(rep(list(seq_along(x)), length(x)))
means <- apply(indices, 1, function(i) mean(x[as.integer(i)]))
stopifnot(length(means) == 256, mean(means) == 5)
stopifnot(isTRUE(all.equal(mean((means - 5)^2), 5 / 4)))
stopifnot(isTRUE(all.equal(sd(x) / length(x), mean_se(x) / 2)))
stopifnot(inherits(try(mean_se(1), silent = TRUE), "try-error"))
t_interval <- mean(x) + c(-1, 1) * qt(0.975, 3) * mean_se(x)
percentile <- quantile(means, c(0.025, 0.975), type = 7, names = FALSE)
stopifnot(t_interval[1] < 5, t_interval[2] > 5, percentile[1] <= 5, percentile[2] >= 5)
print(list(t_mean_interval = t_interval, exact_empirical_percentile = percentile))
cat("r-042 reference checks passed\n")
