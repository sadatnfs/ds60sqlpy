# r-058: complete reference for the declared synthetic inputs.
d <- data.frame(id = c("A1", "A2", "B1", "B2"), group = c("A", "A", "B", "B"), x = c(1, 2, 1, 2), y = c(2, 3, 4, 6))
p <- plotly::plot_ly()
for (g in c("A", "B")) {
  part <- d[d$group == g, ]
  p <- plotly::add_trace(p, data = part, x = ~x, y = ~y, customdata = ~id, type = "scatter", mode = "markers", name = g, hovertemplate = "ID: %{customdata}<br>Input: %{x}<br>Value: %{y}<extra>%{fullData.name}</extra>")
}
buttons <- list(list(label = "All groups", method = "restyle", args = list("visible", list(TRUE, TRUE))), list(label = "Group A", method = "restyle", args = list("visible", list(TRUE, FALSE))))
p <- plotly::layout(p, updatemenus = list(list(type = "buttons", buttons = buttons)), xaxis = list(title = "Input"), yaxis = list(title = "Value"))
b <- plotly::plotly_build(p)
stopifnot(length(b$x$data) == 2, identical(as.character(b$x$data[[1]]$customdata), c("A1", "A2")))
stopifnot(identical(as.character(b$x$data[[2]]$customdata), c("B1", "B2")))
stopifnot(identical(unlist(b$x$layout$updatemenus[[1]]$buttons[[2]]$args[[2]]), c(TRUE, FALSE)))
stopifnot(nrow(d) == 4, mean(d$y) == 3.75, mean(d$y[d$group == "A"]) == 2.5)
selected <- d[d$group == "A", ]
stopifnot(nrow(selected) == 2, all(selected$id %in% c("A1", "A2")))
print(d)
print(p)
cat("r-058 reference checks passed\n")
