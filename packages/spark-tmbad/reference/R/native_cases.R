# SPDX-License-Identifier: MIT
# Original finite serial studies using prepared TMB models and independent formulas.

reference_ridge_case <- function(engine, seed) {
  set.seed(seed)
  x <- seq(-2, 2, length.out = 160)
  X <- cbind(intercept = 1, slope = x)
  sigma <- 0.7
  y <- as.numeric(X %*% c(1.5, 0.8) + rnorm(length(x), sd = sigma))
  center <- c(0, 0.3)
  precision <- c(0, 12)
  objective <- reference_objective(engine, "gaussian_linear",
    list(X = X, y = y, prior_center = center, prior_precision = precision),
    list(beta = c(0, 0), log_sigma = log(sigma)),
    map = list(log_sigma = factor(NA))
  )
  gradient <- reference_gradient(objective, c(0.2, 0.1))
  fitted <- reference_fit(objective)
  exact <- as.numeric(solve(
    crossprod(X) / sigma^2 + diag(precision),
    crossprod(X, y) / sigma^2 + precision * center
  ))
  reference_close(fitted$optimizer$par, exact, 1e-7)
  future_X <- cbind(1, c(2.5, 3, 3.5))
  future <- as.numeric(future_X %*% exact)
  list(
    case = "gaussian_ridge", target = "selected-coefficient Gaussian MAP; intercept and known log-scale unpenalized",
    parameters = fitted$optimizer$par, parameter_names = colnames(X),
    prior = list(center = center, precision = precision, measure = "d beta"),
    diagnostics = fitted$diagnostics, gradient_check = gradient, analytic_solution = exact,
    future = list(x = future_X[, 2], mean = future, future_has_response = FALSE),
    metrics = list(primary_estimate = exact[2], truth = 0.8),
    fixture = list(training = data.frame(x = x, y = y), future_X = future_X, prior_center = center, prior_precision = precision)
  )
}

