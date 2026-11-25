# r-026: reference reasoning

Run the [complete reference](r-026_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The reference demonstrates search-path masking and then deliberately resolves the public package export. It checks the exact source-tree inventory and the behavior of the authored function in a separate environment.

The tree is removed after inspection, and no installation or network call occurs. A local source environment is not a package namespace. Empty-input and invalid-value tests belong to the function's contract and would be retained in a real package test suite during the optional multi-file continuation.

## Explained practice

### Exercise 1

Predict the difference between a global median and stats::median.

The masked function can return -999 while stats::median(c(1,4,9)) remains 4.

**Expected evidence:** Two deliberately different results.

**Approach:** Define `median <- function(x, ...) -999` in the global environment, then call both `median(c(1, 4, 9))` and `stats::median(c(1, 4, 9))`.

**Why it holds here:** An unqualified name is looked up from the global environment outward, so the mask is found first. `stats::` goes straight to the stats exports, which return the middle value, 4.

**Tempting mistake:** Assuming the package function wins because stats is attached. A script run in a session where someone defined median gets -999 and no warning.

**Verify:** `median(c(1, 4, 9))` returns -999, while `stats::median(c(1, 4, 9))` returns 4.

### Exercise 2

Retrieve the public median function without attaching stats names.

getExportedValue("stats","median")(c(1,4,9)) returns 4.

**Expected evidence:** Public result 4.

**Approach:** Call `public <- getExportedValue("stats", "median")` and then `public(c(1, 4, 9))`.

**Why it holds here:** The lookup goes through the stats export list, not the search path, so the global mask is never consulted and the median of 1, 4 and 9 is 4.

**Tempting mistake:** Using `get("median")`. It searches from the calling environment and returns the -999 mask; calling library(stats) does not help, since the global environment is still searched first.

**Verify:** `public(c(1, 4, 9))` returns 4, and `"median" %in% getNamespaceExports("stats")` returns TRUE.

### Exercise 3

Create and inspect DESCRIPTION, NAMESPACE and one R source file in a temporary tree.

The source tree contains package metadata, export(observed_mean), and R/summary.R. Parse and evaluate only the known authored definitions.

**Expected evidence:** Exact three-file inventory and checked local behavior.

**Approach:** Create the tree under `tempfile()` with `on.exit(unlink(root, recursive = TRUE))`, write the three files, read them back with read.dcf, readLines and parse, then `sys.source()` the R file into an environment whose parent is baseenv().

**Why it holds here:** parse confirms two top-level definitions before anything runs, and the fresh environment holds only those definitions, so the mean of 2 and 4, which is 3, comes from the authored code alone.

**Tempting mistake:** Running `source()` into the global environment. The definitions would overwrite the session's observed_mean, and a stray global helper could satisfy a missing reference and hide the bug.

**Verify:** `result$files` returns "DESCRIPTION", "NAMESPACE", "R/summary.R", and `result$mean` returns 3.

### Exercise 4

Diagnose a helper being considered private merely because its name starts with a dot.

The NAMESPACE export list controls ordinary public access. A dot name alone neither registers nor hides an export.

**Expected evidence:** Separate naming convention and public interface.

**Approach:** Read NAMESPACE to decide what is public: it lists only `export(observed_mean)`, so .validate is internal because it is not exported.

**Why it holds here:** A leading dot only hides a name from a default ls() listing; it has no effect on exports. A NAMESPACE using `exportPattern(".")` would export .validate despite the dot.

**Tempting mistake:** Treating the dot as the access rule. Under a broad export pattern, the helper becomes part of the public interface while its author still thinks it is private.

**Verify:** `readLines(file.path(root, "NAMESPACE"))` returns only "export(observed_mean)", and `ls(environment)` omits .validate while `ls(environment, all.names = TRUE)` shows it.

### Exercise 5

Test empty and nonfinite values in the local observed_mean function.

Empty input returnsNA_real_; nonfinite input raises the finite-values error.

**Expected evidence:** Two distinct boundary cases.

**Approach:** Test `observed_mean(numeric(0))` and `observed_mean(c(1, Inf))` as two separate cases with different expected outcomes.

**Why it holds here:** An empty vector passes the finite check, because any() of nothing is FALSE, and the length guard returns NA_real_. Inf fails is.finite, so the function stops before averaging.

**Tempting mistake:** Dropping the length guard and relying on mean. The empty case would return NaN, which differs from the documented NA_real_, and filtering out Inf would silently average 1 alone.

**Verify:** `is.na(observed_mean(numeric(0)))` returns TRUE, and `observed_mean(c(1, Inf))` stops with "finite numeric values required".

### Exercise 6

Describe what remains before claiming that the temporary tree is an installed, checked package.

Use a separate multi-file project to document, build, install and run R CMD check. Preserve tests and dependency declarations; do not run network installation from this pad.

**Expected evidence:** Explicit optional contributor continuation.

**Approach:** List the remaining steps for a separate project: document, build, install into a library, run R CMD check with tests, and confirm that Imports: stats resolves when the namespace loads.

**Why it holds here:** parse and sys.source only evaluated one file. No namespace was created, so the export list was never applied and the DESCRIPTION fields were never checked by R.

**Tempting mistake:** Claiming a working package because observed_mean returned 3. That proves one function evaluates, not that the package installs or checks; network installation also does not belong in this pad.

**Verify:** `exists(".validate", envir = environment)` returns TRUE in the sys.source environment, which shows that the export list was not enforced.

## What the checks establish

The assertions confirm that DESCRIPTION names measurekit, that NAMESPACE contains exactly `export(observed_mean)`, that the source parses into two expressions and computes a mean of 3, that a masking global median returns -999 while `stats::median()` returns 4, that an empty input returns NA, and that `dnorm(0)` matches its closed form. They do not install or check the package; parsing a tree is not `R CMD check`.

The reference makes 10 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
