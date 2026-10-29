args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) stop("Usage: Rscript --vanilla R/compile.R SOURCE_ROOT BUILD_DIR")
root <- normalizePath(args[1], mustWork = TRUE)
build_dir <- args[2]
dir.create(build_dir, recursive = TRUE, showWarnings = FALSE)
build_dir <- normalizePath(build_dir, mustWork = TRUE)
source(file.path(root, "R", "api.R"))
if (as.character(getRversion()) != "4.6.1" || as.character(utils::packageVersion("TMB")) != "1.9.25") stop("Prepared R4.6.1/TMB1.9.25 required")
setwd(build_dir)
for (model in model_names) {
  source_path <- file.path(root, "models", paste0(model, ".cpp"))
  if (!file.copy(source_path, paste0(model, ".cpp"), overwrite = TRUE)) stop("Cannot stage model")
  status <- TMB::compile(paste0(model, ".cpp"),
    flags = "-O1 -g0", framework = "CppAD",
    openmp = model == "parallel_gaussian", safebounds = TRUE, safeunload = TRUE
  )
  if (status != 0L) stop(paste("Compilation failed:", model))
}
writeLines(c(
  paste("R", getRversion()), paste("TMB", utils::packageVersion("TMB")),
  paste("Matrix", utils::packageVersion("Matrix")), paste("RcppEigen", utils::packageVersion("RcppEigen")),
  paste("architecture", R.version$platform), "framework CppAD", "flags -O1 -g0"
), "build-receipt.txt")
