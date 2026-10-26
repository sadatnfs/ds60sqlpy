# r-047: complete reference for the declared synthetic inputs.
d <- data.frame(x = 1:8, label = factor(rep(c("low", "high"), each = 4), levels = c("low", "high")))
fit <- rpart::rpart(label ~ x, data = d, method = "class", control = rpart::rpart.control(minsplit = 2, minbucket = 1, maxdepth = 1, cp = 0, xval = 0))
new <- data.frame(x = c(2, 7))
stopifnot(identical(as.character(predict(fit, new, type = "class")), c("low", "high")))
prob <- predict(fit, new, type = "prob")
stopifnot(identical(colnames(prob), c("low", "high")), max(abs(rowSums(prob) - 1)) < 1e-12)
small <- rpart::prune(fit, cp = 1)
stopifnot(nrow(small$frame) == 1, sum(small$frame$var == "<leaf>") == 1)
predict_complete <- function(x) {
  if (anyNA(x) || any(!is.finite(x))) stop("complete finite x required")
  predict(fit, data.frame(x = x), type = "class")
}
stopifnot(inherits(try(predict_complete(NA_real_), silent = TRUE), "try-error"))
stopifnot(as.character(predict_complete(1000)) == "high")
stopifnot(all(as.character(predict(fit, d, type = "class")) == as.character(d$label)))
cat("r-047 reference checks passed\n")
