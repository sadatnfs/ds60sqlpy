for (lambda in c(.1, .8)) {
  integral <- integrate(function(u) exp(-u^2 / 2 - lambda * u^4), -Inf, Inf)$value
  print(c(lambda = lambda, quadrature = integral, laplace = sqrt(2 * pi)))
}
prior <- c(.3, .7);conditional <- dnorm(.5, mean = c(-1, 1), sd = .8)
marginal <- sum(prior * conditional)
print(c(marginal_density = marginal, nll = -log(marginal)));stopifnot(marginal > 0)
print(data.frame(dimension = 1:5, grid_points = 20^(1:5)))
