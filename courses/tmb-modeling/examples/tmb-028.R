estimate <- c(intercept = 1, slope = .4);V <- matrix(c(.04, .01, .01, .09), 2, 2)
contrast <- c(-1, 2)
print(c(estimate = sum(contrast * estimate), se = sqrt(drop(t(contrast) %*% V %*% contrast))))
m <- .5;v <- .3
print(c(transform_of_mean = exp(m), mean_of_transform = exp(m + v / 2)))
stopifnot(exp(m + v / 2) > exp(m))
