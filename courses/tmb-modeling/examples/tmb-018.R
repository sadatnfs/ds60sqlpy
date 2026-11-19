h <- 1:6; phi <- .7; tau <- .8; sigma <- .3; current_state <- 1.2; beta <- 2
print(data.frame(horizon = h, mean = beta + phi^h * current_state, innovation_variance = tau^2 * (1 - phi^(2 * h)) + sigma^2))
intercept_se <- .1
new_observation_sd <- sqrt(intercept_se^2 + tau^2 + sigma^2)
print(c(intercept_se = intercept_se, new_group_observation_sd = new_observation_sd))
stopifnot(new_observation_sd > intercept_se, all(diff(tau^2 * (1 - phi^(2 * h)) + sigma^2) > 0))
