# r-016: complete reference for the declared synthetic inputs.
stopifnot(identical(grepl(".", c("a.b", "axb"), fixed = TRUE), c(TRUE, FALSE)))
stopifnot(grepl("^[0-9]{5}$", "00123"), !grepl("^[0-9]{5}$", "123"))
fields <- strsplit("A|12", "|", fixed = TRUE)[[1]]
stopifnot(identical(fields, c("A", "12")))
stopifnot(!grepl("^[0-9]+$", "ID12bad"))
stopifnot(identical(strsplit("A|", "|", fixed = TRUE)[[1]], "A"))
text <- enc2utf8("café")
stopifnot(nchar(text, type = "chars") == 4L, nchar(text, type = "bytes") == 5L)
cat("r-016 reference checks passed\n")
