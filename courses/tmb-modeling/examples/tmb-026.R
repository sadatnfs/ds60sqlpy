start <- c(2, 2, 7); mapping <- factor(c(1, 1, NA))
reconstruct <- function(free) {
  result <- start; result[!is.na(mapping)] <- free[as.integer(mapping[!is.na(mapping)])]; result
}
print(reconstruct(3));stopifnot(identical(reconstruct(3), c(3, 3, 7)))
a <- c(1, 2, 3);b <- c(1, 2, 9)
print(c(same_length = length(a) == length(b), objective_a = sum(a^2) / 2, objective_b = sum(b^2) / 2))
