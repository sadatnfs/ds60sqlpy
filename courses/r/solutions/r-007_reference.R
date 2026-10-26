# r-007: complete reference for the declared synthetic inputs.
x <- c(A = 1, B = 2)
y <- x
y[1] <- 9
stopifnot(x[[1]] == 1)
z <- unname(x)
stopifnot(is.null(names(z)), identical(z, c(1, 2)))
m <- 1:4
dim(m) <- c(2L, 2L)
stopifnot(identical(dim(m), c(2L, 2L)))
e <- new.env(parent = emptyenv()); e$count <- 1
alias <- e; alias$count <- 3
stopifnot(e$count == 3, !identical(c(A = 1), 1))
stopifnot(identical(names(x), c("A", "B")))
cat("r-007 reference checks passed\n")
