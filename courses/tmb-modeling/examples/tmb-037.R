paths <- c(tempfile(), tempfile());writeLines("model revision A", paths[1]);writeLines("model revision B", paths[2])
print(tools::md5sum(paths));stopifnot(unname(tools::md5sum(paths)[1]) != unname(tools::md5sum(paths)[2]));unlink(paths)
receipt <- list(R = as.character(getRversion()), architecture = R.version$platform, source_immutable = TRUE, scratch_separate = TRUE)
print(receipt)
