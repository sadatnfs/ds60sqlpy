plan <- data.frame(check = c("array order", "covariance versus precision", "normalizer", "gradient", "native execution"), failure = c("transposed meaning", "wrong quadratic form", "wrong estimator", "wrong optimizer direction", "incompatible binary"))
print(plan)
coverage <- data.frame(family = c("Gaussian model", "new unreviewed primitive"), math = c(TRUE, TRUE), compiled = c(TRUE, FALSE))
print(coverage);stopifnot(!all(coverage$compiled))
