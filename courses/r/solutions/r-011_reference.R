# r-011: complete reference for the declared synthetic inputs.
square <- function(x) {
  out <- numeric(length(x)); for (i in seq_along(x)) out[[i]] <- x[[i]]^2; out
}
stopifnot(identical(square(c(1, 3)), c(1, 9)), identical(square(numeric(0)), numeric(0)))
total <- 0
for (value in c(-2, 3, 4)) {
  if (value > 0) total <- total + value
}
stopifnot(total == 7, identical(1:0, c(1L, 0L)))
state <- 20; steps <- 0L
while (state > 3 && steps < 10L) {
  state <- state / 2; steps <- steps + 1L
}
stopifnot(state <= 3, steps == 3L)
stopifnot(identical(square(c(1, 3)), c(1, 3)^2))
cat("r-011 reference checks passed\n")
