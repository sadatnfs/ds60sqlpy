# Original fixed model interface. No source compilation occurs during evaluation.
model_names <- c(
  "normal_mean", "regression", "nonlinear", "poisson_exposure",
  "censored_weibull", "random_intercept", "ar1", "panel_trend",
  "parallel_gaussian"
)
finite_numeric <- function(x, label, integer = FALSE) {
  if (!is.numeric(x) || !length(x) || any(!is.finite(x))) stop(paste(label, "must be finite numeric"))
  if (integer && any(x != floor(x))) stop(paste(label, "must contain integers"))
  invisible(x)
}
validate_inputs <- function(model, data, parameters) {
  if (length(model) != 1L || !model %in% model_names) stop("Unknown model")
  if (!is.list(data) || !is.list(parameters) || is.null(names(parameters)) || anyDuplicated(names(parameters))) stop("Named data and parameter lists required")
  for (key in names(parameters)) finite_numeric(parameters[[key]], key)
  n <- if (model == "censored_weibull") length(data$time) else length(data$y)
  if (n < 2L || n > 100000L) stop("Require 2 to 100000 observations")
  response <- if (model == "censored_weibull") data$time else data$y
  finite_numeric(response, "response")
  equal <- function(x, label) {
    finite_numeric(x, label)
    if (length(x) != n) stop(paste(label, "length differs from response"))
  }
  if (model == "regression") {
    if (!is.matrix(data$X) || !is.matrix(data$X_pred)) stop("X and X_pred must be matrices")
    finite_numeric(data$X, "X"); finite_numeric(data$X_pred, "X_pred")
    if (nrow(data$X) != n || ncol(data$X) != length(parameters$beta) || ncol(data$X_pred) != ncol(data$X)) stop("Design matrix shape mismatch")
  }
  if (model %in% c("nonlinear", "panel_trend")) {
    equal(data$time, "time"); finite_numeric(data$time_pred, "time_pred")
    if (any(data$time < 0) || any(data$time_pred < 0)) stop("Time must be nonnegative")
  }
  if (model == "poisson_exposure") {
    equal(data$x, "x"); equal(data$exposure, "exposure")
    if (any(data$y < 0 | data$y != floor(data$y)) || any(data$exposure <= 0)) stop("Counts must be nonnegative integers; exposure must be positive")
  }
  if (model == "censored_weibull") {
    equal(data$entry, "entry"); equal(data$event, "event")
    if (any(data$time <= 0) || any(data$entry < 0 | data$entry >= data$time) || any(!data$event %in% c(0, 1))) stop("Invalid censor/entry record")
    data$event <- as.integer(data$event)
  }
  if (model %in% c("random_intercept", "panel_trend")) {
    equal(data$group, "group"); finite_numeric(data$group, "group", TRUE)
    if (any(data$group < 0 | data$group >= length(parameters$u))) stop("group must index u from zero")
    data$group <- as.integer(data$group)
  }
  if (model == "panel_trend") {
    finite_numeric(data$group_pred, "group_pred", TRUE)
    if (length(data$group_pred) != length(data$time_pred) || any(data$group_pred < 0 | data$group_pred >= length(parameters$u))) stop("Prediction groups invalid")
    data$group_pred <- as.integer(data$group_pred)
  }
  if (model == "ar1") {
    if (length(parameters$u) != n) stop("AR1 requires one state per observation")
    if (length(data$horizon) != 1L || !is.finite(data$horizon) || data$horizon < 1 || data$horizon > 100 || data$horizon != floor(data$horizon)) stop("Horizon must be an integer from 1 to 100")
    data$horizon <- as.integer(data$horizon)
  }
  data
}
make_objective <- function(model, data, parameters, random = NULL,
                           build_dir = Sys.getenv("TMB_BUILD_DIR")) {
  if (!requireNamespace("TMB", quietly = TRUE)) stop("Prepare TMB first")
  data <- validate_inputs(model, data, parameters)
  if (!is.null(random) && (!identical(random, "u") || !model %in% c("random_intercept", "ar1", "panel_trend"))) stop("This interface permits only random='u' for latent models")
  if (!nzchar(build_dir)) stop("TMB_BUILD_DIR is required; evaluation never compiles")
  library_path <- normalizePath(file.path(build_dir, TMB::dynlib(model)), mustWork = TRUE)
  if (!model %in% names(getLoadedDLLs())) dyn.load(library_path)
  actual <- normalizePath(getLoadedDLLs()[[model]][["path"]], mustWork = TRUE)
  if (!identical(actual, library_path)) stop("A different model library is already loaded; use a fresh R process")
  TMB::MakeADFun(data = data, parameters = parameters, random = random, DLL = model, silent = TRUE)
}
evaluate_objective <- function(obj, theta) {
  finite_numeric(theta, "theta")
  if (length(theta) != length(obj$par)) stop("Theta dimension mismatch")
  value <- obj$fn(theta)
  gradient <- as.numeric(obj$gr(theta))
  if (!is.finite(value) || any(!is.finite(gradient))) stop("Non-finite objective or gradient")
  list(value = as.numeric(value), gradient = gradient)
}
fit_objective <- function(obj) {
  fit <- nlminb(obj$par, obj$fn, obj$gr, control = list(eval.max = 600, iter.max = 400, rel.tol = 1e-10))
  checked <- evaluate_objective(obj, fit$par)
  fit$gradient_max <- max(abs(checked$gradient))
  fit$refinement <- list(applied = FALSE, original_gradient_max = fit$gradient_max)
  # Relative objective stopping can leave an absolute gradient in a narrow basin.
  # Permit one small Newton correction only after successful outer convergence.
  if (fit$convergence == 0L && fit$gradient_max >= 1e-4 && length(fit$par) <= 32L) {
    hessian <- stats::optimHess(fit$par, obj$fn, obj$gr)
    factor <- tryCatch(chol(hessian), error = function(e) NULL)
    if (!is.null(factor)) {
      step <- backsolve(factor, forwardsolve(t(factor), checked$gradient))
      if (max(abs(step) / pmax(1, abs(fit$par))) < 1e-3) {
        candidate <- fit$par - step
        revised <- evaluate_objective(obj, candidate)
        tolerance <- 100 * .Machine$double.eps * max(1, abs(checked$value))
        if (revised$value <= checked$value + tolerance && max(abs(revised$gradient)) < fit$gradient_max) {
          fit$refinement <- list(
            applied = TRUE, original_gradient_max = fit$gradient_max,
            original_objective = fit$objective, relative_step = max(abs(step) / pmax(1, abs(fit$par)))
          )
          fit$par <- candidate
          fit$objective <- revised$value
          fit$gradient_max <- max(abs(revised$gradient))
        }
      }
    }
  }
  fit$diagnostic_ok <- fit$convergence == 0L && fit$gradient_max < 1e-4
  fit
}
