# SPDX-License-Identifier: MIT
# Original serial reference utilities. Runtime code never compiles or downloads.

reference_assert <- function(condition, message) {
  if (!isTRUE(condition)) stop(message, call. = FALSE)
}

reference_close <- function(actual, expected, tolerance = 1e-5) {
  reference_assert(length(actual) == length(expected), "Reference dimensions differ")
  reference_assert(all(is.finite(actual)) && all(is.finite(expected)), "Nonfinite reference values")
  reference_assert(
    all(abs(actual - expected) <= tolerance * pmax(1, abs(expected))),
    "Independent numerical reference mismatch"
  )
}

reference_versions <- function() {
  packages <- c("TMB", "glmmTMB", "RTMB", "Matrix", "RcppEigen", "jsonlite", "digest")
  setNames(lapply(packages, function(name) as.character(utils::packageVersion(name))), packages)
}

reference_read_json <- function(path) {
  reference_assert(
    file.exists(path) && file.info(path)$size <= 4 * 1024^2,
    "Reference JSON is missing or exceeds the input bound"
  )
  jsonlite::fromJSON(path, simplifyVector = FALSE)
}

reference_hash <- function(path) digest::digest(file = path, algo = "sha256", serialize = FALSE)

reference_engine <- function(root, prepared) {
  root <- normalizePath(root, mustWork = TRUE)
  prepared <- normalizePath(prepared, mustWork = TRUE)
  manifest <- reference_read_json(file.path(prepared, "manifest.json"))
  reference_assert(identical(manifest$kind, "optional-r-tmb-glmmtmb-reference"), "Unknown prepared reference")
  reference_assert(identical(manifest$r_version, as.character(getRversion())), "R version differs from preparation")
  reference_assert(identical(manifest$architecture, R.version$arch), "Prepared native architecture differs")
  for (name in names(manifest$source_sha256)) {
    reference_assert(
      identical(reference_hash(file.path(root, name)), manifest$source_sha256[[name]]),
      paste("Prepared reference source changed:", name)
    )
  }
  for (name in names(manifest$packages)) {
    reference_assert(
      identical(as.character(utils::packageVersion(name)), manifest$packages[[name]]),
      paste("Prepared reference dependency changed:", name)
    )
  }
  for (name in names(manifest$package_files)) {
    package_root <- system.file(package = name)
    reference_assert(nzchar(package_root), paste("Missing prepared package:", name))
    for (path in names(manifest$package_files[[name]])) {
      reference_assert(
        identical(reference_hash(file.path(package_root, path)), manifest$package_files[[name]][[path]]),
        paste("Prepared dependency executable changed:", name, path)
      )
    }
  }
  list(root = root, prepared = prepared, manifest = manifest)
}

reference_objective <- function(engine, model, data, parameters, random = NULL, map = list()) {
  reference_assert(is.list(data) && is.list(parameters), "Supply explicit live R data/parameter lists")
  reference_assert(is.numeric(data$y) && length(data$y) >= 1L && length(data$y) <= 4096L &&
    all(is.finite(data$y)), "Custom reference response is invalid or exceeds4096 rows")
  n <- length(data$y)
  finite <- function(value, size) is.numeric(value) && length(value) == size && all(is.finite(value))
  if (model == "gaussian_linear") {
    p <- ncol(data$X)
    reference_assert(is.matrix(data$X) && nrow(data$X) == n && p <= 32L && all(is.finite(data$X)), "Invalid Gaussian design")
    reference_assert(finite(parameters$beta, p) && finite(data$prior_center, p) &&
      finite(data$prior_precision, p) && all(data$prior_precision >= 0) &&
      finite(parameters$log_sigma, 1L), "Invalid Gaussian parameters/prior")
  } else {
    groups <- if (model == "gaussian_random_slope") nrow(parameters$z) else if (model == "nonlinear_growth") length(parameters$u) else data$groups
    reference_assert(length(groups) == 1L && groups >= 1L && groups <= 64L &&
      length(data$group) == n && all(is.finite(data$group)) &&
      all(data$group %% 1 == 0 & data$group >= 0 & data$group < groups), "Invalid complete-group identities")
    reference_assert(setequal(data$group, seq_len(groups) - 1L), "Complete-group identities must be contiguous")
    if (model == "gaussian_random_slope") {
      reference_assert(finite(data$x, n) && finite(parameters$beta, 2L) && finite(parameters$log_sd, 3L) &&
        finite(parameters$correlation_coordinate, 1L) && is.matrix(parameters$z) &&
        ncol(parameters$z) == 2L && all(is.finite(parameters$z)), "Invalid random-slope inputs")
    } else if (model == "nonlinear_growth") {
      reference_assert(finite(data$time, n) && all(data$time >= 0) && finite(parameters$theta, 5L) &&
        all(is.finite(parameters$u)), "Invalid nonlinear growth inputs")
    } else if (model == "panel_ar1") {
      reference_assert(is.matrix(data$X) && nrow(data$X) == n && ncol(data$X) == 3L && all(is.finite(data$X)) &&
        finite(data$time, n) && all(data$time %% 1 == 0 & data$time >= 0 & data$time <= 1000) &&
        finite(data$time_scale, 1L) && data$time_scale > 0, "Invalid panel design/time grid")
      reference_assert(
        !anyDuplicated(paste(data$group, data$time)) && max(table(data$group)) <= 64L,
        "Panel units require unique times and at most64 observations"
      )
      reference_assert(finite(parameters$beta, 3L) && finite(parameters$log_sigma, 1L) &&
        finite(parameters$log_tau, 2L) && finite(parameters$phi_coordinate, 1L) &&
        finite(parameters$scale_trend, 1L), "Invalid panel parameters")
    } else {
      stop("Unknown prepared custom model", call. = FALSE)
    }
  }
  entry <- engine$manifest$models[[model]]
  reference_assert(!is.null(entry), "Model is absent from the prepared trusted registry")
  library <- file.path(engine$prepared, entry$library)
  reference_assert(identical(reference_hash(library), entry$sha256), "Prepared model binary changed")
  if (!model %in% names(getLoadedDLLs())) dyn.load(library)
  TMB::MakeADFun(
    data = data, parameters = parameters, random = random, map = map,
    DLL = model, silent = TRUE
  )
}

