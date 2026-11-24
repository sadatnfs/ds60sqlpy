# r-029: reference reasoning

Use the [complete reference](r-029_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference tests ordinary completion, a deliberately failed callback and an initially absent seed. Each checks a separate restoration obligation. The numeric output is compared within the same explicit generator configuration rather than asserted as an eternal cross-version sequence.

The digest test changes one known value and retains the original object. Metadata is an explicit allowlist of analysis-relevant fields, so the example does not expose unrelated session state. A reproducible ledger supports review but cannot establish unbiasedness or sound experimental design.

## Explained practice

### Exercise 1

Predict whether two with_rng calls with seed 2026 and identical callbacks match.

They match in the prepared runtime, while the caller stream is restored after each call.

**Expected evidence:** Equal output vectors and equal caller state.

**Approach:** Call `with_rng(2026, function() stats::rnorm(5))` twice and compare the vectors, then compare `.Random.seed` and `RNGkind()` with the values saved after `set.seed(81)`.

**Why it holds here:** The wrapper sets Mersenne-Twister, Inversion and Rejection before `set.seed(2026)`, so both calls start from the same state and draw the same five values. on.exit then puts back the stream that seed 81 produced.

**Tempting mistake:** Calling `set.seed(2026)` at top level instead. The two vectors still match, but the caller's seed 81 stream is replaced, so every later draw in the script shifts.

**Verify:** `identical(a, b)` and `identical(.Random.seed, before)` both return TRUE, and `RNGkind()` returns the saved kinds.

### Exercise 2

Test cleanup after a callback raises an error.

The error propagates and the prior generator kind and seed remain unchanged.

**Expected evidence:** Matched error plus restored state.

**Approach:** Pass a callback that calls `stop("deliberate callback failure")`, capture the message, and compare the generator state with `before` and `kind` afterwards.

**Why it holds here:** Restoration is registered with on.exit before fun runs, so it executes while the error unwinds. The caller sees the original message and gets the seed 81 state back.

**Tempting mistake:** Restoring the state in lines placed after `fun()` in the body. The error skips them, leaving the session on Mersenne-Twister seeded with 2026, which changes every later draw without any warning.

**Verify:** assert_error returns NULL after matching "deliberate callback failure", and `identical(.Random.seed, before)` returns TRUE.

### Exercise 3

Test the case where .Random.seed did not exist before the call.

After completion, remove the temporary seed rather than creating ambient RNG state for the caller.

**Expected evidence:** No .Random.seed remains.

**Approach:** Remove `.Random.seed`, run `with_rng(4, function() stats::runif(2))`, and check that no seed exists afterwards.

**Why it holds here:** had_seed is FALSE, so the cleanup branch removes the seed that `set.seed(4)` created. The caller stays unseeded, exactly as before the call.

**Tempting mistake:** Saving with `old_seed <- .Random.seed` without checking existence. That line fails with object not found before fun runs, and skipping the removal instead would leave seed 4 behind as hidden state.

**Verify:** `exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)` returns FALSE after the call.

### Exercise 4

Change one fixture value and compare its content digest.

The altered fixture has a different SHA256 digest; that identifies a content change without judging its validity.

**Expected evidence:** Different digest and bounded meaning.

**Approach:** Change `value[[3]]` from 6 to 7 in a copy, hash both lists with the same toJSON settings, and compare the SHA256 strings.

**Why it holds here:** hash_fixture converts the list to JSON with `digits = 17` and hashes the text with `serialize = FALSE`, so the digest depends only on content. One changed number gives a different 64 character digest.

**Tempting mistake:** Using toJSON's default `digits = 4`. It rounds to four decimals, so a change from 6 to 6.00001 would serialize as 6 and hash identically, hiding a real edit.

**Verify:** `original_hash != hash_fixture(modified)` returns TRUE, and `nchar(original_hash)` returns 64.

### Exercise 5

Record only the configuration and software metadata needed to reproduce this calculation.

Keep seed, draws, missingness rule, input digest, R version, relevant package versions and RNG kinds.

**Expected evidence:** A bounded ledger without unrelated state.

**Approach:** Record seed, draws, missing_policy, input_sha256, R version, jsonlite and digest versions, and the RNG kinds, and nothing else.

**Why it holds here:** Each entry changes the numbers: seed and draws fix the values, the RNG kinds decide how a seed becomes values, the digest pins the input, and the two package versions affect the JSON text and its hash.

**Tempting mistake:** Saving all of `sessionInfo()` and `Sys.getenv()`. Paths, user names and possible tokens leak into the record, and the few relevant entries are buried among unrelated ones.

**Verify:** `identical(sort(names(ledger)), sort(c(...)))` returns TRUE for exactly these eight names.

### Exercise 6

Explain why a repeated result is not evidence that the estimator is unbiased.

The same selection bias or model misspecification can repeat exactly. Evaluate design and assumptions separately.

**Expected evidence:** No validity claim from repeatability.

**Approach:** Treat identical reruns as evidence that the computation is repeatable, and check the sampling design and model assumptions separately.

**Why it holds here:** a and b match because the seed fixes the draws. If a fixture were collected only from slow servers, its mean would repeat exactly in every run and still overstate typical latency.

**Tempting mistake:** Citing `identical(a, b)` as validation of the estimate. Repetition removes variation between runs, not systematic error in how the data were chosen.

**Verify:** A run with seed 2027 shows different draws, which measures sampling variation; no run shows how the sample was collected.

## What the checks establish

The reference makes 7 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
