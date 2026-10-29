Q <- diag(4) * 3;Q[row(Q) == col(Q) + 1 | row(Q) == col(Q) - 1] <- -.7;b <- c(1, 2, -1, .5)
x <- solve(Q, b);print(c(solve_residual = max(abs(Q %*% x - b)), inverse_difference = max(abs(x - solve(Q) %*% b))))
permutation <- c(4, 2, 1, 3);z <- solve(Q[permutation, permutation], b[permutation]);restored <- numeric(4);restored[permutation] <- z
stopifnot(max(abs(restored - x)) < 1e-12)
approximate <- diag(diag(Q));xa <- solve(approximate, b)
print(c(dropped_coupling_residual = max(abs(Q %*% xa - b))))
