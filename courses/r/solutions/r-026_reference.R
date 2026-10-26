# r-026: complete reference for the declared synthetic inputs.
inspect_local_package <- function() {
  root <- tempfile("measurekit-")
  dir.create(root)
  on.exit(unlink(root, recursive = TRUE), add = TRUE)
  dir.create(file.path(root, "R"))
  writeLines(c(
    "Package: measurekit", "Version: 0.0.1", "Title: Local Contract Example",
    "Description: Demonstrates a bounded package source layout.",
    "License: MIT", "Authors@R: person('Example', 'Author', role=c('aut','cre'), email='example@example.invalid')",
    "Imports: stats"
  ), file.path(root, "DESCRIPTION"))
  writeLines("export(observed_mean)", file.path(root, "NAMESPACE"))
  definition <- c(
    ".validate <- function(x) {",
    "  if (!is.numeric(x) || any(!is.finite(x))) stop('finite numeric values required')",
    "  x", "}",
    "observed_mean <- function(x) {",
    "  x <- .validate(x)",
    "  if (!length(x)) return(NA_real_)",
    "  mean(x)", "}"
  )
  writeLines(definition, file.path(root, "R", "summary.R"))
  metadata <- read.dcf(file.path(root, "DESCRIPTION"))
  stopifnot(metadata[1, "Package"] == "measurekit")
  stopifnot(identical(readLines(file.path(root, "NAMESPACE")), "export(observed_mean)"))
  parsed <- parse(file.path(root, "R", "summary.R"), keep.source = FALSE)
  stopifnot(length(parsed) == 2L)
  environment <- new.env(parent = baseenv())
  sys.source(file.path(root, "R", "summary.R"), envir = environment)
  stopifnot(environment$observed_mean(c(2, 4)) == 3)
  list(files = sort(list.files(root, recursive = TRUE)), mean = environment$observed_mean(c(2, 4)))
}
assert_error <- function(expr, pattern) {
  message <- tryCatch(
    {
      force(expr); NULL
    },
    error = conditionMessage
  )
  stopifnot(is.character(message), length(message) == 1L, grepl(pattern, message))
}

median <- function(x, ...) -999
stopifnot(median(c(1, 4, 9)) == -999, stats::median(c(1, 4, 9)) == 4)
public <- getExportedValue("stats", "median")
stopifnot(public(c(1, 4, 9)) == 4, "median" %in% getNamespaceExports("stats"))
result <- inspect_local_package()
stopifnot(identical(result$files, c("DESCRIPTION", "NAMESPACE", "R/summary.R")), result$mean == 3)
observed_mean <- function(x) {
  if (!is.numeric(x) || any(!is.finite(x))) stop("finite numeric values required")
  if (!length(x)) return(NA_real_)
  mean(x)
}
stopifnot(is.na(observed_mean(numeric(0))))
assert_error(observed_mean(c(1, Inf)), "finite numeric values")
stopifnot(isTRUE(all.equal(stats::dnorm(0), 1 / sqrt(2 * pi))))
cat("r-026 reference checks passed\n")
