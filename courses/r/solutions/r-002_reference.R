# r-002: complete reference for the declared synthetic inputs.
stopifnot(typeof(c(1L, 2.5)) == "double")
identifier <- "0017"
stopifnot(nchar(identifier) == 4, is.character(identifier))
stopifnot(19 %/% 5 == 3, 19 %% 5 == 4)
stopifnot(!identical(2L, 2), 2L == 2)
stopifnot(isTRUE(all.equal(0.1 + 0.2, 0.3, tolerance = 1e-12)))
stopifnot(!isTRUE(all.equal(0.31, 0.3, tolerance = 1e-12)))
cat("r-002 reference checks passed\n")
