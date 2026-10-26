# r-010: complete reference for the declared synthetic inputs.
records <- data.frame(id = c("B", "A", "C"), amount = c(20, 10, 30))
stopifnot(nrow(records) == 3L, ncol(records) == 2L)
records$amount_with_fee <- records$amount + 2
stopifnot(identical(records$amount_with_fee, c(22, 12, 32)))
stopifnot(!anyNA(records$id), !anyDuplicated(records$id))
sorted <- records[order(records$id), , drop = FALSE]
stopifnot(identical(sorted$amount, c(10, 20, 30)))
empty <- records[integer(0), , drop = FALSE]
stopifnot(nrow(empty) == 0L, identical(names(empty), names(records)))
lines <- data.frame(line_id = c("L1", "L2"), order_id = c("O1", "O1"))
stopifnot(!anyDuplicated(lines$line_id), anyDuplicated(lines$order_id) > 0L)
cat("r-010 reference checks passed\n")
