# r-054: complete reference for the declared synthetic inputs.
d <- data.frame(category = factor(c("A", "A", "B", "C", "C", "C"), levels = c("A", "B", "C")))
counts <- data.frame(category = factor(c("A", "B", "C"), levels = c("A", "B", "C")), n = c(2, 1, 3))
p <- ggplot2::ggplot(d, ggplot2::aes(category)) +
  ggplot2::geom_bar()
identity <- ggplot2::ggplot(counts, ggplot2::aes(category, n)) +
  ggplot2::geom_col()
stopifnot(identical(as.numeric(ggplot2::ggplot_build(p)$data[[1]]$y), c(2, 1, 3)))
stopifnot(identical(as.numeric(ggplot2::ggplot_build(identity)$data[[1]]$y), c(2, 1, 3)))
bad <- ggplot2::ggplot(counts, ggplot2::aes(category, n)) +
  ggplot2::geom_bar()
stopifnot(inherits(try(ggplot2::ggplot_build(bad), silent = TRUE), "try-error"))
paths <- data.frame(time = rep(1:3, 2), value = c(1, 2, 3, 3, 2, 1), person = rep(c("A", "B"), each = 3))
lines <- ggplot2::ggplot(paths, ggplot2::aes(time, value, group = person, colour = person)) +
  ggplot2::geom_line() +
  ggplot2::geom_point()
stopifnot(length(unique(ggplot2::ggplot_build(lines)$data[[1]]$group)) == 2)
histogram <- ggplot2::ggplot(data.frame(value = c(1, 2, 3, 4)), ggplot2::aes(value)) +
  ggplot2::geom_histogram(binwidth = 2, boundary = 0, closed = "left")
stopifnot(sum(ggplot2::ggplot_build(histogram)$data[[1]]$count) == 4)
print(p)
print(lines)
cat("r-054 reference checks passed\n")
