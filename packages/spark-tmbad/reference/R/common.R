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

reference_newton_seed <- function(objective, start, lower, upper, tolerance) {
  # This is an opt-in local seed for a fresh genuine optimizer attempt. It is
  # never itself reported as an accepted fit or given a synthetic status zero.
  reference_assert(length(start) == 5L && length(lower) == 5L && length(upper) == 5L &&
    all(is.finite(c(start, lower, upper))) && all(start > lower + 1e-5) &&
    all(start < upper - 1e-5), "Newton seed requires five interior bounded coordinates")
  evaluate <- function(par) {
    value <- as.numeric(objective$fn(par))
    gradient <- as.numeric(objective$gr(par))
    reference_assert(length(value) == 1L && is.finite(value) && length(gradient) == 5L &&
      all(is.finite(gradient)), "Newton seed objective/gradient is nonfinite")
    list(objective = value, gradient = gradient, score_inf = max(abs(gradient)))
  }
  initial <- evaluate(start)
  hessian <- function(width) {
    result <- matrix(0, 5L, 5L)
    for (j in seq_len(5L)) {
      step <- width * max(1, abs(start[j]))
      high <- low <- start
      high[j] <- high[j] + step
      low[j] <- low[j] - step
      reference_assert(
        high[j] < upper[j] && low[j] > lower[j],
        "Newton finite differences leave declared bounds"
      )
      result[, j] <- (evaluate(high)$gradient - evaluate(low)$gradient) / (2 * step)
    }
    result
  }
  wide <- hessian(1e-4)
  narrow <- hessian(5e-5)
  repeated <- evaluate(start)
  reference_assert(
    abs(initial$objective - repeated$objective) <= 1e-9 &&
      max(abs(initial$gradient - repeated$gradient)) <= 1e-7,
    "Newton marginal gradient or inner-mode branch drifted"
  )
  reference_assert(
    all(is.finite(wide)) && all(is.finite(narrow)) &&
      max(abs(wide - narrow)) <= 1e-3 &&
      max(abs(wide - t(wide))) <= 1e-3 && max(abs(narrow - t(narrow))) <= 1e-3,
    "Newton marginal Hessian is unstable or asymmetric"
  )
  matrix <- (wide + t(wide) + narrow + t(narrow)) / 4
  eigenvalues <- eigen(matrix, symmetric = TRUE, only.values = TRUE)$values
  reference_assert(
    all(is.finite(eigenvalues)) && min(eigenvalues) > 0 &&
      max(eigenvalues) / min(eigenvalues) <= 1e6,
    "Newton marginal Hessian is not positive definite and well conditioned"
  )
  factor <- chol(matrix)
  direction <- as.numeric(backsolve(factor, forwardsolve(t(factor), -repeated$gradient)))
  reference_assert(
    all(is.finite(direction)) && max(abs(direction)) <= 0.1 &&
      sum(repeated$gradient * direction) < 0,
    "Newton direction is unbounded or is not descent"
  )
  trials <- list()
  for (index in 0:7) {
    alpha <- 2^(-index)
    candidate <- start + alpha * direction
    if (any(candidate <= lower) || any(candidate >= upper)) {
      trials[[length(trials) + 1L]] <- list(alpha = alpha, feasible = FALSE)
      next
    }
    inspected <- evaluate(candidate)
    trials[[length(trials) + 1L]] <- list(
      alpha = alpha, feasible = TRUE, objective = inspected$objective,
      score_inf = inspected$score_inf
    )
    if (inspected$objective < repeated$objective &&
      inspected$score_inf < min(tolerance, repeated$score_inf)) {
      confirmed <- evaluate(candidate)
      reference_assert(
        abs(confirmed$objective - inspected$objective) <= 1e-12 &&
          max(abs(confirmed$gradient - inspected$gradient)) <= 1e-7 &&
          confirmed$objective < repeated$objective &&
          confirmed$score_inf < min(tolerance, repeated$score_inf),
        "Newton selected trial objective or gradient drifted"
      )
      return(list(
        par = candidate, objective = confirmed$objective,
        diagnostics = list(
          initial_objective = repeated$objective, initial_score_inf = repeated$score_inf,
          hessian_widths = c(1e-4, 5e-5),
          hessian_max_scale_difference = max(abs(wide - narrow)),
          hessian_max_asymmetry = max(abs(wide - t(wide)), abs(narrow - t(narrow))),
          hessian_eigenvalues = eigenvalues,
          direction = direction, directional_derivative = sum(repeated$gradient * direction),
          trials = trials, selected_alpha = alpha,
          selected_trial_recheck = list(
            objective = confirmed$objective, gradient = confirmed$gradient,
            score_inf = confirmed$score_inf,
            objective_drift = confirmed$objective - inspected$objective,
            gradient_drift_inf = max(abs(confirmed$gradient - inspected$gradient))
          )
        )
      ))
    }
  }
  stop("Newton seed found no feasible monotone score-improving trial", call. = FALSE)
}

