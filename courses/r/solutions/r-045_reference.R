# r-045: complete reference for the declared synthetic inputs.
d <- data.frame(id = 1:8, group = rep(LETTERS[1:4], each = 2), x = 0:7)
d$y <- 1 + 2 * d$x
train <- d$group %in% c("A", "B")
stopifnot(length(intersect(d$group[train], d$group[!train])) == 0)
stopifnot(length(intersect(d$group[c(1, 3, 5, 7)], d$group[c(2, 4, 6, 8)])) == 4)
folds <- lapply(unique(d$group), function(g) {
  train <- d$group != g
  stopifnot(length(intersect(d$group[train], d$group[!train])) == 0)
  fit <- lm(y ~ x, data = d[train, ])
  error <- d$y[!train] - predict(fit, d[!train, ])
  data.frame(group = g, n = sum(!train), squared_error_sum = sum(error^2))
})
folds <- do.call(rbind, folds)
stopifnot(sum(folds$n) == 8, sum(folds$squared_error_sum) < 1e-20)
center <- mean(c(0, 2))
stopifnot(center == 1, mean(c(0, 2, 100, 102)) == 51)
day <- 1:6
stopifnot(max(day[day <= 4]) < min(day[day > 4]))
stopifnot((2 + 12) / (1 + 3) == 3.5, mean(c(2 / 1, 12 / 3)) == 3)
cat("r-045 reference checks passed\n")
