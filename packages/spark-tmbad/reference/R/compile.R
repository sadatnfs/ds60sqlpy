# SPDX-License-Identifier: MIT
# Explicit preparation only. Runtime entrypoints never source this builder.
arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 2L) stop("Usage: Rscript R/compile.R SOURCE_ROOT FRESH_MODELS_DIRECTORY")
root <- normalizePath(arguments[1], mustWork = TRUE)
output <- arguments[2]
if (dir.exists(output) || file.exists(output)) stop("Use a fresh model build directory")
dir.create(output, recursive = TRUE)
output <- normalizePath(output, mustWork = TRUE)
registry <- jsonlite::fromJSON(file.path(root, "registry.json"))
models <- list()
original <- getwd()
setwd(output)
for (name in registry$models) {
  source <- file.path(root, "models", paste0(name, ".cpp"))
  file.copy(source, paste0(name, ".cpp"), overwrite = FALSE)
  status <- TMB::compile(paste0(name, ".cpp"), flags = "-O1 -g0", framework = "CppAD", safeunload = TRUE)
  if (status != 0L) stop(paste("Template compilation failed:", name))
  library <- paste0(name, .Platform$dynlib.ext)
  stopifnot(file.exists(library))
  models[[name]] <- list(
    library = file.path("models", library),
    sha256 = digest::digest(file = library, algo = "sha256", serialize = FALSE),
    source_sha256 = digest::digest(file = source, algo = "sha256", serialize = FALSE),
    framework = "CppAD", flags = "-O1 -g0"
  )
}
packages <- c("TMB", "glmmTMB", "RTMB", "Matrix", "RcppEigen", "jsonlite", "digest")
identity <- list(
  models = models, r_version = as.character(getRversion()), architecture = R.version$arch,
  packages = setNames(lapply(packages, function(name) as.character(packageVersion(name))), packages)
)
jsonlite::write_json(identity, "compile.json", pretty = TRUE, auto_unbox = TRUE, digits = NA)
