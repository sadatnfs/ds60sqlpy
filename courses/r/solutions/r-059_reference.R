# r-059: complete reference for the declared synthetic inputs.
d <- data.frame(x = 1:4, y = c(1, 3, 2, 6), group = c("A", "A", "B", "B"))
p <- ggplot2::ggplot(d, ggplot2::aes(x, y, colour = group)) +
  ggplot2::geom_point(size = 3) +
  ggplot2::labs(x = "Input", y = "Response", colour = "Group")
interactive <- plotly::ggplotly(p, tooltip = c("x", "y", "group"))
traces <- Filter(function(trace) identical(trace$type, "scatter") && isTRUE(grepl("markers", trace$mode)), plotly::plotly_build(interactive)$x$data)
stopifnot(all(vapply(traces, function(trace) length(trace$x) == length(trace$y), logical(1))))
pairs <- unlist(lapply(traces, function(trace) paste(as.numeric(trace$x), as.numeric(trace$y), sep = ":")), use.names = FALSE)
stopifnot(length(pairs) == 4, identical(sort(pairs), sort(paste(d$x, d$y, sep = ":"))))
line_plot <- p + ggplot2::geom_hline(yintercept = mean(d$y), linetype = "dashed")
line_widget <- plotly::ggplotly(line_plot, tooltip = c("x", "y", "group"))
all_traces <- plotly::plotly_build(line_widget)$x$data
stopifnot(length(all_traces) >= 3)
marker_count <- sum(vapply(all_traces, function(trace) if (isTRUE(grepl("markers", trace$mode))) length(trace$x) else 0L, integer(1)))
stopifnot(marker_count == 4)
print(p)
print(interactive)
cat("r-059 reference checks passed\n")
