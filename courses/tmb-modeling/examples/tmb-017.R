A <- matrix(c(2, .2, .2, 1), 2, 2); B <- matrix(c(3, .4, .4, 2), 2, 2)
full <- matrix(0, 4, 4); full[1:2, 1:2] <- A; full[3:4, 3:4] <- B
logdet <- function(M) as.numeric(determinant(M, logarithm = TRUE)$modulus)
print(c(full = logdet(full), blocks = logdet(A) + logdet(B)))
stopifnot(abs(logdet(full) - logdet(A) - logdet(B)) < 1e-12)
coupled <- matrix(c(2, .8, .8, 2), 2, 2)
print(c(coupled = logdet(coupled), incorrect_independent = 2 * log(2)))
stopifnot(abs(logdet(coupled) - 2 * log(2)) > .1)