reference_fit <- function(objective, lower = rep(-Inf, length(objective$par)),
                          upper = rep(Inf, length(objective$par)), tolerance = 2e-4,
                          nonlinear_growth_polish = FALSE) {
  fit <- nlminb(objective$par, objective$fn, objective$gr,
    lower = lower, upper = upper,
    control = list(iter.max = 1500, eval.max = 3000, rel.tol = 1e-11)
  )
  inspect <- function(candidate, method) {
    gradient <- as.numeric(objective$gr(candidate$par))
    projected <- gradient
    projected[candidate$par <= lower + 1e-7 & gradient > 0] <- 0
    projected[candidate$par >= upper - 1e-7 & gradient < 0] <- 0
    list(
      method = method, parameters = unname(candidate$par),
      parameter_names = names(candidate$par), objective = candidate$objective,
      convergence = candidate$convergence, message = candidate$message,
      iterations = candidate$iterations, evaluations = unname(candidate$evaluations),
      gradient = gradient, projected_gradient = projected,
      raw_score_inf = max(abs(gradient)), projected_score_inf = max(abs(projected))
    )
  }
  attempts <- list(inspect(fit, "nlminb"))
  accepted <- function(candidate, diagnostic) {
    isTRUE(candidate$convergence == 0L) && all(is.finite(candidate$par)) &&
      is.finite(candidate$objective) && all(is.finite(diagnostic$gradient)) &&
      diagnostic$projected_score_inf < tolerance
  }
  polish_diagnostics <- NULL
  fail_fit <- function(polish_reason = NULL) {
    diagnostics <- list(optimizer_attempts = attempts)
    if (!is.null(polish_diagnostics)) diagnostics$newton_polish <- polish_diagnostics
    if (!is.null(polish_reason)) diagnostics$newton_polish_refusal <- polish_reason
    stop(structure(
      list(
        message = "TMB optimization/refinement failed the original status or score checks",
        call = NULL, diagnostics = diagnostics
      ),
      class = c("reference_fit_error", "error", "condition")
    ))
  }
  verify_polished <- function(candidate, seed, baseline) {
    check <- function() {
      list(
        objective = as.numeric(objective$fn(candidate$par)),
        gradient = as.numeric(objective$gr(candidate$par))
      )
    }
    first <- check()
    second <- check()
    reference_assert(
      length(first$objective) == 1L && is.finite(first$objective) &&
        length(first$gradient) == length(candidate$par) && all(is.finite(first$gradient)) &&
        length(second$objective) == 1L && is.finite(second$objective) &&
        length(second$gradient) == length(candidate$par) && all(is.finite(second$gradient)) &&
        all(is.finite(candidate$par)) && all(candidate$par >= lower) && all(candidate$par <= upper),
      "Newton-seeded final source evaluation is invalid or outside bounds"
    )
    projected <- first$gradient
    projected[candidate$par <= lower + 1e-7 & first$gradient > 0] <- 0
    projected[candidate$par >= upper - 1e-7 & first$gradient < 0] <- 0
    projected_repeat <- second$gradient
    projected_repeat[candidate$par <= lower + 1e-7 & second$gradient > 0] <- 0
    projected_repeat[candidate$par >= upper - 1e-7 & second$gradient < 0] <- 0
    reference_assert(
      abs(first$objective - second$objective) <= 1e-12 &&
        max(abs(first$gradient - second$gradient)) <= 1e-7 &&
        abs(first$objective - candidate$objective) <= 1e-9 &&
        first$objective <= seed$objective && first$objective <= baseline$objective &&
        second$objective <= seed$objective && second$objective <= baseline$objective &&
        max(abs(projected)) < tolerance && max(abs(projected_repeat)) < tolerance,
      "Newton-seeded final objective, score or inner-mode branch is uncertified"
    )
    list(
      objective = first$objective, gradient = first$gradient,
      projected_score_inf = max(abs(projected)),
      repeat_objective_drift = second$objective - first$objective,
      repeat_gradient_drift_inf = max(abs(first$gradient - second$gradient))
    )
  }
  if (!accepted(fit, attempts[[1]])) {
    # Optimize the same bounded objective from the retained first attempt.
    # A solver status alone never substitutes for the original score check.
    refined <- optim(fit$par, objective$fn, objective$gr,
      method = "L-BFGS-B",
      lower = lower, upper = upper,
      control = list(maxit = 1500, factr = 1, pgtol = tolerance / 10)
    )
    refined$objective <- refined$value
    refined$evaluations <- refined$counts
    attempts[[2]] <- inspect(refined, "optim L-BFGS-B refinement")
    if (!accepted(refined, attempts[[2]])) {
      if (!isTRUE(nonlinear_growth_polish)) fail_fit()
      if (!is.finite(refined$objective) || refined$objective > fit$objective) {
        fail_fit("The second optimizer did not decrease the same objective")
      }
      seed <- tryCatch(
        reference_newton_seed(objective, refined$par, lower, upper, tolerance),
        error = function(error) error
      )
      if (inherits(seed, "error")) fail_fit(conditionMessage(seed))
      polish_diagnostics <- seed$diagnostics
      restarted <- tryCatch(
        nlminb(seed$par, objective$fn, objective$gr,
          lower = lower, upper = upper,
          control = list(iter.max = 1500, eval.max = 3000, rel.tol = 1e-11)
        ),
        error = function(error) error
      )
      if (inherits(restarted, "error")) fail_fit(conditionMessage(restarted))
      restarted_diagnostic <- tryCatch(
        inspect(restarted, "nlminb Newton-seeded restart"),
        error = function(error) error
      )
      if (inherits(restarted_diagnostic, "error")) fail_fit(conditionMessage(restarted_diagnostic))
      attempts[[3]] <- restarted_diagnostic
      restart_ok <- accepted(restarted, attempts[[3]]) &&
        restarted$objective <= seed$objective && restarted$objective <= refined$objective
      if (restart_ok) {
        certificate <- tryCatch(verify_polished(restarted, seed, refined),
          error = function(error) error
        )
        if (inherits(certificate, "error")) fail_fit(conditionMessage(certificate))
        polish_diagnostics$final_recheck <- certificate
        fit <- restarted
      } else {
        seed_check <- tryCatch(list(
          objective = as.numeric(objective$fn(seed$par)),
          gradient = as.numeric(objective$gr(seed$par))
        ), error = function(error) error)
        if (inherits(seed_check, "error") || length(seed_check$objective) != 1L ||
          !is.finite(seed_check$objective) ||
          length(seed_check$gradient) != length(seed$par) ||
          !all(is.finite(seed_check$gradient)) ||
          abs(seed_check$objective - seed$objective) > 1e-12 ||
          max(abs(seed_check$gradient -
            seed$diagnostics$selected_trial_recheck$gradient)) > 1e-7) {
          fail_fit("Newton seed changed after failed restart")
        }
        last <- tryCatch(
          optim(seed$par, objective$fn, objective$gr,
            method = "L-BFGS-B", lower = lower, upper = upper,
            control = list(maxit = 1500, factr = 1, pgtol = tolerance / 10)
          ),
          error = function(error) error
        )
        if (inherits(last, "error")) fail_fit(conditionMessage(last))
        last$objective <- last$value
        last$evaluations <- last$counts
        last_diagnostic <- tryCatch(
          inspect(last, "optim L-BFGS-B Newton-seeded restart"),
          error = function(error) error
        )
        if (inherits(last_diagnostic, "error")) fail_fit(conditionMessage(last_diagnostic))
        attempts[[4]] <- last_diagnostic
        if (!accepted(last, attempts[[4]]) || last$objective > seed$objective ||
          last$objective > refined$objective) fail_fit("Newton-seeded optimizers remained uncertified")
        certificate <- tryCatch(verify_polished(last, seed, refined),
          error = function(error) error
        )
        if (inherits(certificate, "error")) fail_fit(conditionMessage(certificate))
        polish_diagnostics$final_recheck <- certificate
        fit <- last
      }
    } else {
      reference_assert(
        refined$objective <= fit$objective + 1e-8 * (1 + abs(fit$objective)),
        "TMB refinement increased the objective"
      )
      fit <- refined
    }
  }
  final <- attempts[[length(attempts)]]
  gradient <- final$gradient
  projected <- final$projected_gradient
  reference_assert(
    fit$convergence == 0L && all(is.finite(fit$par)) && is.finite(fit$objective),
    paste("TMB optimization failed:", fit$message)
  )
  reference_assert(max(abs(projected)) < tolerance, "TMB projected score is too large")
  objective$fn(fit$par)
  uncertainty <- TMB::sdreport(objective, par.fixed = fit$par)
  reference_assert(isTRUE(uncertainty$pdHess), "TMB fixed-parameter curvature is not positive definite")
  restored <- reference_restore_fit(objective, fit$par, fit$objective)
  if (!is.null(polish_diagnostics)) reference_assert(
    abs(restored$restored_loss - polish_diagnostics$final_recheck$objective) <= 1e-9 &&
      restored$restored_loss <= polish_diagnostics$selected_trial_recheck$objective &&
      restored$restored_loss <= polish_diagnostics$initial_objective,
    "Newton-seeded restored objective differs from fresh final evaluation"
  )
  diagnostics <- list(
    converged = TRUE, objective = fit$objective,
    raw_score_inf = max(abs(gradient)), projected_score_inf = max(abs(projected)),
    iterations = fit$iterations, pd_hessian = uncertainty$pdHess,
    restored_objective = restored$restored_loss, optimizer_attempts = attempts
  )
  if (!is.null(polish_diagnostics)) diagnostics$newton_polish <- polish_diagnostics
  list(
    objective = objective, optimizer = fit, parameters = restored$parameters, report = restored$report,
    diagnostics = diagnostics,
    uncertainty = uncertainty
  )
}

reference_coefficients <- function(value) {
  reference_assert(
    is.list(value) && setequal(names(value), c("cond", "zi", "disp")),
    "Unexpected glmmTMB coefficient components"
  )
  setNames(lapply(value, function(component) {
    reference_assert(
      is.numeric(component) && is.null(dim(component)) && all(is.finite(component)) &&
        (length(component) == 0L || (!is.null(names(component)) && !anyDuplicated(names(component)))),
      "Invalid named coefficient vector"
    )
    list(parameter_names = unname(as.list(names(component))), values = unname(as.list(component)))
  }), names(value))
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
