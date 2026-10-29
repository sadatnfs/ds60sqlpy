Sigma <- matrix(c(2, .5, .5, 1), 2, 2);Q <- solve(Sigma);u <- c(.3, -.4);constant <- length(u) * log(2 * pi) / 2
ld <- function(M) as.numeric(determinant(M, logarithm = TRUE)$modulus)
a <- constant + ld(Sigma) / 2 + drop(t(u) %*% solve(Sigma, u)) / 2
b <- constant - ld(Q) / 2 + drop(t(u) %*% Q %*% u) / 2
wrong_precision_as_covariance <- constant + ld(Q) / 2 + drop(t(u) %*% solve(Q, u)) / 2
print(c(covariance_form = a, precision_form = b, wrong_precision_as_covariance = wrong_precision_as_covariance))
stopifnot(abs(a - b) < 1e-12, abs(wrong_precision_as_covariance - a) > .1)
D <- matrix(c(-1, 1, 0, 0, -1, 1), 2, 3, byrow = TRUE);intrinsic <- crossprod(D);proper <- intrinsic;proper[1, 1] <- proper[1, 1] + 1
print(list(intrinsic = eigen(intrinsic, symmetric = TRUE)$values, anchored = eigen(proper, symmetric = TRUE)$values))
