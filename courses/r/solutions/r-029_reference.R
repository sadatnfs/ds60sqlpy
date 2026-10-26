# r-029: complete reference for the declared synthetic inputs.
with_rng <- function(seed, fun) {
  if (!is.numeric(seed) || length(seed) != 1L || !is.finite(seed) ||
    seed != floor(seed) || seed < 0 || seed > .Machine$integer.max) stop("seed must be one valid integer")
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
  RNGkind(kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection")
  set.seed(as.integer(seed))
  fun()
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

set.seed(81)
before <- .Random.seed
kind <- RNGkind()
a <- with_rng(2026, function() stats::rnorm(5))
b <- with_rng(2026, function() stats::rnorm(5))
stopifnot(identical(a, b), identical(.Random.seed, before), identical(RNGkind(), kind))
assert_error(with_rng(2026, function() stop("deliberate callback failure")), "deliberate callback failure")
stopifnot(identical(.Random.seed, before), identical(RNGkind(), kind))
rm(".Random.seed", envir = .GlobalEnv)
with_rng(4, function() stats::runif(2))
stopifnot(!exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE))
assert_error(with_rng(1.5, function() 1), "valid integer")
fixture <- list(id = c("a", "b", "c"), value = c(2, 4, 6), unit = "ms")
hash_fixture <- function(x) digest::digest(as.character(jsonlite::toJSON(x, auto_unbox = TRUE, digits = 17)), algo = "sha256", serialize = FALSE)
original_hash <- hash_fixture(fixture)
modified <- fixture
modified$value[[3]] <- 7
stopifnot(original_hash == hash_fixture(fixture), original_hash != hash_fixture(modified))
stopifnot(nchar(original_hash) == 64L, fixture$value[[3]] == 6)
ledger <- list(
  seed = 2026L, draws = 5L, missing_policy = "reject", input_sha256 = original_hash,
  R = R.version.string, jsonlite = as.character(utils::packageVersion("jsonlite")),
  digest = as.character(utils::packageVersion("digest")), rng = RNGkind()
)
stopifnot(identical(sort(names(ledger)), sort(c("seed", "draws", "missing_policy", "input_sha256", "R", "jsonlite", "digest", "rng"))))
print(ledger)
cat("r-029 reference checks passed\n")
