# r-035: complete reference for the declared synthetic inputs.
validate <- function(data) {
  stopifnot(all(c("id", "amount") %in% names(data)), is.character(data$id), is.numeric(data$amount))
  flags <- data.frame(missing_id = is.na(data$id) | data$id == "", invalid_amount = !is.finite(data$amount) | data$amount < 0)
  keep <- !flags$missing_id & !flags$invalid_amount
  list(admitted = data[keep, , drop = FALSE], rejected = cbind(data[!keep, , drop = FALSE], flags[!keep, , drop = FALSE]))
}
raw <- data.frame(id = c("A", "", "C", "D"), amount = c(2, -3, -1, NA_real_))
result <- validate(raw)
stopifnot(nrow(result$admitted) == 1L, nrow(result$rejected) == 3L)
stopifnot(result$rejected$missing_id[[1]], result$rejected$invalid_amount[[1]])
stopifnot(nrow(result$admitted) + nrow(result$rejected) == nrow(raw))
empty <- validate(raw[integer(0), , drop = FALSE])
stopifnot(nrow(empty$admitted) == 0L, nrow(empty$rejected) == 0L)
cat("r-035 reference checks passed\n")
