# r-038: complete reference for the declared synthetic inputs.
counts <- matrix(c(30, 70, 10, 90), nrow = 2, byrow = TRUE)
stopifnot(sum(counts[, 1]) == 40, counts[1, 1] / sum(counts[, 1]) == 0.75)
p_a <- 0.2; p_alert <- 0.3 * p_a + 0.1 * (1 - p_a)
stopifnot(isTRUE(all.equal(p_alert, 0.14)), isTRUE(all.equal(0.3 * p_a / p_alert, 3 / 7)))
joint <- counts / sum(counts)
stopifnot(isTRUE(all.equal(sum(joint), 1)))
conditional <- function(numerator, denominator) if (denominator > 0) numerator / denominator else NA_real_
stopifnot(is.na(conditional(0, 0)), conditional(30, 100) == 0.3)
stopifnot(conditional(30, 100) != conditional(30, 40))
cat("r-038 reference checks passed\n")
