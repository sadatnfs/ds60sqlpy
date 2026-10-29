# Run from the project root with compiled libraries selected by TMB_BUILD_DIR.
source("R/api.R")
assert_close <- function(actual, expected, tol = 1e-6) {
  if (!isTRUE(all.equal(as.numeric(actual), as.numeric(expected), tolerance = tol))) stop("Numerical oracle mismatch")
}
finite_gradient <- function(fn, theta) {
  vapply(seq_along(theta), function(j) {
    step <- 1e-5 * max(1, abs(theta[j]))
    a <- b <- theta; a[j] <- a[j] + step; b[j] <- b[j] - step
    (fn(a) - fn(b)) / (2 * step)
  }, numeric(1))
}
y <- c(1, 2, 4, 7)
obj <- make_objective("normal_mean", list(y = y), list(mu = 2.2, log_sigma = .3))
theta <- obj$par
assert_close(obj$fn(theta), sum(-dnorm(y, theta[1], exp(theta[2]), log = TRUE)))
assert_close(obj$gr(theta), finite_gradient(obj$fn, theta))
fit <- fit_objective(obj)
stopifnot(fit$diagnostic_ok)
assert_close(fit$par, c(mean(y), log(sqrt(mean((y - mean(y))^2)))))
report <- TMB::sdreport(obj, par.fixed = fit$par)
stopifnot(report$pdHess)
assert_close(obj$report(fit$par)$residual, y - mean(y))
X <- cbind(1, seq(-1, 1, length.out = 12))
yr <- as.numeric(X %*% c(1.2, -.7)) + rep(c(-.1, .2, -.1), 4)
reg <- make_objective("regression", list(y = yr, X = X, X_pred = X), list(beta = c(0, 0), log_sigma = 0))
rf <- fit_objective(reg); stopifnot(rf$diagnostic_ok)
assert_close(rf$par[1:2], as.numeric(qr.solve(X, yr)))
# Integrating Gaussian random intercepts is exactly Gaussian, so Laplace has an exact oracle.
yg <- c(-.2, .1, .4, 1.8, 2.2, 2.5)
group <- c(0L, 0L, 0L, 1L, 1L, 1L)
latent <- make_objective("random_intercept", list(y = yg, group = group), list(beta = .7, log_sigma = log(.4), log_tau = log(.8), u = c(0, 0)), random = "u")
exact <- function(p) {
  Z <- model.matrix(~ factor(group) - 1)
  V <- exp(2 * p[2]) * diag(length(yg)) + exp(2 * p[3]) * tcrossprod(Z)
  delta <- yg - p[1]
  .5 * (length(yg) * log(2 * pi) + as.numeric(determinant(V, logarithm = TRUE)$modulus) + sum(delta * solve(V, delta)))
}
assert_close(latent$fn(latent$par), exact(latent$par))
assert_close(latent$gr(latent$par), finite_gradient(exact, latent$par), 1e-5)
# Stationary AR1 covariance, including first-state normalization.
ya <- c(.1, .4, -.1, .3, .7)
a <- make_objective("ar1", list(y = ya, horizon = 3L), list(beta = .2, log_sigma = log(.3), log_tau = log(.7), phi_raw = atanh(.5), u = rep(0, 5)), random = "u")
va <- .7^2 * .5^abs(outer(seq_along(ya), seq_along(ya), "-")) + .3^2 * diag(5)
da <- ya - .2
assert_close(a$fn(a$par), .5 * (5 * log(2 * pi) + as.numeric(determinant(va, logarithm = TRUE)$modulus) + sum(da * solve(va, da))), 1e-6)
# Count and censor terms use actual likelihood families.
p <- make_objective("poisson_exposure", list(y = c(0, 3), x = c(0, 1), exposure = c(1, 2)), list(alpha = log(2), beta = log(1.5)))
assert_close(p$fn(p$par), sum(-dpois(c(0, 3), c(2, 6), log = TRUE)))
cens <- make_objective("censored_weibull", list(time = c(2, 4), entry = c(0, 1), event = c(1L, 0L)), list(log_scale = log(2), log_shape = 0))
assert_close(cens$fn(cens$par), 2.5 + log(2))
assert_close(cens$gr(cens$par), finite_gradient(cens$fn, cens$par), 1e-5)
# Nonlinear fit and separate complete synthetic panels.
time <- seq(0, 8, length.out = 40)
yn <- 3 * exp(-.6 * time) + 1 + rep(c(-.03, .01, .02, -.01, .01), 8)
n <- make_objective("nonlinear", list(y = yn, time = time, time_pred = c(9, 10)), list(log_a = log(2.5), log_b = log(.5), offset = .9, log_sigma = log(.1)))
nf <- fit_objective(n); stopifnot(nf$diagnostic_ok, max(abs(n$gr(nf$par))) < 1e-4)
assert_close(nf$par[1:3], c(log(3), log(.6), 1), .03)
pt <- rep(time, 4); pg <- rep(0:3, each = length(time)); py <- rep(3 * exp(-.6 * time) + 1, 4) + rep(c(-.6, -.2, .2, .6), each = length(time)) + rep(rep(c(-.03, .01, .02, -.01, .01), 8), 4)
panel <- make_objective("panel_trend", list(y = py, time = pt, group = pg, time_pred = rep(9, 4), group_pred = 0:3), list(log_a = log(2.5), log_b = log(.5), offset = .9, log_sigma = log(.1), log_tau = log(.4), u = rep(0, 4)), random = "u")
assert_close(panel$gr(panel$par), finite_gradient(panel$fn, panel$par), 1e-4)
pf <- fit_objective(panel); stopifnot(pf$diagnostic_ok)
psd <- TMB::sdreport(panel, par.fixed = pf$par, getReportCovariance = FALSE); stopifnot(psd$pdHess)
# Validate one and two actual OpenMP threads, values and derivatives.
parallel <- make_objective("parallel_gaussian", list(y = y), list(mu = 2.2, log_sigma = .3))
TMB::openmp(1, DLL = "parallel_gaussian"); one <- evaluate_objective(parallel, parallel$par)
TMB::openmp(2, DLL = "parallel_gaussian"); two <- evaluate_objective(parallel, parallel$par)
assert_close(one$value, two$value); assert_close(one$gradient, two$gradient)
assert_close(two$value, obj$fn(theta)); assert_close(two$gradient, obj$gr(theta))
# Boundary failures must be explicit, before native model evaluation.
expect_failure <- function(expression) {
  rejected <- tryCatch(
    {
      force(expression); FALSE
    },
    error = function(e) TRUE
  )
  if (!rejected) stop("Invalid input was accepted")
}
expect_failure(make_objective("unknown", list(y = y), list(mu = 0, log_sigma = 0)))
expect_failure(make_objective("normal_mean", list(y = c(1, NA)), list(mu = 0, log_sigma = 0)))
expect_failure(make_objective("poisson_exposure", list(y = c(0, 2), x = c(0, 1), exposure = c(0, 1)), list(alpha = 0, beta = 0)))
expect_failure(make_objective("random_intercept", list(y = c(1, 2), group = c(0, 2)), list(beta = 0, log_sigma = 0, log_tau = 0, u = c(0, 0)), random = "u"))
expect_failure(make_objective("ar1", list(y = c(1, 2), horizon = 0), list(beta = 0, log_sigma = 0, log_tau = 0, phi_raw = 0, u = c(0, 0)), random = "u"))
expect_failure(evaluate_objective(obj, c(1)))
stopifnot(is.list(pf$refinement), pf$gradient_max < 1e-4)
cat("Panel diagnostics:", jsonlite::toJSON(list(convergence = pf$convergence, message = pf$message, gradient_max = pf$gradient_max, refinement = pf$refinement), auto_unbox = TRUE, digits = 17), "\n")
# All runtime evidence is emitted only after every assertion succeeds.
cat("PASS: compiled Gaussian, gradients, optimizer, Hessian, REPORT, sdreport, linear regression, Gaussian Laplace, AR1, counts, censoring, nonlinear, panels and OpenMP parity\n")
