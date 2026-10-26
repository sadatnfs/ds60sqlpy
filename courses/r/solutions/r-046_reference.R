# r-046: complete reference for the declared synthetic inputs.
x <- cbind(short = c(-2, -1, 1, 2), long = c(-20, -10, 10, 20))
raw <- prcomp(x, center = TRUE, scale. = FALSE)
scaled <- prcomp(x, center = TRUE, scale. = TRUE)
stopifnot(abs(abs(raw$rotation[2, 1]) - 10 / sqrt(101)) < 1e-10)
stopifnot(max(abs(abs(scaled$rotation[, 1]) - 1 / sqrt(2))) < 1e-10)
y <- cbind(a = c(1, 2, 4, 5), b = c(2, 1, 5, 4))
pc <- prcomp(y, center = TRUE, scale. = TRUE)
rebuild <- function(scores, rotation) sweep(sweep(scores %*% t(rotation), 2, pc$scale, "*"), 2, pc$center, "+")
stopifnot(max(abs(rebuild(pc$x, pc$rotation) - y)) < 1e-10)
scores <- pc$x; rotation <- pc$rotation
scores[, 1] <- -scores[, 1]; rotation[, 1] <- -rotation[, 1]
stopifnot(max(abs(rebuild(scores, rotation) - y)) < 1e-10)
stopifnot(inherits(try(prcomp(cbind(v = 1:4, constant = rep(1, 4)), scale. = TRUE), silent = TRUE), "try-error"))
new <- matrix(c(3, 2), nrow = 1, dimnames = list(NULL, colnames(y)))
manual <- sweep(sweep(new, 2, pc$center, "-"), 2, pc$scale, "/") %*% pc$rotation
stopifnot(max(abs(manual - predict(pc, newdata = new))) < 1e-10)
stopifnot(abs(sum(pc$sdev^2 / sum(pc$sdev^2)) - 1) < 1e-12)
cat("r-046 reference checks passed\n")
