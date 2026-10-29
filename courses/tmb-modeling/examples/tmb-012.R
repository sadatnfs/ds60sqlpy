y <- c(.2, .8, 1.1); beta <- .5; sigma <- .4; tau <- .7
V <- sigma^2 * diag(length(y)) + tau^2 * matrix(1, length(y), length(y))
R <- chol(V); residual <- y - beta
nll <- .5 * (length(y) * log(2 * pi) + 2 * sum(log(diag(R))) + sum(backsolve(R, forwardsolve(t(R), residual)) * residual))
print(list(covariance = V, marginal_nll = nll))
m <- c(2, 20); shrink <- m * tau^2 / (sigma^2 + m * tau^2)
print(data.frame(group_size = m, shrinkage_factor = shrink, latent_mode = shrink * .8))
stopifnot(shrink[2] > shrink[1], all(eigen(V, symmetric = TRUE)$values > 0))
