# r-036: complete reference for the declared synthetic inputs.
combine <- function(chunks) {
  state <- c(observed = 0, missing = 0, total = 0)
  for (chunk in chunks) {
    valid <- !is.na(chunk)
    state <- state + c(observed = sum(valid), missing = sum(!valid), total = sum(chunk[valid]))
  }
  list(state = state, mean = if (state[["observed"]] > 0) state[["total"]] / state[["observed"]] else NA_real_)
}
a <- combine(list(10, c(20, 30, 40))); b <- combine(list(c(10, 20), numeric(0), c(30, 40)))
stopifnot(a$mean == 25, identical(a, b))
missing <- combine(list(NA_real_, c(NA_real_, NA_real_)))
stopifnot(is.na(missing$mean), missing$state[["missing"]] == 3)
c <- combine(list(c(1, NA_real_), c(3, 5), NA_real_))
stopifnot(c$mean == 3, c$state[["observed"]] == 3)
cat("r-036 reference checks passed\n")
