# r-049: complete reference for the declared synthetic inputs.
y <- ts(c(2, 1.2, 0.8, 0.1, -0.2, 0.3, 0.1, 0.4))
fit <- arima(y, order = c(1, 0, 0), include.mean = FALSE, fixed = 0.5, transform.pars = FALSE, method = "ML")
f <- predict(fit, n.ahead = 3)
stopifnot(max(abs(as.numeric(f$pred) - c(0.2, 0.1, 0.05))) < 1e-10)
stopifnot(all(is.finite(f$se)), all(f$se >= 0))
series <- 1:8
origins <- 4:7
predictions <- vapply(origins, function(origin) tail(series[seq_len(origin)], 1), numeric(1))
actual <- series[origins + 1]
stopifnot(all(actual - predictions == 1), mean((actual - predictions)^2) == 1)
stopifnot(mean(series) != mean(series[1:4]))
changes <- diff(1:6)
stopifnot(length(changes) == 5, all(changes == 1))
stopifnot(all(origins < origins + 1))
cat("r-049 reference checks passed\n")
