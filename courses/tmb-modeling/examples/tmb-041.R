a <- array(1:6, dim = c(2, 3));print(a);print(as.vector(a));stopifnot(a[2, 2] == 4, identical(as.vector(a), 1:6))
group <- c(1L, 2L, 1L, 3L);u <- c(-.2, .4, .8);Z <- matrix(0, 4, 3);Z[cbind(1:4, group)] <- 1
print(Z);stopifnot(max(abs(drop(Z %*% u) - u[group])) < 1e-12)
print(list(r_indices = group, explicit_cpp_indices = group - 1L))
