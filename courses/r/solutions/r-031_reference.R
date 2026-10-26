# r-031: complete reference for the declared synthetic inputs.
transform_lines <- function(lines, threshold = 8) {
  stopifnot(!anyNA(lines$id), !anyDuplicated(lines$id))
  lines$net <- lines$quantity * lines$price - lines$discount
  keep <- !is.na(lines$net) & lines$net >= threshold
  selected <- lines[keep, c("id", "net"), drop = FALSE]
  selected <- selected[order(selected$id), , drop = FALSE]
  list(data = selected, input = nrow(lines), retained = sum(keep), excluded = sum(!keep))
}
lines <- data.frame(id = c("L3", "L1", "L2"), quantity = c(2, 1, NA_real_), price = c(5, 8, 4), discount = c(1, 0, 0))
a <- transform_lines(lines)
stopifnot(identical(a$data$id, c("L1", "L3")), identical(a$data$net, c(8, 9)))
stopifnot(a$input == 3, a$retained == 2, a$excluded == 1)
b <- transform_lines(lines, 9)
stopifnot(identical(b$data$id, "L3"), b$data$net == 9)
empty <- transform_lines(lines, 100)$data
stopifnot(nrow(empty) == 0, identical(names(empty), c("id", "net")))
cat("r-031 reference checks passed\n")
