# r-037: complete reference for the declared synthetic inputs.
exact <- sum(choose(4, 3:4)) / 2^4
stopifnot(exact == 5 / 16)
set.seed(41)
repetitions <- 20000L
estimate <- mean(rbinom(repetitions, 4, 0.5) >= 3)
stopifnot(abs(estimate - exact) < 0.02)
p <- 0.3
stopifnot(isTRUE(all.equal(sqrt(p * (1 - p) / 400), sqrt(p * (1 - p) / 100) / 2)))
stopifnot(all(rbinom(10, 4, 0) == 0), all(rbinom(10, 4, 1) == 4))
set.seed(41); first <- rbinom(5, 4, 0.5)
set.seed(41); second <- rbinom(5, 4, 0.5)
stopifnot(identical(first, second))
cat("r-037 reference checks passed\n")
