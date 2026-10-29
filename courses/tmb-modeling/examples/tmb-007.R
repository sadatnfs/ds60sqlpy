y <- c(1, 2, 4, 7)
fn <- function(p) -sum(dnorm(y, p[1], exp(p[2]), log = TRUE))
gr <- function(p) c(sum(p[1] - y) / exp(2 * p[2]), length(y) - sum((y - p[1])^2) / exp(2 * p[2]))
fits <- lapply(list(c(-2, 0), c(8, 2)), function(start) nlminb(start, fn, gr))
for (fit in fits) print(c(fit$par, value = fit$objective, gradient = max(abs(gr(fit$par)))))
stopifnot(max(abs(fits[[1]]$par - fits[[2]]$par)) < 1e-4)
curve <- function(t, a, b, c) a * exp(-b * t) + c
print(data.frame(time = c(0, .1, 8), first = curve(c(0, .1, 8), 3, .6, 1), second = curve(c(0, .1, 8), 6, .3, -2)))
