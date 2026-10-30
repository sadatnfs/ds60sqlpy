# SPDX-License-Identifier: MIT
# Original calling code. The real glmmTMB library retains its AGPL-3 license.

reference_glmm_fit <- function(...) {
  observed_warnings <- character()
  model <- withCallingHandlers(
    glmmTMB::glmmTMB(...,
      control = glmmTMB::glmmTMBControl(optCtrl = list(iter.max = 1500, eval.max = 3000))
    ),
    warning = function(condition) observed_warnings <<- c(observed_warnings, conditionMessage(condition))
  )
  gradient <- as.numeric(model$obj$gr(model$fit$par))
  reference_assert(
    model$fit$convergence == 0L && isTRUE(model$sdr$pdHess),
    "Upstream glmmTMB fit failed convergence or positive-curvature checks"
  )
  reference_assert(
    all(is.finite(gradient)) && max(abs(gradient)) < 2e-3,
    "Upstream glmmTMB score is too large"
  )
  list(model = model, diagnostics = list(
    converged = TRUE, pd_hessian = model$sdr$pdHess,
    score_inf = max(abs(gradient)), objective = model$fit$objective, warnings = observed_warnings
  ))
}

reference_glmm_family_case <- function(engine, seed, family_name) {
  set.seed(seed)
  n <- 600L
  x <- runif(n, -1.5, 1.5)
  z <- rep(c(-0.5, 0.5), length.out = n)
  exposure <- runif(n, 0.6, 1.8)
  eta <- 0.3 + 0.65 * x
  mu <- exp(eta)
  probability <- plogis(eta)
  dispersion <- exp(1.1 + 0.35 * z)
  family <- switch(family_name,
    gaussian = gaussian(),
    poisson = poisson(),
    nbinom1 = glmmTMB::nbinom1(),
    nbinom2 = glmmTMB::nbinom2(),
    beta = glmmTMB::beta_family(),
    betabinomial = glmmTMB::betabinomial(),
    Gamma = Gamma(link = "log"),
    student = glmmTMB::t_family(),
    lognormal = glmmTMB::lognormal(link = "log"),
    stop("Unknown prepared family example", call. = FALSE)
  )
  trials <- rep(12L, n)
  y <- switch(family_name,
    gaussian = eta + rnorm(n, sd = exp(-0.5 + 0.3 * z)),
    poisson = rpois(n, mu * exposure),
    nbinom1 = rnbinom(n, mu = mu * exposure, size = mu * exposure / dispersion),
    nbinom2 = rnbinom(n, mu = mu * exposure, size = dispersion),
    beta = rbeta(n, probability * dispersion, (1 - probability) * dispersion),
    betabinomial = rbinom(n, trials, rbeta(n, probability * dispersion, (1 - probability) * dispersion)),
    Gamma = rgamma(n, shape = dispersion, scale = mu / dispersion),
    student = eta + 0.5 * rt(n, df = 4),
    lognormal = rlnorm(n, log(mu) - 0.5 * log1p(0.5^2 / mu^2), sqrt(log1p(0.5^2 / mu^2)))
  )
  data <- data.frame(y = y, x = x, z = z, exposure = exposure, trials = trials)
  formula <- if (family_name == "betabinomial") cbind(y, trials - y) ~ x else y ~ x
  if (family_name %in% c("poisson", "nbinom1", "nbinom2")) formula <- y ~ x + offset(log(exposure))
  dispersion_formula <- if (family_name %in% c("gaussian", "nbinom1", "nbinom2", "beta", "betabinomial", "Gamma")) ~z else ~1
  settings <- list(formula = formula, data = data, family = family, dispformula = dispersion_formula)
  if (family_name == "student") {
    settings$start <- list(psi = log(4))
    settings$map <- list(psi = factor(NA))
  }
  result <- do.call(reference_glmm_fit, settings)
  future <- data.frame(
    x = c(-1, 0, 1, 1.75), z = c(-0.5, 0.5, -0.5, 0.5), exposure = 1,
    trials = 12L
  )
  prediction <- as.numeric(predict(result$model, newdata = future, type = "response"))
  reference_assert(length(prediction) == nrow(future) && all(is.finite(prediction)), "Family predictions are invalid")
  if (family_name %in% c("beta", "betabinomial")) reference_assert(all(prediction > 0 & prediction < 1), "Probability prediction outside support")
  if (!family_name %in% c("gaussian", "student")) reference_assert(all(prediction > 0), "Positive-family prediction outside support")
  set.seed(seed + 100000L)
  simulations <- stats::simulate(result$model, nsim = 2)
  simulation_summary <- reference_simulation_summary(simulations, family_name, nrow(data), data$trials)
  list(
    case = "glmm_family", family = family_name, backend = "actual pinned upstream glmmTMB",
    target = "maximum likelihood with declared response/dispersion link", diagnostics = result$diagnostics,
    parameters = glmmTMB::fixef(result$model), predictions = prediction, future_covariates = future,
    future_has_response = FALSE, simulation_replicates = 2L,
    simulation_summary = simulation_summary,
    simulation_conditioning = "upstream fitted-model simulate with new random draws, conditional on fitted parameters",
    metrics = list(primary_estimate = unname(glmmTMB::fixef(result$model)$cond["x"]), truth = 0.65),
    fixture = list(training = data, future = future, generating_slope = 0.65)
  )
}

