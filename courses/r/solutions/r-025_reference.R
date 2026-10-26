# r-025: complete reference for the declared synthetic inputs.
measurement_record <- function(values, unit) {
  if (!is.numeric(values) || is.complex(values) || !is.null(dim(values)) ||
    any(!is.finite(values))) stop("values must be a finite numeric vector")
  if (!is.character(unit) || length(unit) != 1L || is.na(unit) || !nzchar(unit)) {
    stop("unit must be one nonempty string")
  }
  list(values = as.double(values), unit = unit)
}
record_mean <- function(record) {
  checked <- measurement_record(record$values, record$unit)
  list(
    mean = if (length(checked$values)) mean(checked$values) else NA_real_,
    count = length(checked$values), unit = checked$unit
  )
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

s3 <- structure(list(values = c(2, 4), unit = "ms"), class = "measure_s3")
from_s3 <- function(x) {
  stopifnot(inherits(x, "measure_s3"))
  measurement_record(x$values, x$unit)
}
methods::setClass("MeasureS4", slots = c(values = "numeric", unit = "character"))
s4 <- methods::new("MeasureS4", values = c(2, 4), unit = "ms")
from_s4 <- function(x) {
  stopifnot(methods::is(x, "MeasureS4"))
  measurement_record(x@values, x@unit)
}
Store <- R6::R6Class("Store", private = list(data = NULL, label = NULL), public = list(
  initialize = function(values, unit) {
    record <- measurement_record(values, unit)
    private$data <- record$values
    private$label <- record$unit
  },
  values = function() private$data,
  unit = function() private$label
))
r6 <- Store$new(c(2, 4), "ms")
from_r6 <- function(x) measurement_record(x$values(), x$unit())
Series <- S7::new_class("Series", properties = list(values = S7::class_numeric, unit = S7::class_character))
s7 <- Series(values = c(2, 4), unit = "ms")
from_s7 <- function(x) {
  stopifnot(S7::S7_inherits(x, Series))
  measurement_record(x@values, x@unit)
}
records <- list(from_s3(s3), from_s4(s4), from_r6(r6), from_s7(s7))
stopifnot(all(vapply(records, identical, logical(1), records[[1]])))
stopifnot(identical(record_mean(records[[1]]), list(mean = 3, count = 2L, unit = "ms")))
copy <- from_r6(r6)
copy$values[[1]] <- 100
stopifnot(r6$values()[[1]] == 2)
assert_error(measurement_record(c(1, Inf), "ms"), "finite numeric")
empty <- record_mean(measurement_record(numeric(0), "ms"))
stopifnot(empty$count == 0L, is.na(empty$mean), empty$unit == "ms")
data <- data.frame(time = c(1, 2, 3), latency = c(4, 7, 9))
plot <- ggplot2::ggplot(data, ggplot2::aes(x = time, y = latency)) +
  ggplot2::geom_point()
layer <- ggplot2::ggplot_build(plot)$data[[1]]
stopifnot(identical(layer$x, data$time), identical(layer$y, data$latency))
cat("r-025 reference checks passed\n")
