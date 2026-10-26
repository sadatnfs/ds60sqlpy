# r-050: complete reference for the declared synthetic inputs.
train <- data.frame(x = c(-2, -1, 0, 1, 2))
train$y <- 1 + 2 * train$x - 0.5 * train$x^2
heldout <- data.frame(id = paste0("q", 1:4), x = c(-1.5, -0.5, 0.5, 1.5))
heldout$actual <- 1 + 2 * heldout$x - 0.5 * heldout$x^2
affine <- lm(y ~ x, data = train)
quadratic <- lm(y ~ x + I(x^2), data = train)
stopifnot(max(abs(unname(coef(quadratic)) - c(1, 2, -0.5))) < 1e-10)
pred <- data.frame(id = heldout$id, prediction = as.numeric(predict(affine, heldout)))
paired <- merge(heldout, pred[4:1, ], by = "id", sort = FALSE)
stopifnot(!anyDuplicated(paired$id), nrow(paired) == 4)
score <- mean((paired$actual - paired$prediction)^2)
stopifnot(abs(score - 0.390625) < 1e-10)
stopifnot(mean((heldout$actual - predict(quadratic, heldout))^2) < 1e-20)
report <- list(metric = "held-out mean squared error", count = 4L, affine = score, R = as.character(getRversion()), limitation = "synthetic four-point assessment")
check_report <- function(value) {
  path <- tempfile(fileext = ".json")
  on.exit(unlink(path), add = TRUE)
  jsonlite::write_json(value, path, auto_unbox = TRUE)
  restored <- jsonlite::read_json(path, simplifyVector = TRUE)
  stopifnot(restored$count == 4, restored$metric == value$metric)
  path
}
removed <- check_report(report)
stopifnot(!file.exists(removed))
cat("r-050 reference checks passed\n")
