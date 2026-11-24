# julia-009: explained reference

The executable reference is `julia-009_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

`finite_mean` enforces its contract in order: reject an empty vector with `ArgumentError`, reject any nonfinite value with `DomainError`, then return `mean`. `outcome` converts only those two promised failures into a `:rejected` named tuple and rethrows anything else, so a programming defect still stops the run.

## 1. Keep valid zero

The input satisfies the contract and its arithmetic mean happens to be zero.

**Expected observation:** The result is the valid number 0.

**Why it holds here:** `[-1, 1]` is nonempty and finite, so both guards pass and `mean` returns 0.0, a legitimate result rather than a rejection signal.

**Plausible wrong approach:** Using zero as a sentinel for invalid input would make this valid mean indistinguishable from a rejected batch in any downstream table.

**How to verify:** Worked example A asserts `finite_mean([-1, 1]) == 0`; pass the same vector through `outcome` and expect status `:ok`.

## 2. Reject empty input

A fabricated zero would hide the absence of evidence.

**Expected observation:** ArgumentError identifies the missing observation requirement.

**Why it holds here:** `isempty(values)` is checked first, so `Float64[]` raises `ArgumentError` before `mean` could divide by a count of zero.

**Plausible wrong approach:** Returning 0.0 for empty input invents an observation, and averaging that into a report weights a group that has no data.

**How to verify:** Assert `@test_throws ArgumentError finite_mean(Float64[])`, then check that `outcome(Float64[]).reason` mentions observation.

## 3. Reject nonfinite values

Nonfinite values need a declared policy rather than silent propagation into a report.

**Expected observation:** DomainError is raised.

**Why it holds here:** `all(isfinite, values)` fails for NaN or Inf, so the function throws `DomainError` and names the offending vector.

**Plausible wrong approach:** Letting NaN flow into `mean` yields NaN, which then compares false with everything and quietly drops out of later filters.

**How to verify:** The reference asserts `@test_throws DomainError finite_mean([NaN])` and `outcome([Inf]).status == :rejected`.

## 4. Preserve an unexpected error

A broad catch can hide a programming defect behind a normal-looking outcome.

**Expected observation:** The unexpected method error is rethrown.

**Why it holds here:** A vector of strings passes the empty check, then `isfinite` has no string method, so `MethodError` escapes and `outcome` rethrows it.

**Plausible wrong approach:** A bare `catch` returning `:rejected` for every error would label a type mistake in the caller as bad data and hide the bug.

**How to verify:** The reference checks `@test_throws MethodError finite_mean(["not numeric"])`; example B also shows `outcome(nothing)` rethrowing.

## 5. Test independently

Different reasoning paths reduce the chance that code and test share one unnoticed error.

**Expected observation:** The assertion has an independent basis.

**Why it holds here:** A hand calculation such as (1 + 2 + 3) / 3 = 2 and a limiting case like a single value `[7]` come from reasoning separate from the code.

**Plausible wrong approach:** Writing the expected value as `sum(v) / length(v)` copies the implementation, so the test passes even if both share a mistake.

**How to verify:** Keep `finite_mean([7]) == 7` from the reference and add one hand-derived mean with its arithmetic written in a comment.

## 6. Report rejected rows

Selection through validation can change the target population and should remain visible.

**Expected observation:** Retain counts and reasons for rejected rows.

**Why it holds here:** Mapping `outcome` over rows yields `:ok` and `:rejected` tuples, so valid values and rejection reasons can be counted separately.

**Plausible wrong approach:** Averaging only the successful values and printing that mean alone hides how many rows were excluded and why.

**How to verify:** Report the counts of `:ok` and `:rejected` beside the mean and confirm they add up to the number of input rows.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-009: all reference checks passed`:

The checks follow the two error styles in the lesson. `finite_mean` returns 7 for `[7]` and throws `DomainError` for NaN, while `outcome` packages the same decision as a status, so `[Inf]` yields `:rejected` without an exception. A string input fails with `MethodError` before any arithmetic, showing that dispatch rejects it first. The last line accepts `0.1 + 0.2` rounding because it only asks for a finite result.

```julia
function exercise_checks()
    @test finite_mean([7]) == 7
    @test_throws DomainError finite_mean([NaN])
    @test outcome([0]).value == 0
    @test outcome([Inf]).status == :rejected
    @test_throws MethodError finite_mean(["not numeric"])
    @test isfinite(finite_mean([0.1, 0.2]))
end
```
