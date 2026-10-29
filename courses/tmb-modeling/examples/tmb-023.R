request <- list(schema_version = 1L, model = "normal_mean", data = list(y = c(1, 2, 4, 7)), parameters = list(mu = 0, log_sigma = 0), theta = c(2.2, .3))
expected_order <- c("mu", "log_sigma")
stopifnot(identical(names(request$parameters), expected_order), length(request$theta) == 2)
print(setNames(request$theta, expected_order))
ids <- c("r3", "r1", "r2")
returned <- ids
stopifnot(identical(ids, returned))
print(list(correct_order = identical(ids, returned), detect_accidental_sort = !identical(ids, sort(returned))))
