s <- log(2); var_s <- .04
h <- 1e-6
jac <- (exp(s + h) - exp(s - h)) / (2 * h)
print(c(delta_variance = exp(2 * s) * var_s, numerical = jac^2 * var_s))
alpha <- .2; beta <- .7; ratio <- exp(beta - alpha)
V <- matrix(c(.04, .015, .015, .09), 2, 2)
J <- c(-ratio, ratio)
print(c(ratio = ratio, full_se = sqrt(drop(t(J) %*% V %*% J)), independence_se = ratio * sqrt(sum(diag(V)))))
stopifnot(abs(jac - exp(s)) < 1e-8, all(eigen(V, symmetric = TRUE)$values > 0))