reference_restore_fit <- function(objective, parameters, expected_loss) {
  restored_loss <- objective$fn(parameters)
  reference_close(restored_loss, expected_loss, 1e-7)
  full <- objective$env$last.par
  reference_assert(is.numeric(full) && all(is.finite(full)), "TMB restored state is nonfinite")
  reference_assert(is.function(objective$env$lfixed), "Pinned TMB parameter layout is unavailable")
  reference_close(full[objective$env$lfixed()], parameters, 1e-12)
  # TMB1.9.25 parList's first argument is the FIXED vector. Supplying a full
  # last.par.best vector there can recycle random coordinates into fixed slots.
  list(
    parameters = objective$env$parList(x = parameters, par = full),
    report = objective$report(full), restored_loss = restored_loss
  )
}

reference_fit <- function(objective, lower = rep(-Inf, length(objective$par)),
                          upper = rep(Inf, length(objective$par)), tolerance = 2e-4) {
  fit <- nlminb(objective$par, objective$fn, objective$gr,
    lower = lower, upper = upper,
    control = list(iter.max = 1500, eval.max = 3000, rel.tol = 1e-11)
  )
  gradient <- as.numeric(objective$gr(fit$par))
  projected <- gradient
  projected[fit$par <= lower + 1e-7 & gradient > 0] <- 0
  projected[fit$par >= upper - 1e-7 & gradient < 0] <- 0
  reference_assert(
    fit$convergence == 0L && all(is.finite(fit$par)) && is.finite(fit$objective),
    paste("TMB optimization failed:", fit$message)
  )
  reference_assert(max(abs(projected)) < tolerance, "TMB projected score is too large")
  objective$fn(fit$par)
  uncertainty <- TMB::sdreport(objective, par.fixed = fit$par)
  reference_assert(isTRUE(uncertainty$pdHess), "TMB fixed-parameter curvature is not positive definite")
  restored <- reference_restore_fit(objective, fit$par, fit$objective)
  list(
    objective = objective, optimizer = fit, parameters = restored$parameters, report = restored$report,
    diagnostics = list(
      converged = TRUE, objective = fit$objective,
      raw_score_inf = max(abs(gradient)), projected_score_inf = max(abs(projected)),
      iterations = fit$iterations, pd_hessian = uncertainty$pdHess,
      restored_objective = restored$restored_loss
    ),
    uncertainty = uncertainty
  )
}

reference_gradient <- function(objective, theta, tolerance = 2e-4) {
  gradient <- as.numeric(objective$gr(theta))
  steps <- c(2e-5, 5e-6)
  errors <- vapply(steps, function(step) {
    numerical <- vapply(seq_along(theta), function(j) {
      upper <- lower <- theta
      upper[j] <- upper[j] + step
      lower[j] <- lower[j] - step
      (objective$fn(upper) - objective$fn(lower)) / (2 * step)
    }, numeric(1))
    reference_close(gradient, numerical, tolerance)
    max(abs(gradient - numerical))
  }, numeric(1))
  list(steps = steps, maximum_absolute_errors = errors)
}

reference_gaussian_nll <- function(residual, covariance) {
  factor <- chol(covariance)
  score <- backsolve(factor, forwardsolve(t(factor), residual))
  0.5 * (length(residual) * log(2 * pi) + 2 * sum(log(diag(factor))) + sum(residual * score))
}

reference_conditional <- function(history_y, history_mean, future_mean, history_covariance,
                                  cross_covariance, future_covariance) {
  factor <- chol(history_covariance)
  solve_history <- function(value) backsolve(factor, forwardsolve(t(factor), value))
  mean <- as.numeric(future_mean + cross_covariance %*% solve_history(history_y - history_mean))
  covariance <- future_covariance - cross_covariance %*% solve_history(t(cross_covariance))
  covariance <- (covariance + t(covariance)) / 2
  reference_assert(all(diag(covariance) > 0), "Conditional forecast variance is not positive")
  list(
    mean = mean, covariance = covariance, sd = sqrt(diag(covariance)),
    uncertainty = "observation/latent uncertainty at fitted population parameters"
  )
}

