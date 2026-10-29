args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3L) stop("Usage: evaluate_registered.R PROJECT_ROOT BUILD_DIR REQUEST_JSON")
root <- normalizePath(args[1], mustWork = TRUE)
build <- normalizePath(args[2], mustWork = TRUE)
request_path <- normalizePath(args[3], mustWork = TRUE)
if (file.info(request_path)$size > 1000000) stop("Request too large")
registry <- jsonlite::fromJSON(file.path(root, "registry.json"), simplifyVector = FALSE)
request <- jsonlite::fromJSON(request_path, simplifyVector = FALSE)
if (!identical(request$schema_version, 1L) || !is.character(request$model_id) ||
  length(request$model_id) != 1L || !request$model_id %in% names(registry$models)) stop("Unprepared model ID")
spec <- registry$models[[request$model_id]]
if (!is.character(request$action) || length(request$action) != 1L ||
  !request$action %in% c("evaluate", "fit", "predict")) stop("Unknown prepared action")

numeric_scalar <- function(value, integer = FALSE) {
  if (!is.numeric(value) || length(value) != 1L || !is.finite(value)) stop("Numeric values cannot be booleans, null or nonfinite")
  if (integer) {
    if (value != floor(value) || value < -.Machine$integer.max || value > .Machine$integer.max) stop("Expected non-NA signed32 integer vector")
    converted <- as.integer(value)
    if (is.na(converted) || as.double(converted) != value) stop("Integer coercion changed a declared value")
    return(converted)
  }
  as.numeric(value)
}
numeric_vector <- function(values, integer = FALSE, allow_empty = FALSE) {
  if (!is.list(values) || !is.null(names(values)) || length(values) > 4096L ||
    (!allow_empty && !length(values))) stop("Expected a bounded JSON numeric array")
  if (integer) return(vapply(values, numeric_scalar, integer(1), integer = TRUE))
  vapply(values, numeric_scalar, numeric(1))
}
typed <- function(value, kind, allow_empty = FALSE) {
  if (kind == "real_vector") return(numeric_vector(value, allow_empty = allow_empty))
  if (kind == "integer_vector") return(numeric_vector(value, integer = TRUE, allow_empty = allow_empty))
  if (kind == "real_scalar") return(numeric_scalar(value))
  if (kind == "integer_scalar") return(numeric_scalar(value, integer = TRUE))
  stop("Unknown prepared numeric kind")
}

predicting <- identical(request$action, "predict")
if (predicting) {
  if (is.null(spec$prediction) || !is.null(spec$random)) stop("Prediction is not declared for this model")
  prediction <- spec$prediction
  if (!identical(request$target, prediction$target)) stop("Prediction target differs from registered report")
  nobs <- numeric_scalar(request$n_rows, integer = TRUE)
  if (nobs < 1L || nobs > 4096L) stop("Prediction row count outside bounds")
  fields <- prediction$inputs
  constants <- prediction$constants
  count_field <- prediction$row_count_field
} else {
  fields <- spec$data
  constants <- spec$training_constants
  count_field <- NULL
}
expected_fields <- c(names(fields), names(constants), if (!is.null(count_field)) count_field)
if (!setequal(names(request$data), expected_fields) || anyDuplicated(names(request$data))) stop("Data schema differs")
data <- list()
counts <- integer(0)
for (name in names(fields)) {
  data[[name]] <- typed(request$data[[name]], fields[[name]])
  counts <- c(counts, length(data[[name]]))
}
if (predicting) counts <- c(counts, nobs)
if (length(unique(counts)) != 1L) stop("Unequal observation counts")
if (!predicting) nobs <- length(data[[spec$response]])
for (name in names(constants)) {
  entry <- constants[[name]]
  expected <- typed(entry$value, entry$kind, allow_empty = TRUE)
  actual <- typed(request$data[[name]], entry$kind, allow_empty = TRUE)
  if (!identical(actual, expected)) stop("Trusted internal data constant was changed")
  data[[name]] <- actual
}
if (!is.null(count_field)) {
  actual_count <- numeric_scalar(request$data[[count_field]], integer = TRUE)
  if (actual_count != nobs) stop("Prediction row count differs from constructed data")
  data[[count_field]] <- actual_count
}

