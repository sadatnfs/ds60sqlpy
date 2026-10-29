for (tau in c(.5, 2)) {
  at_mode <- log(tau) + .5 * log(2 * pi)
  marginal_nll <- at_mode + .5 * log(1 / tau^2) - .5 * log(2 * pi)
  print(c(tau = tau, nll = marginal_nll))
  stopifnot(abs(marginal_nll) < 1e-12)
}
for (lambda in c(0, .2, 1)) {
  exact <- -log(integrate(function(u) exp(-u^2 / 2 - lambda * u^4), -Inf, Inf)$value)
  approximate <- -.5 * log(2 * pi)
  print(c(lambda = lambda, quadrature_nll = exact, laplace_nll = approximate, error = approximate - exact))
}
