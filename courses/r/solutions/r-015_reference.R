# r-015: complete reference for the declared synthetic inputs.
parse_count <- function(text) {
  if (!is.character(text) || length(text) != 1L || is.na(text) || !grepl("^[0-9]+$", text)) stop("invalid count", call. = FALSE)
  value <- suppressWarnings(as.integer(text))
  if (is.na(value)) stop("count exceeds integer range", call. = FALSE)
  value
}
safe <- function(text) tryCatch(list(ok = TRUE, value = parse_count(text), message = NULL), error = function(e) list(ok = FALSE, value = NULL, message = conditionMessage(e)))
stopifnot(safe("0")$ok, safe("0")$value == 0L, !safe("bad")$ok)
stopifnot(!safe("999999999999999999999")$ok, !safe(12)$ok)
old <- getOption("digits")
change_then_fail <- function() {
  previous <- options(digits = 3); on.exit(options(previous), add = TRUE); stop("intentional")
}
tryCatch(change_then_fail(), error = function(e) NULL)
stopifnot(identical(getOption("digits"), old))
cat("r-015 reference checks passed\n")