reference_random_slope_case <- function(engine, seed) {
  set.seed(seed)
  groups <- 32L
  per_group <- 12L
  x <- rep(seq(-1.5, 1.5, length.out = per_group), groups)
  group <- rep(seq_len(groups) - 1L, each = per_group)
  truth <- list(beta = c(1.2, 0.7), sigma = 0.4, tau0 = 0.65, tau1 = 0.3, rho = -0.25)
  D <- matrix(c(
    truth$tau0^2, truth$rho * truth$tau0 * truth$tau1,
    truth$rho * truth$tau0 * truth$tau1, truth$tau1^2
  ), 2)
  effects <- matrix(rnorm(groups * 2), groups, 2) %*% chol(D)
  y <- truth$beta[1] + truth$beta[2] * x + effects[group + 1L, 1] + effects[group + 1L, 2] * x +
    rnorm(length(x), sd = truth$sigma)
  objective <- reference_objective(engine, "gaussian_random_slope", list(x = x, y = y, group = group),
    list(
      beta = c(0.8, 0.4), log_sd = log(c(0.5, 0.5, 0.25)),
      correlation_coordinate = 0, z = matrix(0, groups, 2)
    ),
    random = "z"
  )
  dense <- function(theta) {
    sigma <- exp(theta[3])
    tau <- exp(theta[4:5])
    rho <- tanh(theta[6])
    covariance <- matrix(c(tau[1]^2, prod(tau) * rho, prod(tau) * rho, tau[2]^2), 2)
    sum(vapply(seq_len(groups) - 1L, function(g) {
      selected <- which(group == g)
      Z <- cbind(1, x[selected])
      reference_gaussian_nll(
        y[selected] - as.numeric(Z %*% theta[1:2]),
        Z %*% covariance %*% t(Z) + diag(sigma^2, length(selected))
      )
    }, numeric(1)))
  }
  exact_loss <- dense(objective$par)
  laplace_loss <- objective$fn(objective$par)
  reference_close(laplace_loss, exact_loss, 1e-8)
  fitted <- reference_fit(objective,
    lower = c(-Inf, -Inf, rep(-5, 3), -3),
    upper = c(Inf, Inf, rep(3, 3), 3)
  )
  theta <- fitted$optimizer$par
  sigma <- exp(theta[3])
  tau <- exp(theta[4:5])
  rho <- tanh(theta[6])
  fitted_D <- matrix(c(tau[1]^2, prod(tau) * rho, prod(tau) * rho, tau[2]^2), 2)
  selected <- which(group == 0L)
  Z <- cbind(1, x[selected])
  future_x <- c(-1.8, 0.6, 2)
  future_Z <- cbind(1, future_x)
  prediction <- reference_conditional(
    y[selected], as.numeric(Z %*% theta[1:2]),
    as.numeric(future_Z %*% theta[1:2]), Z %*% fitted_D %*% t(Z) + diag(sigma^2, length(selected)),
    future_Z %*% fitted_D %*% t(Z), future_Z %*% fitted_D %*% t(future_Z) + diag(sigma^2, 3)
  )
  conditional_effect <- as.numeric(fitted_D %*% t(Z) %*%
    solve(Z %*% fitted_D %*% t(Z) + diag(sigma^2, length(selected)), y[selected] - Z %*% theta[1:2]))
  reference_close(as.numeric(fitted$report$effects[1, ]), conditional_effect, 1e-6)
  set.seed(seed + 100000L)
  future_y <- as.numeric(future_Z %*% truth$beta + future_Z %*% effects[1, ] + rnorm(3, sd = truth$sigma))
  metrics <- reference_prediction_metrics(future_y, prediction)
  metrics$primary_estimate <- theta[2]
  metrics$truth <- truth$beta[2]
  list(
    case = "gaussian_random_slope", target = "marginal ML; Gaussian Laplace equals exact integration",
    parameters = theta, diagnostics = fitted$diagnostics,
    exact_marginal_loss_difference = laplace_loss - exact_loss,
    prediction = prediction, future_x = future_x, future_has_response = FALSE,
    new_group_mean = as.numeric(future_Z %*% theta[1:2]),
    new_group_sd = sqrt(diag(future_Z %*% fitted_D %*% t(future_Z)) + sigma^2), metrics = metrics,
    fixture = list(training = data.frame(group = group, x = x, y = y), future_x = future_x, future_y = future_y, truth = truth)
  )
}