reference_glmm_zero_case <- function(engine, seed, hurdle = FALSE) {
  set.seed(seed)
  n <- 900L
  x <- runif(n, -1.5, 1.5)
  z <- rep(c(-0.5, 0.5), length.out = n)
  mu <- exp(0.5 + 0.6 * x)
  shape <- exp(1 + 0.25 * z)
  y <- rnbinom(n, mu = mu, size = shape)
  if (hurdle) {
    attempts <- 0L
    while (any(y == 0L)) {
      attempts <- attempts + 1L
      reference_assert(attempts < 1000L, "Positive-count generator exhausted its bound")
      selected <- which(y == 0L)
      y[selected] <- rnbinom(length(selected), mu = mu[selected], size = shape[selected])
    }
  }
  structural <- rbinom(n, 1, plogis(-1.2 + 0.5 * z)) == 1L
  y[structural] <- 0L
  data <- data.frame(y = y, x = x, z = z)
  family <- if (hurdle) glmmTMB::truncated_nbinom2() else glmmTMB::nbinom2()
  result <- reference_glmm_fit(y ~ x, data = data, family = family, ziformula = ~z, dispformula = ~z)
  future <- data.frame(x = c(-1, 0, 1), z = c(-0.5, 0.5, -0.5))
  conditional <- as.numeric(predict(result$model, newdata = future, type = "conditional"))
  zero_probability <- as.numeric(predict(result$model, newdata = future, type = "zprob"))
  response <- as.numeric(predict(result$model, newdata = future, type = "response"))
  reference_close(response, conditional * (1 - zero_probability), 1e-10)
  reference_assert(all(zero_probability > 0 & zero_probability < 1), "Invalid structural-zero probability")
  list(
    case = if (hurdle) "glmm_hurdle" else "glmm_zero_inflation",
    backend = "actual pinned upstream glmmTMB", diagnostics = result$diagnostics,
    parameters = glmmTMB::fixef(result$model), conditional_mean = conditional,
    zero_probability = zero_probability, response_mean = response, future_has_response = FALSE,
    interpretation = if (hurdle) {
      "positive-count truncated component plus separate zero hurdle"
    } else {
      "structural zeros plus ordinary NB2 component zeros"
    },
    metrics = list(primary_estimate = unname(glmmTMB::fixef(result$model)$cond["x"]), truth = 0.6),
    fixture = list(training = data, future = future, structural_zero = structural)
  )
}

reference_glmm_map_case <- function(engine, seed) {
  set.seed(seed)
  x <- seq(-2, 2, length.out = 200)
  y <- rbinom(length(x), 1, plogis(-0.2 + 2.2 * x))
  data <- data.frame(y = y, x = x)
  priors <- data.frame(
    prior = c("normal(0,3)", "normal(0.3,1)"),
    class = c("fixef", "fixef"), coef = c("(Intercept)", "x")
  )
  result <- reference_glmm_fit(y ~ x, data = data, family = binomial(), priors = priors)
  X <- cbind(1, x)
  center <- c(0, 0.3)
  precision <- c(1 / 9, 1)
  fn <- function(beta) {
    eta <- as.numeric(X %*% beta)
    sum(pmax(eta, 0) + log1p(exp(-abs(eta))) - y * eta) + sum(precision * (beta - center)^2) / 2
  }
  gr <- function(beta) as.numeric(crossprod(X, plogis(X %*% beta) - y)) + precision * (beta - center)
  independent <- optim(c(0, 0), fn, gr, method = "BFGS", control = list(reltol = 1e-12, maxit = 1000))
  reference_assert(
    independent$convergence == 0L && max(abs(gr(independent$par))) < 1e-4,
    "Independent MAP oracle did not converge"
  )
  actual <- as.numeric(glmmTMB::fixef(result$model)$cond)
  reference_close(actual, independent$par, 1e-4)
  list(
    case = "glmm_map", backend = "actual pinned upstream glmmTMB", parameters = actual,
    independent_map = independent$par, priors = priors, diagnostics = result$diagnostics,
    target = "MAP in coefficient coordinates with proper nonzero-mean Gaussian prior; not posterior sampling",
    metrics = list(primary_estimate = actual[2], truth = 2.2), fixture = list(training = data)
  )
}

