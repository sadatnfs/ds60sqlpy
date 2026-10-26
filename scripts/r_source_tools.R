# Parse, format or lint stdin without evaluating learner code or loading profiles.
main <- function() {
  arguments <- commandArgs(trailingOnly = TRUE)
  if (length(arguments) != 1L || !arguments[[1L]] %in% c("parse", "format", "lint")) {
    stop("Choose exactly one R source operation: parse, format or lint")
  }
  connection <- file("stdin", open = "rb")
  on.exit(close(connection), add = TRUE)
  bytes <- readBin(connection, what = "raw", n = 5000001L)
  if (length(bytes) > 5000000L || any(bytes == as.raw(0))) {
    stop("R source must be at most five megabytes and contain no NUL bytes")
  }
  source <- rawToChar(bytes)
  if (!validUTF8(source)) {
    stop("R source must be valid UTF-8")
  }
  Encoding(source) <- "UTF-8"
  before <- parse(text = source, keep.source = FALSE)
  operation <- arguments[[1L]]
  if (operation == "parse") {
    return(invisible(NULL))
  }
  if (operation == "format") {
    if (!requireNamespace("styler", quietly = TRUE)) {
      stop("The prepared R formatting image must supply styler")
    }
    options(R.cache.rootPath = tempdir(), styler.quiet = TRUE)
    styler::cache_deactivate(verbose = FALSE)
    if (!nzchar(source)) {
      return(invisible(NULL))
    }
    lines <- strsplit(source, "\n", fixed = TRUE)[[1L]]
    formatted <- as.character(styler::style_text(
      lines,
      scope = "line_breaks",
      include_roxygen_examples = FALSE
    ))
    text <- paste(formatted, collapse = "\n")
    after <- parse(text = text, keep.source = FALSE)
    if (!identical(before, after)) {
      stop("R formatter changed the parsed expressions; source was not written")
    }
    cat(text, "\n", sep = "")
    return(invisible(NULL))
  }
  if (!requireNamespace("lintr", quietly = TRUE)) {
    stop("The prepared R formatting image must supply lintr")
  }
  # Fixed lexical rules avoid evaluating .lintr settings or learner expressions.
  # Semantic examples, unfinished exercises and nonstandard evaluation retain
  # their own runtime and content checks instead of object-usage assumptions.
  rules <- list(
    commas_linter = lintr::commas_linter(),
    infix_spaces_linter = lintr::infix_spaces_linter(),
    spaces_inside_linter = lintr::spaces_inside_linter(),
    trailing_whitespace_linter = lintr::trailing_whitespace_linter()
  )
  lints <- lintr::lint(
    text = source,
    linters = rules,
    cache = FALSE,
    parse_settings = FALSE
  )
  if (length(lints)) {
    print(lints)
    stop("R source has static lint findings")
  }
  invisible(NULL)
}

tryCatch(
  main(),
  error = function(error) {
    cat(conditionMessage(error), "\n", file = stderr(), sep = "")
    quit(status = 1L, save = "no")
  }
)
