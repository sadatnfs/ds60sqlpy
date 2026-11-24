# r-015: reference reasoning

Use the [complete reference](r-015_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The rejected input remains distinguishable from a valid count of zero. Its diagnostic is retained for the caller.

The calling handler records this known warning and permits the expression to finish. The retained warning remains evidence alongside the value.

## Explained practice

### Exercise 1

Distinguish a valid zero from a rejected count.

Both cannot be represented by the same unexplained numeric zero.

**Approach:** Run both inputs through `safe()` and read `ok` before looking at `value`.

**Why it holds here:** "0" gives ok TRUE with value 0, while "bad" gives ok FALSE with value NULL, so the status field carries the difference the numbers cannot.

**Tempting mistake:** A fallback that returns 0 on any error. "0" and "bad" both become 0, and the rejected row is counted as a real zero, as the broad wrapper in Example 3 shows.

**Verify:** `safe("0")$ok` returns TRUE while `safe("bad")$ok` returns FALSE.

### Exercise 2

Add a valid digit-only input "0".

The result is successful with value 0.

**Approach:** Pass "0" through the pattern `^[0-9]+$` and convert it with `as.integer()`.

**Why it holds here:** The pattern requires one or more digits and nothing else, and "0" is a single digit, so it is accepted and converts to 0L.

**Tempting mistake:** Tightening the pattern to `^[1-9][0-9]*$` to forbid leading zeros. That also rejects "0" itself, which this domain allows.

**Verify:** `safe("0")$value` returns 0L, which the reference compares with `== 0L`.

### Exercise 3

Return structured status, value and diagnostic fields.

Callers can aggregate rejection rates without parsing arbitrary console output.

**Approach:** Return `list(ok, value, message)` from both the success and the error branch.

**Why it holds here:** Success fills value and leaves message NULL; failure does the reverse. Matching names let one expression collect status for all three starter inputs.

**Tempting mistake:** Returning the bare integer on success and the message string on failure. Combining results for "12", "0" and "bad" with `c()` turns every value into text.

**Verify:** `vapply(lapply(inputs, safe), function(r) r$ok, logical(1))` returns TRUE, TRUE, FALSE.

### Exercise 4

Diagnose tryCatch(..., error=function(e)0) around a whole pipeline.

Catch only expected failures at a narrow boundary and retain diagnostics.

**Approach:** Wrap only the parse call, handle the specific message it is documented to raise, and re-raise anything else.

**Why it holds here:** Bad input is an expected outcome here, but a missing function or package is a defect. Example 3 shows that a broad handler cannot tell them apart.

**Tempting mistake:** Placing `tryCatch(..., error = function(e) 0)` around the whole pipeline. A typo, a missing dependency and the word "bad" all return 0 without a trace.

**Verify:** In Example 3 `narrow("bad")` returns NA, and the typo result shows a message containing parse_cuont.

### Exercise 5

Restore a changed option after an error.

on.exit restores the original option when the function exits.

**Approach:** Save the previous options and register `on.exit(options(previous), add = TRUE)` immediately, before the code that can fail.

**Why it holds here:** `options(digits = 3)` returns the old setting, and on.exit runs even when `stop("intentional")` ends the function.

**Tempting mistake:** Restoring with `options(previous)` as the last line of the function. The error exits first, the line never runs, and the session keeps printing three significant digits.

**Verify:** After the caught error, `getOption("digits")` returns the same value as `old`.

### Exercise 6

Explain when suppressing a warning is justified.

Handle or record a specifically understood warning; do not silence all new warnings by default.

**Approach:** Suppress or muffle only a warning whose cause is known and whose information is kept elsewhere.

**Why it holds here:** The reference silences the integer-range coercion warning because the resulting NA is immediately turned into its own error, so nothing is lost. Example 2 records its warning before muffling it.

**Tempting mistake:** Wrapping the whole batch in `suppressWarnings()`. A new warning from a later parser change disappears with no record.

**Verify:** In Example 2 `warnings_seen` returns the one recorded notice and `value` is 4.

## What the checks establish

The reference makes 3 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
