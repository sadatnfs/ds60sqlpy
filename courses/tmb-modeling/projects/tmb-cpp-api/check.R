# Fixed original C++ API probes. Compile only in explicitly owned scratch.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) stop("Usage: Rscript --vanilla check.R PROJECT_ROOT BUILD_DIR")
root <- normalizePath(args[1], mustWork = TRUE)
dir.create(args[2], recursive = TRUE, showWarnings = FALSE)
build <- normalizePath(args[2], mustWork = TRUE)
stopifnot(as.character(packageVersion("TMB")) == "1.9.25")
setwd(build)
models <- c("density_forms", "separable_array", "stable_mixture", "conditional", "atomic_quartic")
for (model in models) {
  stopifnot(file.copy(file.path(root, "models", paste0(model, ".cpp")), paste0(model, ".cpp"), overwrite = TRUE))
  status <- TMB::compile(paste0(model, ".cpp"), flags = "-O1 -g0", framework = "CppAD", openmp = FALSE)
  stopifnot(status == 0L)
  dyn.load(TMB::dynlib(model))
}
close_enough <- function(a, b, tol = 1e-6) stopifnot(isTRUE(all.equal(as.numeric(a), as.numeric(b), tolerance = tol)))
finite_gradient <- function(fn, theta, relative_step = 1e-5) {
  vapply(seq_along(theta), function(index) {
    step <- relative_step * max(1, abs(theta[index]))
    plus <- minus <- theta
    plus[index] <- plus[index] + step
    minus[index] <- minus[index] - step
    (fn(plus) - fn(minus)) / (2 * step)
  }, numeric(1))
}
Sigma <- matrix(c(2, .5, .5, 1), 2, 2)
Q <- Matrix::forceSymmetric(Matrix::Matrix(solve(Sigma), sparse = TRUE))
state <- c(.3, -.4)
dense <- function(u, S) length(u) * log(2 * pi) / 2 + as.numeric(determinant(S, logarithm = TRUE)$modulus) / 2 + sum(u * solve(S, u)) / 2
for (mode in 0:3) {
  scales <- c(2, .5)
  obj <- TMB::MakeADFun(list(mode = as.integer(mode), covariance = Sigma, precision = Q, scales = scales), list(state = state), DLL = "density_forms", silent = TRUE)
  target <- if (mode == 2) diag(scales) %*% Sigma %*% diag(scales) else if (mode == 3) 4 * Sigma else Sigma
  close_enough(obj$fn(obj$par), dense(state, target))
  close_enough(obj$gr(obj$par), solve(target, state))
}
array_state <- array(c(.2, -.1, .3, .4, -.2, .1), dim = c(2, 3))
sep <- TMB::MakeADFun(list(), list(state = array_state, phi_row_raw = atanh(.3), phi_col_raw = atanh(.7), log_scale = log(1.2)), DLL = "separable_array", silent = TRUE)
C <- 1.2^2 * kronecker(.7^abs(outer(1:3, 1:3, "-")), .3^abs(outer(1:2, 1:2, "-")))
close_enough(sep$fn(sep$par), dense(as.vector(array_state), C))
close_enough(sep$gr(sep$par)[1:6], solve(C, as.vector(array_state)))
stopifnot(identical(names(sep$par)[7:9], c("phi_row_raw", "phi_col_raw", "log_scale")))
separable_dense_oracle <- function(theta) {
  row_cov <- tanh(theta[7])^abs(outer(1:2, 1:2, "-"))
  col_cov <- tanh(theta[8])^abs(outer(1:3, 1:3, "-"))
  covariance <- exp(2 * theta[9]) * kronecker(col_cov, row_cov)
  dense(theta[1:6], covariance)
}
for (step in c(1e-4, 1e-5)) {
  oracle_gradient <- finite_gradient(separable_dense_oracle, sep$par, step)
  close_enough(sep$gr(sep$par), oracle_gradient, tol = 1e-5)
}
cat("SEPARABLE state and all correlation/scale gradient directions matched the independent dense oracle\n")

