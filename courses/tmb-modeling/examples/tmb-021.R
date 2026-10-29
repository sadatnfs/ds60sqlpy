time <- 0:5; trend <- 3 * exp(-.5 * time) + 1
residual_a <- c(.3, .2, -.1, .1, .05, .02)
residual_b <- c(-.2, -.1, .1, .2, .1, .04)
print(data.frame(time = time, trend = trend, panel_a = trend - .4 + residual_a, panel_b = trend + .4 + residual_b))
phi <- .6; horizon <- 1:3
print(data.frame(horizon = horizon, panel_a_residual = phi^horizon * tail(residual_a, 1), panel_b_residual = phi^horizon * tail(residual_b, 1)))
stopifnot(all(abs(phi^horizon * tail(residual_a, 1)) < abs(tail(residual_a, 1))))
