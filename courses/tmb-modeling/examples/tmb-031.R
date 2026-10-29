set.seed(3131);n <- 20;B <- 100;mu <- 1;sigma <- 2
scores <- replicate(B, {
  y <- rnorm(n, mu, sigma);c(mean_score = sum(mu - y) / sigma^2, scale_score = n - sum((y - mu)^2) / sigma^2, missing_normalizer = -sum((y - mu)^2) / sigma^2)
})
print(rowMeans(scores));print(apply(scores, 1, sd) / sqrt(B))
stopifnot(mean(scores[3, ]) < -10)
