# SPDX-License-Identifier: MIT
# Source-bound finite registry execution; serialized requests contain data only.
arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 4L) stop("Usage: Rscript R/run.R SOURCE_ROOT PREPARED REQUEST_JSON OUTPUT_DIRECTORY")
root <- normalizePath(arguments[1], mustWork = TRUE)
prepared <- normalizePath(arguments[2], mustWork = TRUE)
request_path <- normalizePath(arguments[3], mustWork = TRUE)
output <- arguments[4]
if (dir.exists(output) || file.exists(output)) stop("Choose a fresh case output directory")
dir.create(output, recursive = TRUE)
for (name in c("common.R", "regularization.R", "native_cases.R", "glmm_cases.R")) {
  source(file.path(root, "R", name), local = TRUE)
}
request <- reference_read_json(request_path)
reference_assert(setequal(names(request), c("case", "seed", "options")), "Unexpected request fields")
reference_assert(is.character(request$case) && length(request$case) == 1L, "Case must be a registered identifier")
reference_assert(is.numeric(request$seed) && length(request$seed) == 1L && request$seed %% 1 == 0 &&
  request$seed >= 1 && request$seed <= 100000000, "Seed is outside the explicit bound")
registry <- reference_read_json(file.path(root, "registry.json"))
entry <- registry$cases[[request$case]]
reference_assert(!is.null(entry), "Unknown prepared case")
reference_assert(setequal(names(request$options), names(entry$options)), "Case option set differs from its registry")
for (name in names(entry$options)) {
  reference_assert(is.character(request$options[[name]]) && length(request$options[[name]]) == 1L &&
    request$options[[name]] %in% unlist(entry$options[[name]]), "Unsupported case option")
}
engine <- reference_engine(root, prepared)
started <- proc.time()[["elapsed"]]
result <- tryCatch(
  {
    function_name <- entry[["function"]]
    reference_assert(
      startsWith(function_name, "reference_") && exists(function_name, mode = "function"),
      "Prepared registry function is unavailable"
    )
    options <- c(request$options, entry$fixed_options)
    value <- do.call(get(function_name, mode = "function"), c(list(engine = engine, seed = as.integer(request$seed)), options))
    if (!is.null(value$fixture)) {
      fixture_path <- file.path(output, "fixture.json")
      jsonlite::write_json(value$fixture, fixture_path,
        pretty = FALSE, auto_unbox = TRUE, digits = NA,
        na = "null", null = "null"
      )
      value$fixture <- NULL
      value$fixture_sha256 <- reference_hash(fixture_path)
    }
    list(
      schema_version = 1L, status = "passed", request = request, result = value,
      scope = "serial optional R/TMB/glmmTMB reference; no Spark or native-port claim",
      prepared_manifest_sha256 = reference_hash(file.path(prepared, "manifest.json")),
      source_revision = engine$manifest$upstream_revision, packages = reference_versions(),
      elapsed_seconds = proc.time()[["elapsed"]] - started
    )
  },
  error = function(condition) {
    list(
      schema_version = 1L, status = "failed", request = request,
      error = list(class = class(condition)[1], message = conditionMessage(condition)),
      prepared_manifest_sha256 = reference_hash(file.path(prepared, "manifest.json")),
      elapsed_seconds = proc.time()[["elapsed"]] - started
    )
  }
)
jsonlite::write_json(result, file.path(output, "result.json"),
  pretty = TRUE, auto_unbox = TRUE,
  digits = NA, na = "null", null = "null"
)
if (!identical(result$status, "passed")) quit(status = 1L)
