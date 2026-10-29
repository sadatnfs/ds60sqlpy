frame <- data.frame(row_id = c("r-003", "r-001", "r-002"), x = c(2, 0, 1), y = c(4.1, .2, 1.9), stringsAsFactors = FALSE)
stopifnot(!anyDuplicated(frame$row_id), all(is.finite(frame$x)), all(is.finite(frame$y)))
print(frame)
bad <- frame; bad$y[2] <- NA_real_
print(c(valid_complete = all(is.finite(frame$y)), reject_missing = !all(is.finite(bad$y))))
category <- factor(c("medium", "low"), levels = c("low", "medium", "high"))
print(list(category_levels = levels(category), utc = as.POSIXct("2026-01-01 12:00:00", tz = "UTC")))
