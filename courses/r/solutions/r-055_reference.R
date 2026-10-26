# r-055: complete reference for the declared synthetic inputs.
d <- data.frame(x = 1:4, y = c(1, 2, 3, 100))
base <- ggplot2::ggplot(d, ggplot2::aes(x, y)) +
  ggplot2::geom_point() +
  ggplot2::geom_smooth(method = "lm", formula = y ~ x, se = FALSE)
zoom <- base + ggplot2::coord_cartesian(ylim = c(0, 4))
limited <- base + ggplot2::scale_y_continuous(limits = c(0, 4))
stopifnot(max(ggplot2::ggplot_build(zoom)$data[[2]]$y, na.rm = TRUE) > 4)
stopifnot(max(ggplot2::ggplot_build(limited)$data[[2]]$y, na.rm = TRUE) <= 4)
f <- data.frame(x = rep(1:2, 2), y = c(1, 2, 100, 200), group = c("A", "A", "B", "B"))
fixed <- ggplot2::ggplot(f, ggplot2::aes(x, y)) +
  ggplot2::geom_point() +
  ggplot2::facet_wrap(~group)
free <- fixed + ggplot2::facet_wrap(~group, scales = "free_y")
stopifnot(length(unique(ggplot2::ggplot_build(fixed)$layout$layout$SCALE_Y)) == 1)
stopifnot(length(unique(ggplot2::ggplot_build(free)$layout$layout$SCALE_Y)) == 2)
positive <- data.frame(x = c(1, 10, 100), y = 1:3)
stopifnot(all(positive$x > 0))
log_plot <- ggplot2::ggplot(positive, ggplot2::aes(x, y)) +
  ggplot2::geom_point() +
  ggplot2::scale_x_log10()
stopifnot(max(abs(ggplot2::ggplot_build(log_plot)$data[[1]]$x - 0:2)) < 1e-12)
palette <- c(A = "#0072B2", B = "#D55E00")
stopifnot(!all(c("A", "C") %in% names(palette)))
print(zoom)
print(limited)
cat("r-055 reference checks passed\n")
