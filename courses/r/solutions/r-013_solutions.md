# r-013: reference reasoning

Use the [complete reference](r-013_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

Each returned function retains its own configured factor. No global factor is needed at call time.

The unforced promise looks up rate on first use after the change. The forced closure retained the value two during construction.

## Explained practice

### Exercise 1

Predict make_multiplier(4)(2).

The result is eight.

**Approach:** Read the call in two stages: `make_multiplier(4)` returns a function with factor 4, and `(2)` calls that function.

**Why it holds here:** The returned function computes x times its captured factor, so 2 times 4 is 8.

**Tempting mistake:** Rewriting it as `make_multiplier(4, 2)`. The factory takes one argument, so R stops with an unused argument error instead of returning 8.

**Verify:** `make_multiplier(4)(2)` returns 8.

### Exercise 2

Create two factories with different factors.

Their outputs remain independently configured.

**Approach:** Build `a <- make_multiplier(2)` and `b <- make_multiplier(3)` as two separate calls.

**Why it holds here:** Each call creates a fresh environment, so a holds factor 2 and b holds factor 3, and neither reads a global setting.

**Tempting mistake:** Using one function that reads a global `factor` variable. Setting it to 3 for b also changes a, so a(5) becomes 15.

**Verify:** `a(5)` returns 10 and `b(5)` returns 15; `environment(a)$factor` shows 2.

### Exercise 3

Capture a threshold at construction time.

Later caller rebinding does not change the captured threshold.

**Approach:** Call `force(threshold)` in make_threshold before returning the predicate.

**Why it holds here:** The caller sets t to 10, builds the predicate and then sets t to 100. Forcing fixes 10 at construction, so 20 counts as meeting the threshold.

**Tempting mistake:** Leaving out force. The promise is first evaluated when predicate(20) runs, when t is already 100, so the result is FALSE.

**Verify:** `predicate(20)` returns TRUE, which the reference checks.

### Exercise 4

Diagnose a lazy factory changing after caller configuration changes.

Force the argument when fixed configuration is intended.

**Approach:** Trace lazy_factory: v is 2 at construction, becomes 5, and `lazy(3)` is the first call that reads factor. Fix it by forcing the argument.

**Why it holds here:** The promise reads v only on first use, so it sees 5 and returns 15 rather than the intended 6.

**Tempting mistake:** Calling `lazy(3)` once before changing v. That does evaluate the promise and fix it at 2, but the result now depends on call order, which any refactor can break.

**Verify:** The reference `lazy(3)` returns 15; the forced `fixed(3)` from Example 2 returns 6.

### Exercise 5

Reject an invalid scalar configuration before returning a closure.

No partially configured function is returned for missing or nonfinite input.

**Approach:** Force the factor, then check numeric, length one and finite before building the closure.

**Why it holds here:** `NA_real_` is numeric and has length 1, so only `is.finite()` rejects it. Checking at construction reports the problem where the configuration was set.

**Tempting mistake:** Deferring the check to the inner function or skipping it. `make_multiplier(NA_real_)(2)` would then return NA, and the error, if any, appears far from the bad setting.

**Verify:** In the reference `bad` returns TRUE, and `is.finite(NA_real_)` returns FALSE.

### Exercise 6

Explain why hidden global mutation complicates a model pipeline.

Prefer explicit inputs or documented captured state with reset and reproducibility rules.

**Approach:** Pass configuration as arguments or capture it with force, and avoid `<<-` updates that change behavior between calls.

**Why it holds here:** This lesson already shows a hidden dependency: `lazy(3)` returned 15 or 6 depending on code that ran between definition and use.

**Tempting mistake:** A closure that increments a counter with `<<-` to label runs. Rerunning a pipeline in the same session gives different labels than a fresh session, so results cannot be reproduced.

**Verify:** Calling `fixed(3)` before and after `rate <- 5` returns 6 both times.

## What the checks establish

The reference makes 6 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
