expected <- c(1, 2) * exp(log(2) + log(1.5) * c(0, 1))
print(data.frame(count = c(0, 3), expected = expected, nll = -dpois(c(0, 3), expected, log = TRUE)))
t <- c(2, 4); entry <- c(0, 1); event <- c(1, 0); scale <- 2; shape <- 1
H <- function(x) (x / scale)^shape
logh <- log(shape / scale) + (shape - 1) * log(t / scale)
nll <- sum(H(t) - H(entry) - event * logh)
print(c(censored_nll = nll, wrong_all_events = sum(H(t) - H(entry) - logh)))
stopifnot(abs(nll - (2.5 + log(2))) < 1e-12)
