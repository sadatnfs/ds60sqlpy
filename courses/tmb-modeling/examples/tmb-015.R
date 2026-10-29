n <- 5; tau <- .7
for (phi in c(-.6, .6)) {
  covariance <- tau^2 * phi^abs(outer(1:n, 1:n, "-"))
  precision <- matrix(0, n, n)
  diag(precision) <- c(1, rep(1 + phi^2, n - 2), 1)
  precision[row(precision) == col(precision) + 1 | row(precision) == col(precision) - 1] <- -phi
  precision <- precision / (tau^2 * (1 - phi^2))
  stopifnot(max(abs(precision %*% covariance - diag(n))) < 1e-12)
  print(precision)
}
u <- c(.8, .3, -.1); phi <- .6
conditional <- -sum(dnorm(u[-1], phi * u[-length(u)], tau * sqrt(1 - phi^2), log = TRUE))
print(c(conditional_nll = conditional, stationary_nll = conditional - dnorm(u[1], 0, tau, log = TRUE)))
