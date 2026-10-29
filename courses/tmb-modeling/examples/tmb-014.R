H <- matrix(c(3, .5, .5, 2), 2, 2); b <- c(1, -2)
newton <- function(u) u - solve(H, drop(H %*% u) - b)
print(rbind(from_zero = newton(c(0, 0)), from_far = newton(c(10, -7)), exact = solve(H, b)))
stopifnot(max(abs(newton(c(10, -7)) - solve(H, b))) < 1e-12)
fn <- function(u) (u^2 - 1)^2 + .1 * u
gr <- function(u) 4 * u * (u^2 - 1) + .1
for (start in c(-2, 2)) {
  short <- nlminb(start, fn, gr, control = list(iter.max = 1))
  full <- nlminb(start, fn, gr)
  print(c(start = start, limited_gradient = gr(short$par), full_value = full$objective, full_gradient = gr(full$par)))
}
