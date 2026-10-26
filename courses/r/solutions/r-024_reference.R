# r-024: complete reference for the declared synthetic inputs.
Series <- S7::new_class("Series",
  properties = list(
    values = S7::class_numeric, unit = S7::class_character
  ),
  validator = function(self) {
    problems <- character(0)
    if (!is.null(dim(self@values)) || any(!is.finite(self@values))) {
      problems <- c(problems, "values must be a finite vector")
    }
    if (length(self@unit) != 1L || is.na(self@unit) || !nzchar(self@unit)) {
      problems <- c(problems, "unit must be one nonempty string")
    }
    if (length(problems)) problems else NULL
  }
)
series_total <- S7::new_generic("series_total", "x")
S7::method(series_total, Series) <- function(x) setNames(sum(x@values), x@unit)
join_series <- S7::new_generic("join_series", c("x", "y"))
S7::method(join_series, list(Series, Series)) <- function(x, y) {
  if (!identical(x@unit, y@unit)) stop("incompatible series units")
  Series(values = c(x@values, y@values), unit = x@unit)
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

x <- Series(values = c(3, 7), unit = "ms")
y <- join_series(x, Series(values = 5, unit = "ms"))
stopifnot(identical(series_total(x), c(ms = 10)), identical(y@values, c(3, 7, 5)))
stopifnot(identical(series_total(y), c(ms = 15)))
series_count <- S7::new_generic("series_count", "x")
S7::method(series_count, Series) <- function(x) length(x@values)
stopifnot(identical(series_count(y), 3L))
assert_error(Series(values = NA_real_, unit = "ms"), "finite vector")
assert_error(
  {
    x@unit <- character(0)
  },
  "nonempty string"
)
stopifnot(identical(x@unit, "ms"))
assert_error(join_series(x, Series(values = 1, unit = "s")), "incompatible series units")
empty <- Series(values = numeric(0), unit = "ms")
stopifnot(series_count(empty) == 0L, series_total(empty)[[1]] == 0)
cat("r-024 reference checks passed\n")
