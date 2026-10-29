args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) stop("Usage: Rscript --vanilla R/evaluate.R PROJECT_ROOT REQUEST_JSON")
root <- normalizePath(args[1], mustWork = TRUE)
source(file.path(root, "R", "api.R"))
request_path <- normalizePath(args[2], mustWork = TRUE)
if (file.info(request_path)$size > 10000000) stop("Request too large")
request <- jsonlite::fromJSON(request_path, simplifyVector = TRUE)
if (!identical(request$schema_version, 1L)) stop("Unsupported request schema")
obj <- make_objective(request$model, request$data, request$parameters, request$random)
result <- evaluate_objective(obj, request$theta)
result$schema_version <- 1L
result$model <- request$model
result$parameter_names <- names(obj$par)
result$nobs <- if (request$model == "censored_weibull") length(request$data$time) else length(request$data$y)
result$provenance <- list(
  R = as.character(getRversion()), TMB = as.character(utils::packageVersion("TMB")),
  architecture = R.version$platform, source_md5 = unname(tools::md5sum(file.path(root, "models", paste0(request$model, ".cpp"))))
)
cat(jsonlite::toJSON(result, auto_unbox = TRUE, digits = 17, null = "null"), "\n")
