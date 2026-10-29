set.seed(1919)
B <- 200L; n <- 30L; truth <- 2; sigma <- 1
estimate <- replicate(B, mean(rnorm(n, truth, sigma)))
covered <- abs(estimate - truth) <= qnorm(.975) * sigma / sqrt(n)
print(c(bias = mean(estimate) - truth, coverage = mean(covered), mcse = sqrt(.95 * .05 / B)))
dependent <- replicate(B, mean(truth + rnorm(1, 0, .6) + rnorm(n, 0, sigma)))
wrong_coverage <- mean(abs(dependent - truth) <= qnorm(.975) * sigma / sqrt(n))
print(c(coverage_assuming_independence = wrong_coverage, attempted = B))
stopifnot(all(is.finite(estimate)), wrong_coverage < .8)
