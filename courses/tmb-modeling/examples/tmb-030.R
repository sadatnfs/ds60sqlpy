y <- c(1, 2, 4, 7);sigma <- 2;n <- length(y);center <- mean(y);cutoff <- .5 * qchisq(.95, 1)
rise <- function(mu) n * (mu - center)^2 / (2 * sigma^2) - cutoff
roots <- c(uniroot(rise, c(center - 10, center))$root, uniroot(rise, c(center, center + 10))$root)
exact <- center + c(-1, 1) * sigma * sqrt(2 * cutoff / n)
print(rbind(roots = roots, exact = exact));stopifnot(max(abs(roots - exact)) < 1e-4)
print(c(unconstrained_lower = .1 - 1.96 * .2, positive_domain_boundary = 0))