reference_growth_case <- function(engine, seed) {
  set.seed(seed)
  groups <- 24L
  times <- seq(0, 8, length.out = 14)
  time <- rep(times, groups)
  group <- rep(seq_len(groups) - 1L, each = length(times))
  truth <- c(0.5, log(2.5), log(0.45), log(0.18), log(0.2))
  u <- rnorm(groups, sd = exp(truth[5]))
  y <- truth[1] + exp(truth[2] + u[group + 1L]) * (1 - exp(-exp(truth[3]) * time)) +
    rnorm(length(time), sd = exp(truth[4]))
  objective <- reference_objective(engine, "nonlinear_growth", list(time = time, y = y, group = group),
    list(theta = c(0.3, log(2), log(0.35), log(0.3), log(0.25)), u = rep(0, groups)),
    random = "u"
  )
  fitted <- reference_fit(objective, lower = c(-5, -3, -5, -6, -6), upper = c(5, 4, 2, 2, 2))
  theta <- fitted$parameters$theta
  latent <- fitted$parameters$u
  future_time <- c(9, 10, 11)
  curve <- 1 - exp(-exp(theta[3]) * future_time)
  conditional <- theta[1] + exp(theta[2] + latent[1]) * curve
  tau2 <- exp(2 * theta[5])
  integrated <- theta[1] + exp(theta[2] + tau2 / 2) * curve
  new_variance <- exp(2 * theta[4]) + exp(2 * theta[2]) * curve^2 * (exp(2 * tau2) - exp(tau2))
  reference_assert(
    all(integrated > theta[1] + exp(theta[2]) * curve),
    "New-group mean must integrate nonlinear latent amplitude"
  )
  # Independent quadrature for a single group's likelihood, compared honestly to
  # its Laplace approximation rather than asserted to be exact for nonlinear u.
  selected <- which(group == 0L)
  joint <- function(value) {
    mean <- theta[1] + exp(theta[2] + value) * (1 - exp(-exp(theta[3]) * time[selected]))
    -sum(dnorm(y[selected], mean, exp(theta[4]), log = TRUE)) - dnorm(value, 0, exp(theta[5]), log = TRUE)
  }
  mode_bound <- max(5, 8 * exp(theta[5]))
  mode <- optimize(joint, c(-mode_bound, mode_bound))$minimum
  reference_assert(abs(mode) < 0.98 * mode_bound, "Nonlinear mode touches its declared search bound")
  steps <- c(1e-4, 5e-5)
  curvatures <- vapply(steps, function(step) {
    (joint(mode + step) - 2 * joint(mode) + joint(mode - step)) / step^2
  }, numeric(1))
  reference_assert(all(is.finite(curvatures)) && all(curvatures > 0), "Nonlinear mode curvature is invalid")
  reference_close(curvatures[1], curvatures[2], 2e-3)
  quadrature <- reference_quadrature(joint, mode, exp(theta[5]), 1 / sqrt(curvatures[2]))
  laplace_group_loss <- joint(mode) + 0.5 * log(curvatures[2]) - 0.5 * log(2 * pi)
  # A separate random stream generates an unseen group's held-out observations.
  # These responses are never supplied to the fit or prediction calculation.
  set.seed(seed + 200000L)
  future_u <- rnorm(1, sd = exp(truth[5]))
  future_y <- truth[1] + exp(truth[2] + future_u) *
    (1 - exp(-exp(truth[3]) * future_time)) + rnorm(length(future_time), sd = exp(truth[4]))
  metrics <- reference_prediction_metrics(future_y, list(mean = integrated, sd = sqrt(new_variance)))
  metrics$interval <- "pointwise mean plus/minus normal quantile times mixture SD; not exact mixture quantiles"
  metrics$primary_estimate <- exp(theta[3])
  metrics$truth <- exp(truth[3])
  list(
    case = "nonlinear_growth", target = "nonlinear mixed-model marginal ML via approximate random-effect Laplace",
    parameters = theta, diagnostics = fitted$diagnostics,
    future_time = future_time, future_has_response = FALSE,
    known_group_conditional_mode_mean = conditional,
    new_group_latent_integrated_mean = integrated, new_group_observation_sd = sqrt(new_variance),
    nonlinear_laplace_check = list(
      quadrature = quadrature, laplace_loss = laplace_group_loss,
      curvature_steps = steps, curvature_estimates = curvatures,
      difference = laplace_group_loss - quadrature$negative_log_integral
    ),
    uncertainty = "new-group observation/latent moments; population-parameter uncertainty excluded",
    metrics = metrics,
    fixture = list(training = data.frame(group = group, time = time, y = y),
      future_time = future_time, heldout_future_y = future_y, truth = truth)
  )
}

reference_panel_covariance <- function(left, right, parameters, time_scale) {
  tau <- exp(parameters$log_tau)
  phi <- tanh(parameters$phi_coordinate)
  left_scale <- exp(parameters$log_sigma + parameters$scale_trend * left / time_scale)
  right_scale <- exp(parameters$log_sigma + parameters$scale_trend * right / time_scale)
  tau[1]^2 + tau[2]^2 * outer(left / time_scale, right / time_scale) +
    outer(left_scale, right_scale) * phi^abs(outer(left, right, "-"))
}

