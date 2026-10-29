R <- matrix(c(1, .4, .4, 1), 2, 2);scales <- c(2, .5);D <- diag(scales);u <- c(.3, -.4)
nll <- function(x, S) length(x) * log(2 * pi) / 2 + as.numeric(determinant(S, logarithm = TRUE)$modulus) / 2 + sum(x * solve(S, x)) / 2
print(c(direct = nll(u, D %*% R %*% D), transformed = nll(u / scales, R) + sum(log(scales))))
stopifnot(abs(nll(u, D %*% R %*% D) - nll(u / scales, R) - sum(log(scales))) < 1e-12)
space <- .3^abs(outer(1:2, 1:2, "-"));time <- .7^abs(outer(1:3, 1:3, "-"));S <- kronecker(time, space)
print(S);stopifnot(S[1, 2] == .3, S[1, 3] == .7, abs(S[1, 4] - .21) < 1e-12)
