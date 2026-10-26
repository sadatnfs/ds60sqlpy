# r-021: complete reference for the declared synthetic inputs.
new_measurement <- function(values, unit) {
  structure(list(values = values, unit = unit), class = "measurement")
}
validate_measurement <- function(x) {
  if (!inherits(x, "measurement") || !is.list(x) ||
    !is.numeric(x$values) || is.complex(x$values) ||
    !is.null(dim(x$values)) || any(!is.finite(x$values))) {
    stop("values must be a finite numeric vector", call. = FALSE)
  }
  if (!is.character(x$unit) || length(x$unit) != 1L ||
    is.na(x$unit) || !nzchar(x$unit)) {
    stop("unit must be one nonempty string", call. = FALSE)
  }
  x
}
measurement <- function(values, unit) {
  validate_measurement(new_measurement(values, unit))
}
measurement_total <- function(x, ...) UseMethod("measurement_total")
measurement_total.measurement <- function(x, ...) {
  x <- validate_measurement(x)
  setNames(sum(x$values), x$unit)
}
measurement_total.default <- function(x, ...) {
  stop("measurement_total requires a measurement", call. = FALSE)
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

x <- measurement(c(3, 7), "ms")
y <- measurement(c(x$values, 5), x$unit)
stopifnot(identical(measurement_total(x), c(ms = 10)))
stopifnot(identical(measurement_total(y), c(ms = 15)))
measurement_count <- function(x, ...) UseMethod("measurement_count")
measurement_count.measurement <- function(x, ...) length(validate_measurement(x)$values)
measurement_count.default <- function(x, ...) stop("unsupported count input")
stopifnot(identical(measurement_count(y), 3L))
assert_error(measurement_count(1), "unsupported count")
assert_error(measurement_total(new_measurement(c(1, Inf), "ms")), "finite numeric vector")
assert_error(measurement(matrix(1:4, 2), "ms"), "finite numeric vector")
assert_error(measurement(c(1, NA_real_), "ms"), "finite numeric vector")
assert_error(measurement(1, ""), "nonempty string")
empty <- measurement(numeric(0), "ms")
stopifnot(measurement_count(empty) == 0L, identical(measurement_total(empty), c(ms = 0)))
copy <- x
copy$values[[1]] <- 9
stopifnot(x$values[[1]] == 3, copy$values[[1]] == 9)
cat("r-021 reference checks passed\n")
