a <- 3; b <- .6; offset <- 1; future <- c(9, 10, 12)
trend <- a * exp(-b * future) + offset
group_offset <- c(sensor_a = -.4, sensor_b = .4)
forecast <- outer(trend, group_offset, "+")
print(data.frame(time = future, new_group_mean = trend, forecast))
sigma <- .2; tau <- .5
print(c(known_group_noise_sd = sigma, new_group_noise_sd = sqrt(sigma^2 + tau^2)))
stopifnot(all(forecast[, 1] < trend), all(forecast[, 2] > trend), sqrt(sigma^2 + tau^2) > sigma)
