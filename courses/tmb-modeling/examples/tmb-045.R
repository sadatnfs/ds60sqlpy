y <- c(1, 2, 4);fitted <- c(1.2, 2.1, 3.8);print(data.frame(y = y, fitted = fitted, residual = y - fitted))
set.seed(4545);group <- rep(1:3, each = 4);sigma <- .2;tau <- .8
new_u <- rnorm(3, 0, tau);unconditional <- 1 + new_u[group] + rnorm(12, 0, sigma)
conditional <- 1 + c(-.2, 0, .2)[group] + rnorm(12, 0, sigma)
print(data.frame(group = group, unconditional = unconditional, conditional = conditional))
stopifnot(length(new_u) == 3, length(unconditional) == length(group))
