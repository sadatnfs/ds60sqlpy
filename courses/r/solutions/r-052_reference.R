# r-052: complete reference for the declared synthetic inputs.
groups <- list(A = c(1, 2, 3, 4), B = c(2, 3, 6, 7))
means <- vapply(groups, mean, numeric(1))
se <- vapply(groups, function(x) sd(x) / sqrt(length(x)), numeric(1))
stopifnot(max(abs(means - c(2.5, 4.5))) < 1e-12, max(abs(se^2 - c(5 / 12, 17 / 12))) < 1e-12)
half <- qt(0.975, 3) * se
stopifnot(all(half > se))
draw <- function() {
  old <- par(mfrow = c(1, 2), mar = c(4, 4, 3, 1))
  on.exit(par(old), add = TRUE)
  limits <- range(c(unlist(groups), means - half, means + half))
  plot(rep(1:2, each = 4), unlist(groups), xaxt = "n", ylim = limits, xlab = "Group", ylab = "Observed value", pch = 16)
  axis(1, 1:2, names(groups))
  plot(1:2, means, xaxt = "n", ylim = limits, xlab = "Group", ylab = "Mean and 95% t interval", pch = 16)
  axis(1, 1:2, names(groups))
  arrows(1:2, means - half, 1:2, means + half, angle = 90, code = 3, length = 0.06)
}
before <- par("mfrow")
draw()
stopifnot(identical(par("mfrow"), before), !is.finite(log(0)))
stopifnot(max(abs(diff(log10(c(1, 10, 100))) - c(1, 1))) < 1e-12)
cat("r-052 reference checks passed\n")
