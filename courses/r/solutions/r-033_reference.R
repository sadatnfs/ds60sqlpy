# r-033: complete reference for the declared synthetic inputs.
dimension <- data.frame(product = c("A", "B"), category = c("Paper", "Home"))
facts <- data.frame(product = c("B", "A", "B"), amount = c(10, 20, 30))
lookup <- function(facts, dimension) {
  stopifnot(!anyNA(dimension$product), !anyDuplicated(dimension$product))
  index <- match(facts$product, dimension$product)
  stopifnot(!anyNA(index))
  facts$category <- dimension$category[index]
  facts
}
result <- lookup(facts, dimension)
stopifnot(identical(result$category, c("Home", "Paper", "Home")), sum(result$amount) == 60)
unmatched <- tryCatch(
  {
    lookup(data.frame(product = "C", amount = 1), dimension); FALSE
  },
  error = function(e) TRUE
)
duplicated <- tryCatch(
  {
    lookup(facts, rbind(dimension, dimension[1, ])); FALSE
  },
  error = function(e) TRUE
)
stopifnot(unmatched, duplicated)
empty <- lookup(facts[integer(0), , drop = FALSE], dimension)
stopifnot(nrow(empty) == 0L, identical(names(empty), c("product", "amount", "category")))
cat("r-033 reference checks passed\n")
