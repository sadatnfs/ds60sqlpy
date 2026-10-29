f <- function(x) x^4;h <- 1e-6
for (adjoint in c(.3, 2)) for (x in c(-.7, .4, 1.3)) {
  reverse <- 4 * x^3 * adjoint;numeric <- (adjoint * f(x + h) - adjoint * f(x - h)) / (2 * h)
  stopifnot(abs(reverse - numeric) < 1e-7)
}
x <- c(-1, 0, 1, 2);wrong <- 4 * x^3 + .1 * (x - 1)
print(data.frame(x = x, true = 4 * x^3, wrong = wrong, error = wrong - 4 * x^3));stopifnot(wrong[3] == 4, any(abs(wrong - 4 * x^3) > .05))
