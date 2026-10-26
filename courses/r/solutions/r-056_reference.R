# r-056: complete reference for the declared synthetic inputs.
d <- data.frame(id = 1:8, x = 0:7)
d$y <- 1 + 2 * d$x + c(-0.3, 0.2, 0.1, -0.2, 0.4, -0.1, 0.2, -0.3)
fit <- lm(y ~ x, data = d)
z <- data.frame(id = d$id, fitted = fitted(fit), residual = residuals(fit))
stopifnot(nrow(z) == 8, !anyDuplicated(z$id), max(abs(unname(coef(fit)) - c(1, 2))) < 1e-10)
p <- ggplot2::ggplot(z, ggplot2::aes(fitted, residual)) +
  ggplot2::geom_point() +
  ggplot2::geom_hline(yintercept = 0, linetype = "dashed")
stopifnot(max(abs(ggplot2::ggplot_build(p)$data[[1]]$y - z$residual)) < 1e-12)
qq <- ggplot2::ggplot(z, ggplot2::aes(sample = residual)) +
  ggplot2::stat_qq() +
  ggplot2::stat_qq_line() +
  ggplot2::labs(x = "Normal reference quantile", y = "Ordered residual")
stopifnot(nrow(ggplot2::ggplot_build(qq)$data[[1]]) == 8)
f <- data.frame(x = rep(1:4, each = 2)); f$y <- 2 * f$x + rep(c(-1, 1), 4) * f$x
ff <- lm(y ~ x, data = f)
stopifnot(abs(coef(ff)[["x"]] - 2) < 1e-10, abs(cor(abs(residuals(ff)), fitted(ff)) - 1) < 1e-10)
print(p)
print(qq)
cat("r-056 reference checks passed\n")
