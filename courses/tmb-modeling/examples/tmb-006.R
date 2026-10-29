y <- c(1, 2, 4, 7)
fn <- function(p) -sum(dnorm(y, p[1], exp(p[2]), log = TRUE))
gr <- function(p) c(sum(p[1] - y) / exp(2 * p[2]), length(y) - sum((y - p[1])^2) / exp(2 * p[2]))
central <- function(p, h) vapply(seq_along(p), function(j) {
  a <- b <- p; a[j] <- a[j] + h; b[j] <- b[j] - h
  (fn(a) - fn(b)) / (2 * h)
}, numeric(1))
for (p in list(c(2.2, .3), c(-1, 1))) {
  errors <- vapply(c(1e-2, 1e-4, 1e-6), function(h) max(abs(central(p, h) - gr(p))), numeric(1))
  print(errors)
  stopifnot(errors[2] < 1e-5)
}
