# r-051: complete reference for the declared synthetic inputs.
d <- data.frame(x = 0:4, y = 2 * (0:4))
plot(d$x, d$y, xlim = c(0, 4), ylim = c(0, 8), xaxs = "i", yaxs = "i", pch = 16, xlab = "Input value", ylab = "Response value", main = "Pairs and linear rule")
abline(a = 0, b = 2, col = "#1B5E20", lwd = 2)
stopifnot(max(abs(par("usr") - c(0, 4, 0, 8))) < 1e-12, all(d$y == 2 * d$x))
unsorted <- data.frame(time = c(3, 1, 2), value = c(30, 10, 20))
ordered <- unsorted[order(unsorted$time), ]
stopifnot(identical(ordered$time, c(1, 2, 3)), identical(ordered$value, c(10, 20, 30)))
owned_png <- function() {
  path <- tempfile(fileext = ".png")
  grDevices::png(path, width = 500, height = 350, type = "cairo")
  owned <- dev.cur()
  on.exit(
    {
      if (dev.cur() == owned) dev.off(); unlink(path)
    },
    add = TRUE
  )
  plot(1:3, c(2, 1, 4), pch = 16, xlab = "Observation", ylab = "Value")
  dev.off()
  stopifnot(identical(readBin(path, "raw", n = 8), as.raw(c(137, 80, 78, 71, 13, 10, 26, 10))))
  stopifnot(file.info(path)$size > 0)
  path
}
removed <- owned_png()
stopifnot(!file.exists(removed))
cat("r-051 reference checks passed\n")
