# r-022: complete reference for the declared synthetic inputs.
methods::setClass("FormalMeasure",
  slots = c(values = "numeric", unit = "character"),
  prototype = list(values = numeric(0), unit = "ms")
)
methods::setValidity("FormalMeasure", function(object) {
  problems <- character(0)
  if (!is.null(dim(object@values)) || any(!is.finite(object@values))) {
    problems <- c(problems, "values must be a finite vector")
  }
  if (length(object@unit) != 1L || is.na(object@unit) || !nzchar(object@unit)) {
    problems <- c(problems, "unit must be one nonempty string")
  }
  if (length(problems)) problems else TRUE
})
methods::setGeneric("combine_measure", function(x, y) methods::standardGeneric("combine_measure"))
methods::setMethod("combine_measure", c(x = "FormalMeasure", y = "FormalMeasure"), function(x, y) {
  methods::validObject(x)
  methods::validObject(y)
  if (!identical(x@unit, y@unit)) stop("incompatible units", call. = FALSE)
  methods::new("FormalMeasure", values = c(x@values, y@values), unit = x@unit)
})
methods::setMethod("combine_measure", c(x = "FormalMeasure", y = "numeric"), function(x, y) {
  stop("numeric input has no declared unit", call. = FALSE)
})
assert_error <- function(expr, pattern) {
  message <- tryCatch(
    {
      force(expr); NULL
    },
    error = conditionMessage
  )
  stopifnot(is.character(message), length(message) == 1L, grepl(pattern, message))
}

x <- methods::new("FormalMeasure", values = c(1, 3), unit = "ms")
y <- methods::new("FormalMeasure", values = 5, unit = "ms")
z <- combine_measure(x, y)
stopifnot(identical(z@values, c(1, 3, 5)), z@unit == "ms")
seconds <- methods::new("FormalMeasure", values = 2, unit = "s")
assert_error(combine_measure(x, seconds), "incompatible units")
assert_error(methods::new("FormalMeasure", values = Inf, unit = "ms"), "finite vector")
broken <- x
broken@unit <- character(0)
assert_error(methods::validObject(broken), "nonempty string")
assert_error(combine_measure(x, 2), "no declared unit")
to_ms <- function(x) {
  methods::validObject(x)
  if (x@unit != "s") stop("conversion requires seconds")
  methods::new("FormalMeasure", values = x@values * 1000, unit = "ms")
}
converted <- to_ms(seconds)
stopifnot(converted@values == 2000, converted@unit == "ms", seconds@values == 2, seconds@unit == "s")
assert_error(to_ms(x), "requires seconds")
cat("r-022 reference checks passed\n")