reference_prediction_metrics <- function(observed, prediction) {
  reference_assert(length(observed) == length(prediction$mean), "Forecast target dimensions differ")
  error <- observed - prediction$mean
  list(
    mse = mean(error^2), pointwise_coverage = mean(abs(error) <= qnorm(0.975) * prediction$sd),
    interval = "pointwise plug-in Gaussian 95%; population-parameter uncertainty excluded"
  )
}

reference_quadrature <- function(joint, mode, prior_sd, local_sd, tolerance = 1e-8) {
  reference_assert(is.finite(mode) && is.finite(prior_sd) && prior_sd > 0 &&
    is.finite(local_sd) && local_sd > 0, "Invalid quadrature mode/scale")
  shift <- joint(mode)
  reference_assert(is.finite(shift), "Quadrature centering value is nonfinite")
  kernel <- function(values) {
    vapply(values, function(value) {
      loss <- joint(value)
      reference_assert(
        length(loss) == 1L && !is.na(loss) && loss != -Inf,
        "Quadrature encountered an invalid joint density"
      )
      exp(shift - loss)
    }, numeric(1))
  }
  radius <- max(5, 8 * prior_sd, abs(mode) + 8 * local_sd)
  integrate_at <- function(bound) {
    pieces <- lapply(list(c(-bound, mode), c(mode, bound)), function(interval) {
      integrate(kernel, interval[1], interval[2],
        rel.tol = tolerance,
        abs.tol = tolerance * 1e-3, subdivisions = 1000L, stop.on.error = FALSE
      )
    })
    reference_assert(
      all(vapply(pieces, function(piece) identical(piece$message, "OK"), logical(1))),
      "Adaptive quadrature did not report successful integration"
    )
    value <- sum(vapply(pieces, function(piece) piece$value, numeric(1)))
    error <- sum(vapply(pieces, function(piece) piece$abs.error, numeric(1)))
    reference_assert(
      is.finite(value) && value > 0 && is.finite(error) && error >= 0 &&
        error <= max(tolerance * 10 * value, tolerance * 1e-3),
      "Quadrature integral/error is invalid or insufficiently accurate"
    )
    list(value = value, absolute_error = error, interval = c(-bound, bound))
  }
  inner <- integrate_at(radius)
  outer <- integrate_at(radius * 1.5)
  relative_change <- abs(outer$value - inner$value) / outer$value
  reference_assert(
    relative_change <= max(1e-7, 10 * (inner$absolute_error + outer$absolute_error) / outer$value),
    "Quadrature is unstable under interval expansion"
  )
  list(
    negative_log_integral = shift - log(outer$value),
    intervals = list(inner$interval, outer$interval),
    scaled_integrals = c(inner$value, outer$value),
    scaled_absolute_errors = c(inner$absolute_error, outer$absolute_error),
    relative_interval_change = relative_change, centering_loss = shift,
    boundary = "finite-domain numerical reference; interval stability is checked, omitted tails are not rigorously bounded"
  )
}

reference_simulation_summary <- function(simulations, family_name, observations, trials) {
  reference_assert(
    is.list(simulations) && length(simulations) == 2L,
    "Upstream simulator must return exactly two response sets"
  )
  lapply(simulations, function(value) {
    if (family_name == "betabinomial") {
      # The pinned glmmTMB binomialType branch returns one success/failure
      # matrix per simulation. Flattening it would average away the signal.
      reference_assert(
        is.matrix(value) && is.numeric(value) &&
          identical(dim(value), c(as.integer(observations), 2L)) &&
          all(is.finite(value)) && all(value >= 0 & value %% 1 == 0),
        "Beta-binomial simulation must contain finite integer success/failure counts"
      )
      reference_assert(
        length(trials) == observations && all(trials > 0 & trials %% 1 == 0) &&
          all(rowSums(value) == trials),
        "Beta-binomial simulated counts do not preserve trial totals"
      )
      list(
        shape = "success/failure count matrix", observations = observations,
        mean_success_count = mean(value[, 1]), mean_failure_count = mean(value[, 2]),
        mean_success_proportion = mean(value[, 1] / trials)
      )
    } else {
      reference_assert(is.numeric(value) && is.null(dim(value)) && length(value) == observations &&
        all(is.finite(value)), "Upstream scalar response simulation shape differs")
      if (family_name %in% c("poisson", "nbinom1", "nbinom2")) {
        reference_assert(all(value >= 0 & value %% 1 == 0), "Simulated count is outside support")
      } else if (family_name == "beta") {
        reference_assert(all(value > 0 & value < 1), "Simulated beta value is outside support")
      } else if (family_name %in% c("Gamma", "lognormal")) {
        reference_assert(all(value > 0), "Simulated positive response is outside support")
      }
      list(shape = "scalar response vector", observations = observations, mean_response = mean(value))
    }
  })
}
