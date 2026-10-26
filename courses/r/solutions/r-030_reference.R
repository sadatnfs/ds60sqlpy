# r-030: complete reference for the declared synthetic inputs.
metric_batch <- function(ids, values, unit) {
  if (!is.character(ids) || anyNA(ids) || any(!nzchar(ids)) || anyDuplicated(ids)) {
    stop("ids must be unique nonempty strings", call. = FALSE)
  }
  if (!is.numeric(values) || is.complex(values) || !is.null(dim(values)) ||
    any(is.nan(values)) || any(is.infinite(values))) {
    stop("values must be a numeric vector with only finite values or NA", call. = FALSE)
  }
  if (length(ids) != length(values)) stop("ids and values must have equal length", call. = FALSE)
  if (!is.character(unit) || length(unit) != 1L || is.na(unit) || !nzchar(unit)) {
    stop("unit must be one nonempty string", call. = FALSE)
  }
  structure(list(ids = ids, values = as.double(values), unit = unit), class = "metric_batch")
}
validate_batch <- function(x) {
  if (!inherits(x, "metric_batch")) stop("expected a metric_batch")
  metric_batch(x$ids, x$values, x$unit)
}
summary.metric_batch <- function(object, ...) {
  x <- validate_batch(object)
  observed <- !is.na(x$values)
  list(
    rows = length(x$ids), observed = sum(observed), missing = sum(!observed),
    mean = if (any(observed)) mean(x$values[observed]) else NA_real_, unit = x$unit
  )
}
combine_batches <- function(x, y) {
  x <- validate_batch(x)
  y <- validate_batch(y)
  if (!identical(x$unit, y$unit)) stop("incompatible batch units")
  metric_batch(c(x$ids, y$ids), c(x$values, y$values), x$unit)
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

a <- metric_batch(c("a", "b", "c"), c(2, NA_real_, 6), "ms")
before <- a
s <- summary(a)
stopifnot(identical(s, list(rows = 3L, observed = 2L, missing = 1L, mean = 4, unit = "ms")))
b <- combine_batches(a, metric_batch("d", 8, "ms"))
stopifnot(summary(b)$rows == 4L, summary(b)$observed == 3L, summary(b)$missing == 1L)
stopifnot(isTRUE(all.equal(summary(b)$mean, 16 / 3)))
assert_error(metric_batch(c("a", "a"), c(2, 4), "ms"), "unique nonempty")
assert_error(metric_batch(c("a", "b"), 2, "ms"), "equal length")
assert_error(metric_batch("a", NaN, "ms"), "finite values or NA")
assert_error(metric_batch("a", Inf, "ms"), "finite values or NA")
all_missing <- metric_batch(c("x", "y"), c(NA_real_, NA_real_), "ms")
stopifnot(summary(all_missing)$missing == 2L, summary(all_missing)$observed == 0L, is.na(summary(all_missing)$mean))
empty <- metric_batch(character(0), numeric(0), "ms")
stopifnot(summary(empty)$rows == 0L, summary(empty)$missing == 0L, is.na(summary(empty)$mean))
forged <- structure(list(ids = "a", values = Inf, unit = "ms"), class = "metric_batch")
assert_error(summary(forged), "finite values or NA")
assert_error(combine_batches(a, metric_batch("e", 1, "s")), "incompatible batch units")
assert_error(combine_batches(a, metric_batch("a", 9, "ms")), "unique nonempty")
stopifnot(identical(a, before), s$mean == 4)
namespace <- c("export(metric_batch)", "export(combine_batches)", "S3method(summary,metric_batch)")
stopifnot(!any(grepl("validate_batch", namespace, fixed = TRUE)))
print(summary(b))
cat("r-030 reference checks passed\n")
