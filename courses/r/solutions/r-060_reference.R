# r-060: complete reference for the declared synthetic inputs.
d <- data.frame(id = c(paste0("A", 1:5), paste0("B", 1:5)), group = rep(c("A", "B"), each = 5), value = c(1, 2, 3, 4, NA_real_, 2, 3, 6, 7, NA_real_))
observed <- d[!is.na(d$value), ]
summary <- do.call(rbind, lapply(split(d$value, d$group), function(values) {
  x <- values[!is.na(values)]; n <- length(x); se <- sd(x) / sqrt(n); half <- qt(0.975, n - 1) * se
  data.frame(n = n, missing = sum(is.na(values)), mean = mean(x), se = se, lower = mean(x) - half, upper = mean(x) + half, half = half)
}))
summary$group <- rownames(summary)
stopifnot(nrow(d) == 10, nrow(observed) == 8, sum(summary$missing) == 2, !anyDuplicated(observed$id))
stopifnot(max(abs(summary$mean - c(2.5, 4.5))) < 1e-12, max(abs(summary$se^2 - c(5 / 12, 17 / 12))) < 1e-12)
static <- ggplot2::ggplot(observed, ggplot2::aes(group, value)) +
  ggplot2::geom_point(colour = "#0072B2", size = 2) +
  ggplot2::geom_errorbar(data = summary, mapping = ggplot2::aes(x = group, ymin = lower, ymax = upper), inherit.aes = FALSE, width = 0.15) +
  ggplot2::geom_point(data = summary, mapping = ggplot2::aes(group, mean), inherit.aes = FALSE, shape = 4, size = 4) +
  ggplot2::labs(x = "Group", y = "Observed value and mean interval", caption = "Intervals: 95% Student t intervals for group means; synthetic independent-observation model")
layers <- ggplot2::ggplot_build(static)$data
stopifnot(nrow(layers[[1]]) == 8, nrow(layers[[2]]) == 2, nrow(layers[[3]]) == 2)
interactive <- plotly::plot_ly()
interactive <- plotly::add_trace(interactive, data = observed, x = ~group, y = ~value, customdata = ~id, type = "scatter", mode = "markers", name = "Observed", hovertemplate = "ID: %{customdata}<br>Group: %{x}<br>Value: %{y}<extra>Observed</extra>")
interactive <- plotly::add_trace(interactive, data = summary, x = ~group, y = ~mean, type = "scatter", mode = "markers", name = "Mean and 95% t interval", inherit = FALSE, error_y = list(type = "data", array = summary$half, visible = TRUE))
interactive <- plotly::layout(interactive, xaxis = list(title = "Group"), yaxis = list(title = "Observed value and mean interval"))
traces <- plotly::plotly_build(interactive)$x$data
stopifnot(length(traces) == 2, length(traces[[1]]$x) == 8, length(traces[[2]]$x) == 2)
stopifnot(identical(sort(as.character(traces[[1]]$customdata)), sort(observed$id)))
stopifnot(max(abs(as.numeric(traces[[2]]$error_y$array) - summary$half)) < 1e-12)
stopifnot(diff(summary$mean) == 2)
print(summary)
print(static)
print(interactive)
cat("r-060 reference checks passed\n")
