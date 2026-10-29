source("R/api.R")
stopifnot(as.character(utils::packageVersion("TMB")) == "1.9.25")
obj <- make_objective("normal_mean", list(y = c(1, 2, 4, 7)), list(mu = 0, log_sigma = 0))
fit <- fit_objective(obj)
report <- TMB::sdreport(obj, par.fixed = fit$par, getReportCovariance = FALSE)
stopifnot(report$pdHess)
print(summary(report, select = "fixed"))
print(summary(report, select = "report"))
print(as.list(report, what = "Estimate", report = TRUE))
print(report)
print(TMB::TMB.Version())
stopifnot(TMB::dynlib("normal_mean") == "normal_mean.so")
configuration <- TMB::config(DLL = "normal_mean")
stopifnot(is.list(configuration), length(configuration) > 0)
print(TMB::openmp(DLL = "normal_mean"))
# Known sigma makes the scalar mean profile have an independent exact interval.
profile_obj <- TMB::MakeADFun(
  data = list(y = c(1, 2, 4, 7)),
  parameters = list(mu = 3.5, log_sigma = log(2)), map = list(log_sigma = factor(NA)),
  DLL = "normal_mean", silent = TRUE
)
stopifnot(length(profile_obj$par) == 1)
profile_obj$fn(profile_obj$par)
profile <- TMB::tmbprofile(profile_obj, "mu", ytol = 2.2, ystep = .2, trace = FALSE)
interval <- confint(profile)
print(interval)
roots <- TMB::tmbroot(profile_obj, "mu", trace = FALSE)
print(roots)
expected <- 3.5 + c(-1, 1) * qnorm(.975)
stopifnot(max(abs(as.numeric(roots) - expected)) < 1e-3)
stopifnot(max(abs(as.numeric(interval) - expected)) < .03)
# Save then remove an ordinary plot in disposable scratch only.
pdf_path <- tempfile(fileext = ".pdf")
grDevices::pdf(pdf_path)
plot(profile)
grDevices::dev.off()
stopifnot(file.info(pdf_path)$size > 0)
unlink(pdf_path)
# Exercise simulation consistency with a fixed 100-replicate budget; retain the statistical output separately from API success.
set.seed(4141)
simulated <- obj$simulate(par = fit$par)
stopifnot(length(simulated$y) == 4, all(is.finite(simulated$y)))
consistency <- TMB::checkConsistency(obj, par = fit$par, n = 100)
print(consistency)
summary_result <- summary(consistency)
stopifnot(is.list(summary_result))
# A genuine sparse-Hessian inner quadratic and its option reader.
quadratic <- TMB::newton(
  par = c(0, 0), fn = function(x) {
    u <- x - c(1, -2); (2 * u[1]^2 + u[1] * u[2] + u[2]^2) / 2
  },
  gr = function(x) {
    u <- x - c(1, -2); c(2 * u[1] + .5 * u[2], .5 * u[1] + u[2])
  },
  he = function(x) Matrix::sparseMatrix(i = c(1, 1, 2), j = c(1, 2, 2), x = c(2, .5, 1), symmetric = TRUE),
  trace = 0, smartsearch = FALSE
)
print(quadratic)
stopifnot(max(abs(quadratic$par - c(1, -2))) < 1e-8)
options <- TMB::newtonOption(obj)
stopifnot(is.list(options))
# Public grid descriptor and installed example listing, with no example executed.
print(TMB::SR(seq(-3, 3, length.out = 7)))
example_listing <- capture.output(TMB::runExample())
stopifnot(length(example_listing) > 0)
# The exported surface is verified against the exact source-derived inventory.
inventory <- jsonlite::fromJSON("tests/public_api_exports.json")
stopifnot(setequal(getNamespaceExports("TMB"), inventory$explicit_exports))
stopifnot(!"GK" %in% getNamespaceExports("TMB"))
scaffold <- capture.output(TMB::template())
interface <- capture.output(TMB::Rinterface("models/normal_mean.cpp"))
stopifnot(any(grepl("objective_function", scaffold, fixed = TRUE)), any(grepl("log_sigma", interface, fixed = TRUE)))
bench <- TMB::benchmark(profile_obj, n = 10000, cores = 1)
benchmark_plot <- tempfile(fileext = ".pdf")
grDevices::pdf(benchmark_plot)
plot(bench)
grDevices::dev.off()
stopifnot(file.info(benchmark_plot)$size > 0)
unlink(benchmark_plot)
TMB::FreeADFun(profile_obj)
TMB::FreeADFun(obj)
cat("PASS public API probe: exports, MakeADFun/map, sdreport/print/summary/as.list, TMB.Version, dynlib, config, openmp read, tmbprofile/plot/confint, tmbroot, simulate, checkConsistency/print/summary, newton/newtonOption, SR, runExample listing, template/Rinterface, benchmark/plot, FreeADFun\n")

runtime_receipt <- list(
  R = as.character(getRversion()), TMB = as.character(packageVersion("TMB")),
  Matrix = as.character(packageVersion("Matrix")), architecture = R.version$platform
)

api_result <- list(
  schema_version = 1L, case = "tmb-public-api", passed = TRUE,
  checks = as.list(c(
    "prepared-export-inventory", "fixed-parameter-map", "report-methods",
    "normal-profile-root-oracle", "profile-plot", "normal-simulation-finite",
    "score-consistency-api", "sparse-newton-oracle", "newton-options-read",
    "sr-descriptor", "template-interface-generation", "installed-example-listing",
    "benchmark-plot", "version-config-thread-read", "native-object-release"
  )),
  runtime = runtime_receipt,
  fixtures = list(
    seed = 4141L, score_replicates = 100L, benchmark_repetitions = 10000L,
    profile_root_absolute_tolerance = 1e-3, profile_interval_absolute_tolerance = .03
  ),
  artifacts = list()
)
cat("DS60_SCIENTIFIC_RESULT ", jsonlite::toJSON(api_result, auto_unbox = TRUE, digits = 17), "\n", sep = "")
