x <- seq(-1, 1, length.out = 20)
X <- cbind(1, x)
near <- cbind(1, x, x + 1e-5 * cos(seq_along(x)))
print(list(
  ordinary = eigen(crossprod(X), symmetric = TRUE)$values,
  nearly_collinear = eigen(crossprod(near), symmetric = TRUE)$values
))
stopifnot(kappa(crossprod(near)) > 1e8)
s <- log(2); se_s <- .2
print(list(delta_sd = exp(s) * se_s, transformed_interval = exp(s + c(-1, 1) * 1.96 * se_s)))
stopifnot(all(exp(s + c(-1, 1) * 1.96 * se_s) > 0))
