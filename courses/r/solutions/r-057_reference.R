# r-057: complete reference for the declared synthetic inputs.
d <- data.frame(x = 1:3, observed = c(2, 4, 3), rule = c(2, 4, 6))
p <- plotly::plot_ly(d, x = ~x, y = ~observed, type = "scatter", mode = "markers", name = "Observed")
p <- plotly::add_lines(p, y = ~rule, name = "Rule: 2x")
p <- plotly::layout(p, xaxis = list(title = "Input"), yaxis = list(title = "Response"))
built <- plotly::plotly_build(p)
stopifnot(length(built$x$data) == 2, built$x$data[[1]]$type == "scatter")
stopifnot(max(abs(as.numeric(built$x$data[[1]]$y) - d$observed)) < 1e-12)
stopifnot(max(abs(as.numeric(built$x$data[[2]]$y) - d$rule)) < 1e-12)
unsorted <- data.frame(x = c(3, 1, 2), y = c(6, 2, 4)); ordered <- unsorted[order(unsorted$x), ]
stopifnot(identical(ordered$x, c(1, 2, 3)), identical(ordered$y, c(2, 4, 6)))
counts <- data.frame(category = c("A", "B", "C"), count = c(2, 1, 3))
bar <- plotly::plot_ly(counts, x = ~category, y = ~count, type = "bar", name = "Count")
bar <- plotly::layout(bar, yaxis = list(title = "Count", rangemode = "tozero"))
b <- plotly::plotly_build(bar)$x$data[[1]]
stopifnot(identical(as.character(b$x), counts$category), identical(as.numeric(b$y), counts$count))
print(p)
print(bar)
cat("r-057 reference checks passed\n")
