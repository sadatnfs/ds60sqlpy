text1 <- "normal likelihood version 1"
text2 <- "normal likelihood version 2"
paths <- c(tempfile(), tempfile())
writeLines(text1, paths[1]); writeLines(text2, paths[2])
fingerprints <- tools::md5sum(paths)
print(fingerprints)
stopifnot(unname(fingerprints[1]) != unname(fingerprints[2]))
print(list(
  R = as.character(getRversion()), platform = R.version$platform,
  note = "Source identity demonstration only; no DLL compiled"
))
unlink(paths)
