# r-023: complete reference for the declared synthetic inputs.
Counter <- R6::R6Class("Counter", private = list(value = 0), public = list(
  initialize = function(initial = 0) {
    if (!is.numeric(initial) || length(initial) != 1L || !is.finite(initial) || initial < 0) {
      stop("initial must be one nonnegative finite number")
    }
    private$value <- initial
  },
  add = function(amount) {
    if (!is.numeric(amount) || length(amount) != 1L || !is.finite(amount) || amount < 0) {
      stop("amount must be one nonnegative finite number")
    }
    if (!is.finite(private$value + amount)) stop("counter overflow")
    private$value <- private$value + amount
    invisible(self)
  },
  read = function() private$value
))
assert_error <- function(expr, pattern) {
  message <- tryCatch(
    {
      force(expr); NULL
    },
    error = conditionMessage
  )
  stopifnot(is.character(message), length(message) == 1L, grepl(pattern, message))
}

a <- Counter$new(2)
b <- a
b$add(3)
stopifnot(identical(a, b), a$read() == 5, b$read() == 5)
copy <- a$clone()
copy$add(4)
stopifnot(copy$read() == 9, a$read() == 5)
before <- a$read()
assert_error(a$add(-1), "nonnegative finite")
assert_error(a$add(NA_real_), "nonnegative finite")
stopifnot(a$read() == before)
Box <- R6::R6Class("Box", public = list(
  counter = NULL,
  initialize = function(counter) self$counter <- counter
))
original <- Box$new(Counter$new(1))
shallow <- original$clone()
deep <- original$clone(deep = TRUE)
shallow$counter$add(2)
deep$counter$add(5)
stopifnot(original$counter$read() == 3, shallow$counter$read() == 3, deep$counter$read() == 6)
fold_values <- vapply(c(2, 5, 1), function(amount) {
  counter <- Counter$new()
  counter$add(amount)
  counter$read()
}, numeric(1))
stopifnot(identical(fold_values, c(2, 5, 1)))
cat("r-023 reference checks passed\n")
