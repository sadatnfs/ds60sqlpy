H <- matrix(c(3, .5, .5, 2), 2, 2);b <- c(1, -2);u <- c(8, -7)
g <- drop(H %*% u) - b;step <- solve(H, g);updated <- u - step
print(list(gradient = g, step = step, updated = updated, exact = solve(H, b)));stopifnot(max(abs(updated - solve(H, b))) < 1e-12)
bad <- matrix(c(1, 2, 2, 1), 2, 2)
print(list(original = eigen(bad, symmetric = TRUE)$values, shifted = eigen(bad + 2 * diag(2), symmetric = TRUE)$values))
