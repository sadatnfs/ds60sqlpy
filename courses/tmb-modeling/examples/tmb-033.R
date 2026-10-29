for (tau in c(.5, 2)) {
  raw_integral <- integrate(function(u) exp(-u^2 / (2 * tau^2)), -Inf, Inf)$value
  normalized <- raw_integral / (sqrt(2 * pi) * tau)
  print(c(tau = tau, raw_integral = raw_integral, normalized = normalized));stopifnot(abs(normalized - 1) < 1e-8)
}
D <- matrix(c(-1, 1, 0, 0, -1, 1), 2, 3, byrow = TRUE)
Q <- crossprod(D)
print(eigen(Q, symmetric = TRUE)$values);stopifnot(max(abs(Q %*% rep(1, 3))) < 1e-12)
