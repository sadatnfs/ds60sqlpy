# r-034: complete reference for the declared synthetic inputs.
long <- data.frame(id = c("A", "A", "B", "B"), visit = c(1, 2, 1, 2), value = c(10, 12, 20, 23))
stopifnot(!anyDuplicated(long[c("id", "visit")]))
wide <- reshape(long, idvar = "id", timevar = "visit", direction = "wide")
restored <- reshape(wide, varying = c("value.1", "value.2"), v.names = "value", timevar = "visit", times = c(1, 2), idvar = "id", direction = "long")
restored <- restored[order(restored$id, restored$visit), c("id", "visit", "value")]
row.names(restored) <- NULL
stopifnot(isTRUE(all.equal(restored, long, check.attributes = FALSE)))
duplicate <- rbind(long, long[1, ])
stopifnot(anyDuplicated(duplicate[c("id", "visit")]) > 0L)
incomplete <- long[-4, ]
incomplete_wide <- reshape(incomplete, idvar = "id", timevar = "visit", direction = "wide")
stopifnot(is.na(incomplete_wide$value.2[incomplete_wide$id == "B"]))
cat("r-034 reference checks passed\n")
