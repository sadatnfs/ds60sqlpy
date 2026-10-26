# r-053: complete reference for the declared synthetic inputs.
d <- data.frame(x = 1:4, y = c(1, 3, 2, 6), group = factor(c("A", "A", "B", "B"), levels = c("A", "B")))
mapped <- ggplot2::ggplot(d, ggplot2::aes(x, y, colour = group, shape = group)) +
  ggplot2::geom_point(size = 3) +
  ggplot2::scale_colour_manual(values = c(A = "#0072B2", B = "#D55E00"))
b <- ggplot2::ggplot_build(mapped)$data[[1]]
stopifnot(nrow(b) == 4, length(unique(b$colour)) == 2, length(unique(b$shape)) == 2)
constant <- ggplot2::ggplot(d, ggplot2::aes(x, y)) +
  ggplot2::geom_point(colour = "#0072B2")
stopifnot(length(unique(ggplot2::ggplot_build(constant)$data[[1]]$colour)) == 1)
means <- aggregate(cbind(x, y) ~ group, d, mean)
layered <- mapped + ggplot2::geom_point(data = means, mapping = ggplot2::aes(x, y), inherit.aes = FALSE, colour = "black", shape = 4, size = 5)
layers <- ggplot2::ggplot_build(layered)$data
stopifnot(nrow(layers[[1]]) == 4, nrow(layers[[2]]) == 2, max(abs(sort(layers[[2]]$y) - c(2, 4))) < 1e-12)
literal <- ggplot2::ggplot(d, ggplot2::aes(x, y, colour = "group")) +
  ggplot2::geom_point()
stopifnot(length(unique(ggplot2::ggplot_build(literal)$data[[1]]$colour)) == 1)
print(mapped)
print(layered)
cat("r-053 reference checks passed\n")
