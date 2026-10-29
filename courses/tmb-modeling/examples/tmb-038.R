validate_group <- function(group, n) {
  if (any(!is.finite(group)) || any(group != floor(group)) || any(group < 0 | group >= n)) stop("invalid group index");TRUE
}
stopifnot(validate_group(c(0, 1, 0), 2))
rejected <- tryCatch(validate_group(c(0, 2), 2), error = function(e) conditionMessage(e));print(rejected)
next_state <- function(compile_status) if (compile_status == 0L) "fresh-load-check" else "failed-build-no-load"
print(c(success = next_state(0L), failure = next_state(1L)));stopifnot(next_state(1L) == "failed-build-no-load")
