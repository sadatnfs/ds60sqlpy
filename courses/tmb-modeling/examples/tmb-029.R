a <- seq(-2, 2, length.out = 5);rho <- .8
print(data.frame(a = a, nuisance = -rho * a, profile = .5 * (1 - rho^2) * a^2, slice = .5 * a^2))
stopifnot(all(.5 * (1 - rho^2) * a^2 <= .5 * a^2))
s <- log(2);se <- .3
print(list(log_scale_endpoints = s + c(-1, 1) * 1.96 * se, natural_scale_endpoints = exp(s + c(-1, 1) * 1.96 * se)))
natural_center <- exp(s)
transformed <- exp(s + c(-1, 1) * 1.96 * se)
delta <- natural_center + c(-1, 1) * 1.96 * natural_center * se
print(data.frame(
  method = c("transformed log-scale interval", "symmetric original-scale delta interval"),
  lower = c(transformed[1], delta[1]), upper = c(transformed[2], delta[2])
))
stopifnot(
  max(abs(transformed - delta)) > .1,
  abs((delta[1] + delta[2]) / 2 - natural_center) < 1e-12
)
