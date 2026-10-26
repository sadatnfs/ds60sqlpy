# r-008: complete reference for the declared synthetic inputs.
m <- matrix(1:6, nrow = 2)
stopifnot(identical(m[1, ], c(1L, 3L, 5L)))
by_row <- matrix(1:6, nrow = 2, byrow = TRUE)
stopifnot(identical(by_row[1, ], c(1L, 2L, 3L)))
design <- cbind(1, c(3, 4))
stopifnot(identical(as.numeric(design %*% c(2, 3)), c(11, 14)))
one <- design[, 1, drop = FALSE]
stopifnot(identical(dim(one), c(2L, 1L)))
a <- diag(c(2, 4)); b <- c(6, 8); solution <- solve(a, b)
stopifnot(max(abs(a %*% solution - b)) < 1e-12)
cat("r-008 reference checks passed\n")