mix <- TMB::MakeADFun(list(y = c(-1, .2, 1)), list(eta = 0, mu_one = -1, mu_two = 1, log_sigma = 0), DLL = "stable_mixture", silent = TRUE)
softplus <- function(x) max(x, 0) + log1p(exp(-abs(x)))
mixture_oracle <- function(theta) {
  first <- -softplus(-theta[1]) + dnorm(c(-1, .2, 1), theta[2], exp(theta[4]), log = TRUE)
  second <- -softplus(theta[1]) + dnorm(c(-1, .2, 1), theta[3], exp(theta[4]), log = TRUE)
  largest <- pmax(first, second)
  -sum(largest + log(exp(first - largest) + exp(second - largest)))
}
for (eta in c(-1000, -3, 0, 2, 1000)) {
  theta <- mix$par
  theta[1] <- eta
  value <- mix$fn(theta)
  gradient <- mix$gr(theta)
  stopifnot(is.finite(value), all(is.finite(gradient)))
  close_enough(value, mixture_oracle(theta))
  for (step in c(1e-4, 1e-5)) close_enough(gradient, finite_gradient(mixture_oracle, theta, step), tol = 1e-5)
}
cat("Mixture values and all weight/mean/scale gradient directions matched the independent log-density oracle\n")
branch <- TMB::MakeADFun(list(), list(x = 1), DLL = "conditional", silent = TRUE)
for (x in c(-2, -.1, .1, 2)) {
  close_enough(branch$fn(x), max(x, 0)^2)
  close_enough(branch$gr(x), if (x > 0) 2 * x else 0)
}
atomic <- TMB::MakeADFun(list(), list(x = .5), DLL = "atomic_quartic", silent = TRUE, hessian = TRUE)
for (x in c(-.7, .4, 1.3)) {
  close_enough(atomic$fn(x), x^4 + .5 * x^2)
  close_enough(atomic$gr(x), 4 * x^3 + x)
  close_enough(atomic$he(x), 12 * x^2 + 1)
}
cat("PASS original C++ API probes: MVNORM/GMRF/SCALE/VECSCALE, SEPARABLE array order, stable mixtures, conditional tape crossings, atomic value/gradient/Hessian\n")

runtime_receipt <- list(
  R = as.character(getRversion()), TMB = as.character(packageVersion("TMB")),
  Matrix = as.character(packageVersion("Matrix")), architecture = R.version$platform
)

file_sha256 <- function(path) {
  output <- system2("sha256sum", shQuote(normalizePath(path, mustWork = TRUE)), stdout = TRUE)
  status <- attr(output, "status")
  if ((!is.null(status) && status != 0L) || length(output) != 1L) stop("SHA256 file inspection failed")
  digest <- strsplit(output, "[[:space:]]+")[[1]][1]
  if (!grepl("^[a-f0-9]{64}$", digest)) stop("Invalid SHA256 file digest")
  digest
}
artifacts <- lapply(models, function(model) list(
  source_relative = paste0("courses/tmb-modeling/projects/tmb-cpp-api/models/", model, ".cpp"),
  source_sha256 = file_sha256(file.path(root, "models", paste0(model, ".cpp"))),
  library_sha256 = file_sha256(file.path(build, TMB::dynlib(model)))
))
cpp_result <- list(
  schema_version = 1L, case = "tmb-cpp-api", passed = TRUE,
  checks = as.list(c(
    "dense-precision-scale-values", "dense-precision-scale-gradients",
    "separable-kronecker-value", "separable-state-gradient", "separable-all-parameter-finite-differences",
    "mixture-values", "mixture-all-parameter-finite-differences", "conditional-crossing-values",
    "conditional-crossing-gradients", "atomic-values", "atomic-gradients", "atomic-hessians"
  )),
  runtime = runtime_receipt,
  fixtures = list(
    finite_difference_steps = list(1e-4, 1e-5),
    mixture_logits = as.list(c(-1000, -3, 0, 2, 1000)), atomic_points = as.list(c(-.7, .4, 1.3)),
    conditional_points = as.list(c(-2, -.1, .1, 2)), density_modes = as.list(0:3)
  ),
  artifacts = artifacts
)
cat("DS60_SCIENTIFIC_RESULT ", jsonlite::toJSON(cpp_result, auto_unbox = TRUE, digits = 17), "\n", sep = "")
