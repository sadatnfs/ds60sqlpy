y <- c(1, 2, 6)
trace_objective <- function(y) {
  mu <- mean(y)
  data.frame(
    mu = c(0, mu),
    value = vapply(c(0, mu), function(m) sum((y - m)^2) / 2, numeric(1)),
    gradient = vapply(c(0, mu), function(m) length(y) * m - sum(y), numeric(1))
  )
}
print(trace_objective(y))
print(trace_objective(c(1, 2, 9)))
stopifnot(mean(y) == 3, mean(c(1, 2, 9)) == 4)
