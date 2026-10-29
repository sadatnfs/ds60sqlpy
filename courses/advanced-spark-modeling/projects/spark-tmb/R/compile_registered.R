args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) stop("Usage: compile_registered.R PROJECT_ROOT BUILD_DIR")
root <- normalizePath(args[1], mustWork = TRUE)
build <- normalizePath(args[2], mustWork = TRUE)
registry <- jsonlite::fromJSON(file.path(root, "registry.json"), simplifyVector = FALSE)
actual <- list(
  R = as.character(getRversion()), TMB = as.character(packageVersion("TMB")),
  Matrix = as.character(packageVersion("Matrix")), architecture = R.version$platform
)
for (name in names(registry$abi)) if (!identical(actual[[name]], registry$abi[[name]])) stop("Build ABI differs from registry")
setwd(build)
for (name in names(registry$models)) {
  source <- file.path(root, registry$models[[name]]$source)
  if (!file.copy(source, paste0(name, ".cpp"), overwrite = TRUE)) stop("Cannot stage trusted template")
  status <- TMB::compile(paste0(name, ".cpp"),
    flags = "-O1 -g0", framework = "CppAD",
    openmp = FALSE, safebounds = TRUE, safeunload = TRUE
  )
  if (status != 0L) stop("Trusted template compilation failed")
}
writeLines(jsonlite::toJSON(actual, auto_unbox = TRUE), "abi.json")
