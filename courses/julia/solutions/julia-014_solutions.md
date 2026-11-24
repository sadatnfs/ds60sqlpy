# julia-014: explained reference

The executable reference is `julia-014_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

`observed_summary` drops `missing` with `skipmissing`, rejects any nonfinite observed value with `DomainError`, and returns a named tuple of `total`, `observed` and `estimate`. When nothing is observed the estimate is `missing`. Treat `missing` as unknown data and `nothing` as an absent result, using `coalesce` and `something` for each.

## 1. Retain the denominator

The result describes the observed measurements, not an assumed completed dataset.

**Expected observation:** Total 3, observed 2 and mean 2.

**Why it holds here:** `[1, missing, 3]` has 3 entries and 2 observed values, so the mean of observed values is (1 + 3) / 2 = 2.0.

**Plausible wrong approach:** Calling `mean` directly on the vector propagates `missing`, and reporting only a cleaned mean drops the fact that one row lacked data.

**How to verify:** Example A asserts `summary == (total = 3, observed = 2, estimate = 2.0)`.

## 2. Replace explicitly

The replacement policy changes the quantity being summarized.

**Expected observation:** The mean becomes 4/3.

**Why it holds here:** `coalesce.(values, 0.0)` replaces the gap with 0, so the mean becomes (1 + 0 + 3) / 3 = 4/3.

**Plausible wrong approach:** Presenting 4/3 as if it were the observed mean changes both numerator and denominator without stating the imputation.

**How to verify:** Example A asserts `mean(replaced) ≈ 4/3`; print both means beside their policies.

## 3. Reject numerical failure

Unknown data and undefined floating arithmetic need distinct handling.

**Expected observation:** The finite-value guard rejects it.

**Why it holds here:** `skipmissing` removes only `missing`, so NaN remains and the `isfinite` check throws `DomainError`.

**Plausible wrong approach:** Assuming `skipmissing` also discards NaN lets a numerical failure pass through as if it were an unknown measurement.

**How to verify:** Example B asserts `@test_throws DomainError observed_summary([1.0, NaN, missing])`.

## 4. Handle all-missing data

The output preserves unavailable information while retaining the eligible count.

**Expected observation:** The observed count is 0 and estimate is missing.

**Why it holds here:** Two missing values leave `observed` empty, so the function reports observed count 0 and estimate `missing` while keeping total 2.

**Plausible wrong approach:** Returning 0 as the estimate fabricates a mean of no data and could be averaged into later group results.

**How to verify:** Example B asserts `empty_observed.observed == 0` and `ismissing(empty_observed.estimate)`.

## 5. Distinguish absence

An absent return and a missing measurement should not be conflated accidentally.

**Expected observation:** The former returns 7; the latter retains `nothing`.

**Why it holds here:** `something` skips `nothing` and returns 7, while `coalesce` skips only `missing` and returns its first argument `nothing` unchanged.

**Plausible wrong approach:** Using `coalesce` to fill an absent lookup result keeps `nothing`, which later fails in arithmetic with a confusing error.

**How to verify:** Example B asserts `something(nothing, 7) == 7` and `coalesce(nothing, 7) === nothing`.

## 6. Assess a real policy

The missingness mechanism and decision target determine which policy is defensible.

**Expected observation:** State assumptions, affected population and uncertainty.

**Why it holds here:** Deletion targets observed units only, while imputation needs a model; neither choice is justified by the code alone.

**Plausible wrong approach:** Choosing whichever policy makes results look stable treats a scientific assumption about why data is missing as a formatting decision.

**How to verify:** Write the assumed missingness mechanism and affected rows, then report both totals from `observed_summary`.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-014: all reference checks passed`:

`coalesce` replaces missing with 4, but `something` does not treat missing as absent, so the result stays missing. `missing + 1` propagates as expected. `observed_summary([2, 4])` reports an estimate of 3 with every value observed, an empty `Float64[]` still returns a total of 0, and `Inf` raises `DomainError`, because missing and invalid values are different problems that need different handling. Notice that each line asks a separate question. Replacement, propagation, summary counts and invalid input are not tested by one example, so a change to the missing policy cannot hide behind a passing NaN check, and a change to the NaN policy cannot hide behind a passing missing check. A summary that silently dropped `Inf` would report an estimate from fewer values than its total suggests.

```julia
function exercise_checks()
    @test coalesce(missing, 4) == 4
    @test ismissing(missing + 1)
    @test ismissing(something(missing, 4))
    @test observed_summary([2, 4]).estimate == 3
    @test observed_summary(Float64[]).total == 0
    @test_throws DomainError observed_summary([Inf])
end
```
