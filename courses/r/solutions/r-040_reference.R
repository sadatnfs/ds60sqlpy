# r-040: complete reference for the declared synthetic inputs.
analyze <- function(raw, dimension) {
  stopifnot(is.data.frame(raw), is.data.frame(dimension))
  stopifnot(all(c("id", "segment", "amount") %in% names(raw)), all(c("segment", "label") %in% names(dimension)))
  stopifnot(is.character(raw$id), is.character(raw$segment), is.numeric(raw$amount), is.character(dimension$segment), is.character(dimension$label))
  stopifnot(!anyNA(raw$id), !anyDuplicated(raw$id), !anyNA(dimension$segment), !anyDuplicated(dimension$segment))
  keep <- is.finite(raw$amount) & raw$amount >= 0
  data <- raw[keep, , drop = FALSE]
  index <- match(data$segment, dimension$segment)
  stopifnot(!anyNA(index))
  data$label <- dimension$label[index]
  groups <- split(data$amount, data$label)
  count <- vapply(groups, length, integer(1)); total <- vapply(groups, sum, numeric(1))
  report <- data.frame(label = as.character(names(groups)), count = unname(count), total = unname(total), mean = unname(total / count))
  stopifnot(sum(report$count) == nrow(data), sum(report$total) == sum(data$amount))
  list(report = report, input = nrow(raw), admitted = nrow(data), rejected = sum(!keep), overall = if (nrow(data)) sum(data$amount) / nrow(data) else NA_real_)
}
raw <- data.frame(id = c("R1", "R2", "R3", "R4"), segment = c("A", "B", "A", "B"), amount = c(10, 20, NA_real_, 40))
dimension <- data.frame(segment = c("A", "B"), label = c("Alpha", "Beta"))
result <- analyze(raw, dimension)
stopifnot(result$admitted == 3L, result$rejected == 1L, isTRUE(all.equal(result$overall, 70 / 3)))
changed <- raw; changed$amount[[3]] <- 30
stopifnot(analyze(changed, dimension)$overall == 25)
bad <- tryCatch(
  {
    analyze(raw, rbind(dimension, dimension[1, ])); FALSE
  },
  error = function(e) TRUE
)
stopifnot(bad)
empty <- raw; empty$amount[] <- NA_real_
empty_result <- analyze(empty, dimension)
stopifnot(empty_result$admitted == 0L, is.na(empty_result$overall), nrow(empty_result$report) == 0L)
stopifnot(identical(names(empty_result$report), c("label", "count", "total", "mean")))
wrong_type <- raw; wrong_type$amount <- as.character(wrong_type$amount)
rejected_type <- tryCatch(
  {
    analyze(wrong_type, dimension); FALSE
  },
  error = function(e) TRUE
)
stopifnot(rejected_type)
cat("r-040 reference checks passed\n")
