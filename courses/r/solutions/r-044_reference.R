# r-044: complete reference for the declared synthetic inputs.
d <- data.frame(x = c(0, 1), successes = c(2, 6), failures = c(8, 4))
fit <- glm(cbind(successes, failures) ~ x, family = binomial(), data = d)
p <- as.numeric(predict(fit, type = "response"))
stopifnot(max(abs(p - c(0.2, 0.6))) < 1e-8)
stopifnot(max(abs(plogis(predict(fit, type = "link")) - p)) < 1e-10)
odds <- p / (1 - p)
stopifnot(abs(odds[2] / odds[1] - 6) < 1e-7, abs(p[2] / p[1] - 3) < 1e-7)
n <- sum(d$successes + d$failures)
brier <- sum(d$successes * (1 - p)^2 + d$failures * p^2) / n
stopifnot(n == 20, abs(brier - 0.2) < 1e-10)
x_sep <- c(-2, -1, 1, 2)
y_sep <- c(0, 0, 1, 1)
stopifnot(all(x_sep[y_sep == 0] < 0), all(x_sep[y_sep == 1] > 0))
heldout_rate <- c(1, 8) / 10
gaps <- heldout_rate - p
stopifnot(max(abs(gaps - c(-0.1, 0.2))) < 1e-8, abs(mean(abs(gaps)) - 0.15) < 1e-8)
cat("r-044 reference checks passed\n")