reference_panel_case <- function(engine, seed) {
  set.seed(seed)
  groups <- 24L
  time_scale <- 12
  training_time <- 0:15
  future_time <- 16:18
  truth <- list(
    beta = c(1, 0.35, 0.7), log_sigma = log(0.35), log_tau = log(c(0.5, 0.25)),
    phi_coordinate = atanh(0.55), scale_trend = 0.15
  )
  group <- rep(seq_len(groups) - 1L, each = length(training_time))
  time <- rep(training_time, groups)
  x <- rep(sin(training_time / 3), groups) + rnorm(length(time), sd = 0.3)
  X <- cbind(1, time / time_scale, x)
  covariance <- reference_panel_covariance(training_time, training_time, truth, time_scale)
  errors <- matrix(rnorm(groups * length(training_time)), groups) %*% chol(covariance)
  y <- as.numeric(X %*% truth$beta + as.vector(t(errors)))
  objective <- reference_objective(
    engine, "panel_ar1",
    list(X = X, y = y, group = group, time = as.integer(time), groups = groups, time_scale = time_scale),
    list(
      beta = c(0.8, 0.2, 0.5), log_sigma = log(0.4), log_tau = log(c(0.4, 0.2)),
      phi_coordinate = atanh(0.3), scale_trend = 0.1
    )
  )
  initial <- objective$env$parList(objective$par)
  initial_covariance <- reference_panel_covariance(training_time, training_time, initial, time_scale)
  independent <- sum(vapply(seq_len(groups) - 1L, function(g) {
    selected <- which(group == g)
    reference_gaussian_nll(y[selected] - as.numeric(X[selected, ] %*% initial$beta), initial_covariance)
  }, numeric(1)))
  reference_close(objective$fn(objective$par), independent, 1e-8)
  gradient <- reference_gradient(objective, objective$par)
  fitted <- reference_fit(objective,
    lower = c(rep(-Inf, 3), -5, -5, -5, -3, -1),
    upper = c(rep(Inf, 3), 2, 2, 2, 3, 1)
  )
  parameters <- fitted$parameters
  selected <- which(group == 0L)
  future_x <- sin(future_time / 3)
  future_X <- cbind(1, future_time / time_scale, future_x)
  prediction <- reference_conditional(
    y[selected], as.numeric(X[selected, ] %*% parameters$beta),
    as.numeric(future_X %*% parameters$beta),
    reference_panel_covariance(training_time, training_time, parameters, time_scale),
    reference_panel_covariance(future_time, training_time, parameters, time_scale),
    reference_panel_covariance(future_time, future_time, parameters, time_scale)
  )
  truth_future <- reference_conditional(
    y[selected], as.numeric(X[selected, ] %*% truth$beta), as.numeric(future_X %*% truth$beta),
    covariance, reference_panel_covariance(future_time, training_time, truth, time_scale),
    reference_panel_covariance(future_time, future_time, truth, time_scale)
  )
  set.seed(seed + 200000L)
  future_y <- truth_future$mean + as.numeric(t(chol(truth_future$covariance)) %*% rnorm(length(future_time)))
  metrics <- reference_prediction_metrics(future_y, prediction)
  metrics$primary_estimate <- parameters$beta[3]
  metrics$truth <- truth$beta[3]
  return(list(
    case = "panel_ar1", target = "exact Gaussian marginal ML with panel intercept/slope and heteroskedastic observed AR1",
    parameters = parameters, diagnostics = fitted$diagnostics, gradient_check = gradient,
    independent_initial_loss = independent, forecast = prediction, future_time = future_time,
    future_covariate_scenario = future_x, future_has_response = FALSE,
    fit_time_maximum = max(training_time), forecast_time_minimum = min(future_time),
    provenance = "Original synthetic panel inspired by AFModel's scientific topics; no operational code or data reused",
    metrics = metrics,
    fixture = list(training = data.frame(group = group, time = time, x = x, y = y),
      future_time = future_time, future_x = future_x, heldout_future_y = future_y, truth = truth)
  ))
}