fixed_names <- unlist(spec$fixed_parameters, use.names = FALSE)
theta <- numeric_vector(request$theta)
if (length(theta) != length(fixed_names)) stop("Fixed parameter layout differs")
layout <- spec$parameter_layout
if (is.null(layout)) layout <- lapply(fixed_names, function(name) list(name = name, kind = "scalar", size = 1L, coordinates = list(name)))
parameters <- list()
native_names <- character(0)
position <- 1L
for (block in layout) {
  indices <- seq.int(position, length.out = block$size)
  parameters[[block$name]] <- if (block$kind == "scalar") theta[indices[1]] else theta[indices]
  native_names <- c(native_names, rep(block$name, block$size))
  position <- position + block$size
}
if (position != length(theta) + 1L) stop("Fixed parameter block size differs")
random <- NULL
if (!is.null(spec$random)) {
  group <- data[[spec$random$group_field]]
  groups <- sort(unique(group))
  if (length(groups) > 256L || !identical(as.integer(groups), seq_len(length(groups)) - 1L)) stop("Invalid complete group indices")
  random <- spec$random$name
  parameters[[random]] <- rep(0, length(groups))
}
if (!identical(request$random, random)) stop("Marginal versus joint target mismatch")
actual_abi <- list(
  R = as.character(getRversion()), TMB = as.character(packageVersion("TMB")),
  Matrix = as.character(packageVersion("Matrix")), architecture = R.version$platform
)
receipt <- jsonlite::fromJSON(file.path(build, "receipt.json"), simplifyVector = FALSE)
for (name in names(actual_abi)) if (!identical(actual_abi[[name]], receipt$abi[[name]])) stop("Compiled artifact ABI differs")
dyn.load(file.path(build, paste0(request$model_id, ".so")))
obj <- TMB::MakeADFun(data = data, parameters = parameters, random = random, DLL = request$model_id, silent = TRUE)
if (!identical(names(obj$par), native_names)) stop("C++ fixed parameter block order differs")
result <- list(
  schema_version = 1L, model_id = request$model_id,
  parameter_names = as.list(fixed_names), nobs = nobs, abi = actual_abi
)
if (predicting) {
  report <- obj$report(theta)
  values <- report[[prediction$report]]
  if (!is.numeric(values) || !is.null(dim(values)) || length(values) != nobs || any(!is.finite(values))) stop("Native prediction report differs from its declared vector contract")
  result$target <- prediction$target
  result$prediction <- as.list(as.numeric(values))
} else {
  fit <- NULL
  if (identical(request$action, "fit")) {
    fit <- nlminb(theta, obj$fn, obj$gr, control = list(iter.max = 100, eval.max = 300, rel.tol = 1e-10))
    theta <- fit$par
  }
  value <- as.numeric(obj$fn(theta))
  gradient <- as.numeric(obj$gr(theta))
  if (!is.finite(value) || any(!is.finite(gradient))) stop("Nonfinite prepared objective")
  result$value <- value
  result$gradient <- as.list(gradient)
  if (!is.null(fit)) {
    result$fitted_parameters <- as.list(as.numeric(fit$par))
    result$convergence <- fit$convergence
    result$iterations <- fit$iterations
    result$optimizer_message <- fit$message
    result$gradient_max <- max(abs(gradient))
    result$fit_controls <- list(
      optimizer = "nlminb", relative_tolerance = 1e-10,
      max_iterations = 100L, max_evaluations = 300L
    )
  }
}
cat(jsonlite::toJSON(result, auto_unbox = TRUE, digits = 17), "\n")
