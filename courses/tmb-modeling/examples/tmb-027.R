f <- function(x) exp(x) + x^4
for (x in c(-.4, .7)) {
  h <- 1e-4
  numeric_first <- (f(x + h) - f(x - h)) / (2 * h)
  numeric_second <- (f(x + h) - 2 * f(x) + f(x - h)) / h^2
  print(c(x = x, first_error = numeric_first - (exp(x) + 4 * x^3), second_error = numeric_second - (exp(x) + 12 * x^2)))
  stopifnot(abs(numeric_first - (exp(x) + 4 * x^3)) < 1e-6)
}
x <- .5
print(c(first = 4 * x^3, second = 12 * x^2, third = 24 * x, fourth = 24))
