# SPDX-License-Identifier: MIT
# Portable pure geometry and refusal controls; no TMB runtime is loaded.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) stop("Usage: Rscript tests/newton_seed.R REFERENCE_SOURCE")
root <- normalizePath(args[1], mustWork = TRUE)
source(file.path(root, "R/common.R"))

target <- c(0.5, 0.9, -0.8, -1.7, -1.9)
lower <- c(-5, -3, -5, -6, -6)
upper <- c(5, 4, 2, 2, 2)
curvature <- diag(c(44.7, 548.6, 624.4, 874.7, 2629.9))
initial <- target + c(1e-6, -5e-8, 5e-8, 1e-8, -2e-8)

objective <- function(hessian, sign = 1) {
  list(
    fn = function(par) sign * as.numeric(crossprod(par - target, hessian %*% (par - target))) / 2,
    gr = function(par) as.numeric(hessian %*% (par - target))
  )
}

refuse <- function(expression, pattern) {
  error <- tryCatch(
    {
      force(expression); NULL
    },
    error = function(value) value
  )
  stopifnot(inherits(error, "error"), grepl(pattern, conditionMessage(error), fixed = TRUE))
}

seed <- reference_newton_seed(objective(curvature), initial, lower, upper, 2e-4)
stopifnot(
  seed$objective <= objective(curvature)$fn(initial),
  max(abs(objective(curvature)$gr(seed$par))) < 2e-4,
  seed$diagnostics$selected_alpha == 1,
  min(seed$diagnostics$hessian_eigenvalues) > 0,
  seed$diagnostics$directional_derivative < 0
)

wide <- diag(c(1, 10, 100, 1000, 1e5))
other <- reference_newton_seed(objective(wide), target + rep(1e-7, 5), lower, upper, 2e-4)
stopifnot(other$diagnostics$selected_alpha == 1)

indefinite <- curvature
indefinite[1, 1] <- -1
refuse(
  reference_newton_seed(objective(indefinite), initial, lower, upper, 2e-4),
  "not positive definite"
)

asymmetric <- curvature
asymmetric[1, 2] <- 0.5
refuse(
  reference_newton_seed(objective(asymmetric), initial, lower, upper, 2e-4),
  "asymmetric"
)

counter <- 0L
drifting <- list(
  fn = objective(curvature)$fn,
  gr = function(par) {
    counter <<- counter + 1L
    as.numeric(curvature %*% (par - target)) + counter * 1e-3
  }
)
refuse(reference_newton_seed(drifting, initial, lower, upper, 2e-4), "branch drifted")

refuse(
  reference_newton_seed(objective(curvature), lower, lower, upper, 2e-4),
  "interior bounded"
)
refuse(
  reference_newton_seed(objective(curvature, sign = -1), initial, lower, upper, 2e-4),
  "no feasible monotone"
)
flat_value <- list(fn = function(par) 0, gr = objective(curvature)$gr)
refuse(
  reference_newton_seed(flat_value, initial, lower, upper, 2e-4),
  "no feasible monotone"
)
trial_calls <- 0L
trial_drift <- list(
  fn = objective(curvature)$fn,
  gr = function(par) {
    trial_calls <<- trial_calls + 1L
    as.numeric(curvature %*% (par - target)) + if (trial_calls >= 24L) 1e-3 else 0
  }
)
refuse(
  reference_newton_seed(trial_drift, initial, lower, upper, 2e-4),
  "selected trial objective or gradient drifted"
)
nonfinite <- list(fn = objective(curvature)$fn, gr = function(par) rep(Inf, 5))
refuse(reference_newton_seed(nonfinite, initial, lower, upper, 2e-4), "nonfinite")

cat(
  "newton_seed passed: SPD, scaled SPD, indefinite, asymmetric, branch drift,",
  "active bound, objective increase/equality, selected-trial drift, nonfinite gradient\n"
)
