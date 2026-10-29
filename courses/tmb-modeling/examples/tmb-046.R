f <- function(x) pmax(x, 0)^2;g <- function(x) ifelse(x > 0, 2 * x, 0)
x <- c(-2, -.1, .1, 2);h <- 1e-6
numeric_gradient <- (f(x + h) - f(x - h)) / (2 * h)
print(data.frame(x = x, value = f(x), gradient = g(x), numeric = numeric_gradient));stopifnot(max(abs(g(x) - numeric_gradient)) < 1e-7)
softplus <- function(x) pmax(x, 0) + log1p(exp(-abs(x)))
print(c(stable = softplus(1000), naive = log1p(exp(1000))))
