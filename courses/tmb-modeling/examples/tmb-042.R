log_add <- function(a, b) {
  m <- max(a, b);m + log(exp(a - m) + exp(b - m))
}
a <- log(.3) + dnorm(.5, -1, 1, log = TRUE);b <- log(.7) + dnorm(.5, 1, 1, log = TRUE)
print(c(stable = log_add(a, b), direct = log(.3 * dnorm(.5, -1, 1) + .7 * dnorm(.5, 1, 1))))
print(c(extreme_stable = log_add(-1000, -1001), extreme_direct = log(exp(-1000) + exp(-1001))))
log_difference <- function(a, b) {
  stopifnot(a > b);a + log1p(-exp(b - a))
}
stopifnot(abs(log_difference(log(.9), log(.4)) - log(.5)) < 1e-12)
