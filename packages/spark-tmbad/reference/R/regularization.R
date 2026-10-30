# SPDX-License-Identifier: MIT
# Original Gaussian coordinate descent and conjugate posterior references.

reference_lasso <- function(X, y, sigma, lambda, max_iterations = 5000L, tolerance = 1e-8) {
  reference_assert(is.matrix(X) && length(y) == nrow(X), "Lasso design/response shape mismatch")
  reference_assert(length(lambda) == ncol(X) && all(lambda >= 0), "Declare one nonnegative penalty per coefficient")
  reference_assert(all(is.finite(X)) && all(is.finite(y)) && sigma > 0, "Invalid lasso data/scale")
  curvature <- colSums(X^2) / sigma^2
  reference_assert(all(curvature > 0), "Lasso design contains a zero column")
  beta <- numeric(ncol(X))
  residual <- y
  for (iteration in seq_len(max_iterations)) {
    for (j in seq_len(ncol(X))) {
      residual <- residual + X[, j] * beta[j]
      score <- sum(X[, j] * residual) / sigma^2
      beta[j] <- sign(score) * max(abs(score) - lambda[j], 0) / curvature[j]
      residual <- residual - X[, j] * beta[j]
    }
    gradient <- -as.numeric(crossprod(X, residual)) / sigma^2
    violation <- ifelse(beta == 0, pmax(abs(gradient) - lambda, 0),
      abs(gradient + lambda * sign(beta))
    )
    if (max(violation) <= tolerance) {
      return(list(
        beta = beta, iterations = iteration, kkt_inf = max(violation),
        objective = sum(residual^2) / (2 * sigma^2) + sum(lambda * abs(beta)),
        target = "exact L1 Gaussian point estimate; no posterior samples"
      ))
    }
  }
  stop("Gaussian coordinate descent failed its KKT criterion", call. = FALSE)
}

reference_gaussian_posterior <- function(X, y, sigma, center, precision, future_X) {
  reference_assert(length(center) == ncol(X) && length(precision) == ncol(X), "Prior dimensions differ")
  reference_assert(all(precision > 0), "Conjugate posterior reference requires a proper prior on every coefficient")
  posterior_precision <- crossprod(X) / sigma^2 + diag(precision, ncol(X))
  covariance <- solve(posterior_precision)
  mean <- as.numeric(covariance %*% (crossprod(X, y) / sigma^2 + precision * center))
  predictive_variance <- sigma^2 + rowSums((future_X %*% covariance) * future_X)
  list(
    mean = mean, covariance = covariance, posterior_sd = sqrt(diag(covariance)),
    prediction = list(mean = as.numeric(future_X %*% mean), sd = sqrt(predictive_variance)),
    target = "exact conjugate coefficient posterior with known observation scale",
    uncertainty = "observation and population-coefficient posterior uncertainty"
  )
}

reference_regularization_case <- function(engine, seed) {
  set.seed(seed)
  x <- rep(c(-1, 1), 40)
  z <- rep(c(-1, -1, 1, 1), 20)
  X <- cbind(intercept = 1, x = x, z = z)
  beta <- c(2, 0.8, 0.03)
  y <- as.numeric(X %*% beta + rep(c(-0.1, 0.1, 0.1, -0.1, 0.1, -0.1, -0.1, 0.1), 10))
  lambda <- c(0, 8, 8)
  fitted <- reference_lasso(X, y, 1, lambda)
  ordinary <- as.numeric(solve(crossprod(X), crossprod(X, y)))
  exact <- sign(ordinary) * pmax(abs(ordinary) - lambda / nrow(X), 0)
  reference_close(fitted$beta, exact, 1e-10)
  reference_assert(
    fitted$beta[3] == 0,
    "Lasso must produce an exact zero on the thresholded coefficient"
  )
  reference_close(fitted$beta[1], ordinary[1], 1e-10)
  objective <- reference_objective(engine, "gaussian_linear",
    list(X = X, y = y, prior_center = rep(0, 3), prior_precision = rep(0, 3)),
    list(beta = rep(0, 3), log_sigma = 0),
    map = list(log_sigma = factor(NA))
  )
  normalized <- objective$fn(fitted$beta) + sum(lambda * abs(fitted$beta))
  reference_close(normalized, fitted$objective + nrow(X) * log(2 * pi) / 2, 1e-9)
  future_X <- cbind(1, c(-2, 0, 2), c(1, -1, 1))
  posterior <- reference_gaussian_posterior(X, y, 1, c(0, 0.3, 0), c(0.1, 4, 4), future_X)
  set.seed(seed + 100000L)
  draws <- matrix(rnorm(4096 * 3), 4096, 3) %*% chol(posterior$covariance)
  draws <- sweep(draws, 2, posterior$mean, "+")
  mcse <- posterior$posterior_sd / sqrt(nrow(draws))
  reference_assert(all(abs(colMeans(draws) - posterior$mean) < 5 * mcse), "Independent posterior draw mean check failed")
  list(
    case = "regularization_posterior", lasso = fitted, exact_soft_threshold = exact,
    posterior = posterior, posterior_draw_count = nrow(draws), posterior_draw_mean = colMeans(draws),
    posterior_draw_mean_mcse = mcse, posterior_sampler = "independent exact Gaussian draws, not MCMC",
    metrics = list(primary_estimate = fitted$beta[2], truth = beta[2]),
    fixture = list(X = X, y = y, future_X = future_X, lambda = lambda, beta = beta)
  )
}
