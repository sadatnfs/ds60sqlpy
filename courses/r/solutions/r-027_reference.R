# r-027: complete reference for the declared synthetic inputs.
row_means_loop <- function(x) {
  result <- numeric(nrow(x))
  for (i in seq_len(nrow(x))) result[[i]] <- mean(x[i, ])
  result
}
profile_equivalent_work <- function(x) {
  stopifnot(is.matrix(x), is.numeric(x), all(is.finite(x)))
  reference <- row_means_loop(x)
  vectorized <- rowMeans(x)
  stopifnot(isTRUE(all.equal(reference, vectorized, tolerance = 1e-12)))
  slow_time <- system.time(for (i in seq_len(20L)) row_means_loop(x))[["elapsed"]]
  fast_time <- system.time(for (i in seq_len(20L)) rowMeans(x))[["elapsed"]]
  path <- tempfile(fileext = ".Rprof")
  on.exit(unlink(path), add = TRUE)
  utils::Rprof(path, interval = 0.01)
  on.exit(utils::Rprof(NULL), add = TRUE)
  for (i in seq_len(30L)) row_means_loop(x)
  utils::Rprof(NULL)
  profile <- utils::summaryRprof(path)
  list(
    loop_seconds = slow_time, vector_seconds = fast_time,
    sampled_seconds = profile$sampling.time, top = head(profile$by.total, 5L),
    input_bytes = as.numeric(utils::object.size(x))
  )
}

small <- matrix(1:6, nrow = 2)
stopifnot(identical(row_means_loop(small), c(3, 4)))
growing <- function(x) {
  output <- numeric(0)
  for (i in seq_len(nrow(x))) output <- c(output, mean(x[i, ]))
  output
}
x <- matrix(seq_len(6000) / 100, nrow = 300)
stopifnot(isTRUE(all.equal(growing(x), row_means_loop(x))))
stopifnot(isTRUE(all.equal(row_means_loop(x), rowMeans(x))))
missing <- matrix(c(1, NA_real_, 3, 4), nrow = 2)
stopifnot(is.na(rowMeans(missing)[[2]]), rowMeans(missing, na.rm = TRUE)[[2]] == 4)
result <- profile_equivalent_work(x)
stopifnot(result$loop_seconds >= 0, result$vector_seconds >= 0)
stopifnot(result$sampled_seconds >= 0, result$input_bytes > 0)
print(result)
cat("r-027 reference checks passed\n")
