y <- c(-.2, .5, 1.4);forecast_mean <- c(0, .2, 1);forecast_sd <- c(1, .5, .8)
z <- qnorm(pnorm(y, forecast_mean, forecast_sd))
print(z);stopifnot(max(abs(z - (y - forecast_mean) / forecast_sd)) < 1e-12)
set.seed(3232);counts <- c(0, 1, 3, 5);lambda <- 2
u <- ppois(counts, lambda) - runif(length(counts)) * dpois(counts, lambda)
print(data.frame(counts = counts, randomized_quantile = u, residual = qnorm(u)))
stopifnot(all(u > 0 & u < 1))
