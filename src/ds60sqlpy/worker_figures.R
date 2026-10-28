# Capture script graphics in the bounded worker directory without opening a browser.
.ds60_run <- function() {
  run_directory <- getwd()
  saved <- list()
  capture_plotly <- function(x, ...) {
    if (length(saved) >= 2L) {
      message("Figure limit reached: the first two Plotly figures are retained.")
      return(invisible(x))
    }
    document <- jsonlite::fromJSON(
      plotly::plotly_json(x, jsonedit = FALSE, pretty = FALSE),
      simplifyVector = FALSE
    )
    figure <- list(data = document$data, layout = document$layout)
    if (length(document$frames)) figure$frames <- document$frames
    one <- jsonlite::toJSON(figure, auto_unbox = TRUE, null = "null", na = "null", digits = NA)
    if (nchar(one, type = "bytes") > 180000L) {
      message("Figure omitted: one chart exceeds the classroom output limit.")
      return(invisible(x))
    }
    candidate <- c(saved, list(list(kind = "plotly", figure = figure)))
    encoded <- jsonlite::toJSON(candidate, auto_unbox = TRUE, null = "null", na = "null", digits = NA)
    if (nchar(encoded, type = "bytes") > 384000L) {
      message("Figure omitted: saved charts exceed the classroom output limit.")
      return(invisible(x))
    }
    retained <- tryCatch(
      {
        temporary <- tempfile(".ds60-output-", tmpdir = run_directory)
        on.exit(unlink(temporary), add = TRUE)
        writeLines(encoded, temporary, useBytes = TRUE)
        if (!file.rename(temporary, file.path(run_directory, "ds60-figures.json"))) {
          stop("Could not atomically retain the chart")
        }
        TRUE
      },
      error = function(error) {
        message("Figure capture could not be saved: ", conditionMessage(error))
        FALSE
      }
    )
    if (retained) saved <<- candidate
    invisible(x)
  }
  register_plotly <- function(...) {
    registerS3method("print", "plotly", capture_plotly, envir = asNamespace("base"))
  }
  if ("plotly" %in% loadedNamespaces()) {
    register_plotly()
  } else {
    setHook(packageEvent("plotly", "onLoad"), register_plotly, action = "append")
  }
  grDevices::png(file.path(run_directory, ".ds60-r-%02d.png"), width = 900L, height = 600L, res = 100L, type = "cairo")
  on.exit(
    {
      while (grDevices::dev.cur() > 1L) grDevices::dev.off()
      # Python validates the PNG signatures, sizes and total output after R exits.
    },
    add = TRUE
  )
  source("main.R", local = globalenv(), echo = FALSE, keep.source = TRUE)
}
.ds60_run()
