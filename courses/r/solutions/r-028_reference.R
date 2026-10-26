# r-028: complete reference for the declared synthetic inputs.
with_two_workers <- function(fun) {
  cluster <- parallel::makePSOCKcluster(2L,
    master = "127.0.0.1",
    rscript_args = "--vanilla", setup_timeout = 10, timeout = 30
  )
  on.exit(parallel::stopCluster(cluster), add = TRUE)
  fun(cluster)
}
make_tasks <- function(n, seed) {
  old_kind <- RNGkind()
  had_seed <- exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  if (had_seed) old_seed <- get(".Random.seed", envir = .GlobalEnv)
  on.exit(
    {
      do.call(RNGkind, as.list(old_kind))
      if (had_seed) assign(".Random.seed", old_seed, envir = .GlobalEnv)
      else if (exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)) rm(".Random.seed", envir = .GlobalEnv)
    },
    add = TRUE
  )
  RNGkind("L'Ecuyer-CMRG")
  set.seed(seed)
  stream <- .Random.seed
  tasks <- vector("list", n)
  for (i in seq_len(n)) {
    tasks[[i]] <- list(id = i, seed = stream)
    stream <- parallel::nextRNGStream(stream)
  }
  tasks
}
draw_task <- function(task) {
  assign(".Random.seed", task$seed, envir = .GlobalEnv)
  list(id = task$id, values = stats::rnorm(4))
}
order_results <- function(results) {
  results[order(vapply(results, function(x) x$id, integer(1)))]
}
assert_error <- function(expr, pattern) {
  message <- tryCatch(
    {
      force(expr); NULL
    },
    error = conditionMessage
  )
  stopifnot(is.character(message), length(message) == 1L, grepl(pattern, message))
}

tasks <- list(1:3, 4:6, c(2, 2))
summary_task <- function(x) list(count = length(x), sum_squares = sum(x^2))
serial <- lapply(tasks, summary_task)
parallel_result <- with_two_workers(function(cluster) parallel::parLapply(cluster, tasks, summary_task))
stopifnot(identical(serial, parallel_result))
stopifnot(identical(vapply(parallel_result, function(x) x$sum_squares, numeric(1)), c(14, 77, 8)))
stopifnot(parallel_result[[1]]$count == 3L)
streams <- make_tasks(4L, 2026)
random_results <- with_two_workers(function(cluster) {
  a <- parallel::parLapply(cluster, streams, draw_task)
  b <- parallel::parLapplyLB(cluster, rev(streams), draw_task)
  list(a = order_results(a), b = order_results(b))
})
stopifnot(identical(random_results$a, random_results$b))
stopifnot(!identical(random_results$a[[1]]$values, random_results$a[[2]]$values))
assert_error(with_two_workers(function(cluster) {
  parallel::parLapply(cluster, list(1L, 2L), function(x) stop("deliberate task failure"))
}), "deliberate task failure")
cat("r-028 reference checks passed\n")