reference_glmm_covariance_case <- function(engine, seed, structure) {
  set.seed(seed)
  groups <- 80L
  times <- 0:5
  size <- length(times)
  correlation <- switch(structure,
    ar1 = 0.55^abs(outer(times, times, "-")),
    ou = exp(-0.6 * abs(outer(times, times, "-"))),
    cs = matrix(0.3, size, size) + diag(0.7, size),
    diag = diag(size),
    toep = 0.5^abs(outer(times, times, "-")),
    us = 0.4^abs(outer(times, times, "-")),
    stop("Unknown prepared covariance example", call. = FALSE)
  )
  scales <- if (structure %in% c("diag", "cs", "toep", "us")) seq(0.4, 0.7, length.out = size) else rep(0.6, size)
  covariance <- outer(scales, scales) * correlation
  responses <- matrix(rnorm(groups * size), groups) %*% chol(covariance) + 1.2
  data <- data.frame(
    y = as.vector(t(responses)), time = rep(times, groups),
    time_factor = factor(rep(times, groups), levels = times),
    group = factor(rep(seq_len(groups), each = size))
  )
  data$position <- glmmTMB::numFactor(data$time)
  formula <- switch(structure,
    ar1 = y ~ 1 + ar1(time_factor + 0 | group),
    ou = y ~ 1 + ou(position + 0 | group),
    cs = y ~ 1 + cs(time_factor + 0 | group),
    diag = y ~ 1 + diag(time_factor + 0 | group),
    toep = y ~ 1 + toep(time_factor + 0 | group),
    us = y ~ 1 + us(time_factor + 0 | group)
  )
  result <- reference_glmm_fit(formula, data = data, family = gaussian(), dispformula = ~0)
  estimated <- as.matrix(glmmTMB::VarCorr(result$model)$cond$group)
  reference_assert(
    identical(dim(estimated), c(size, size)) && min(eigen(estimated, symmetric = TRUE)$values) > 0,
    "Fitted covariance must be positive definite with all declared levels"
  )
  response <- as.numeric(predict(result$model, type = "response"))
  reference_assert(length(response) == nrow(data), "Structured covariance prediction lost observations")
  list(
    case = "glmm_covariance", structure = structure, backend = "actual pinned upstream glmmTMB",
    diagnostics = result$diagnostics, estimated_covariance = estimated, generating_covariance = covariance,
    relative_covariance_error = sqrt(sum((estimated - covariance)^2) / sum(covariance^2)),
    identifiability = "residual dispersion fixed near zero; do not add an unidentified duplicate diagonal component",
    metrics = list(primary_estimate = unname(glmmTMB::fixef(result$model)$cond[1]), truth = 1.2),
    fixture = list(training = data, covariance = covariance)
  )
}

reference_glmm_ar_forecast_case <- function(engine, seed) {
  set.seed(seed)
  groups <- 48L
  times <- 0:11
  future_times <- 12:14
  tau <- 0.65
  phi <- 0.6
  sigma <- 0.25
  covariance <- tau^2 * phi^abs(outer(times, times, "-")) + diag(sigma^2, length(times))
  x <- rep(sin(times / 3), groups)
  responses <- matrix(rnorm(groups * length(times)), groups) %*% chol(covariance)
  y <- 0.8 + 0.4 * x + as.vector(t(responses))
  data <- data.frame(
    y = y, x = x, time_factor = factor(rep(times, groups), levels = times),
    group = factor(rep(seq_len(groups), each = length(times)))
  )
  result <- reference_glmm_fit(y ~ x + ar1(time_factor + 0 | group), data = data, family = gaussian())
  beta <- glmmTMB::fixef(result$model)$cond
  latent <- as.matrix(glmmTMB::VarCorr(result$model)$cond$group)
  estimated_tau2 <- latent[1, 1]
  estimated_phi <- latent[1, 2] / estimated_tau2
  estimated_sigma2 <- stats::sigma(result$model)^2
  future_x <- sin(future_times / 3)
  historical_mean <- beta[1] + beta[2] * x[seq_along(times)]
  future_mean <- beta[1] + beta[2] * future_x
  future_covariance <- estimated_tau2 * estimated_phi^abs(outer(future_times, future_times, "-")) +
    diag(estimated_sigma2, length(future_times))
  prediction <- reference_conditional(
    y[seq_along(times)], historical_mean, future_mean,
    latent + diag(estimated_sigma2, length(times)),
    estimated_tau2 * estimated_phi^abs(outer(future_times, times, "-")), future_covariance
  )
  list(
    case = "glmm_ar_forecast", backend = "upstream glmmTMB fit plus independent Gaussian conditioning",
    diagnostics = result$diagnostics, fixed_effects = beta, latent_phi = estimated_phi,
    latent_marginal_sd = sqrt(estimated_tau2), observation_sd = sqrt(estimated_sigma2),
    forecast = prediction, future_time = future_times, future_covariates = future_x,
    future_has_response = FALSE,
    interpretation = "latent AR1 plus separate measurement noise; differs from directly observed AR1",
    metrics = list(primary_estimate = estimated_phi, truth = phi), fixture = list(training = data)
  )
}
