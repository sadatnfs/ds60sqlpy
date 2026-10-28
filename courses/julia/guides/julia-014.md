# julia-014: Missing values, absence and nonfinite measurements

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-004`, `julia-012`.

Keep missingness and numerical failure distinct and report the denominator used by each aggregation policy.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Three states with different meanings

`missing` represents unknown or unavailable data. `nothing` commonly represents the absence of a returned value. NaN is a floating-point value that often indicates an undefined numerical result. These states are not interchangeable, and a function should not collapse them into zero without a declared policy.

Operations involving `missing` can propagate uncertainty. The eager Boolean operators `&` and `|` support three-valued behavior when one part is unknown. An `if` condition and the controlling operand of `&&` or `||` still require a Boolean. `ismissing` produces a definite test. `skipmissing` iterates over observed values, while `coalesce` substitutes a stated replacement for missing data.

A vector that can hold missing values may have an element type such as `Union{Missing,Float64}`. This is a representation contract. It does not say whether missingness is random, whether deletion is valid or how uncertainty should be handled statistically.

## Worked case A: deletion and replacement change a mean

The observed values are 1 and 3, with one missing measurement. Averaging only observed values gives 2. Replacing missing with zero gives four thirds. The two results answer different questions. The program reports the observed count and total count so a reader can reconstruct the denominator.

```julia
using Test
using Statistics

function observed_summary(values)
    observed = collect(skipmissing(values))
    all(isfinite, observed) || throw(DomainError(observed, "Observed values must be finite"))
    estimate = isempty(observed) ? missing : mean(observed)
    return (total = length(values), observed = length(observed), estimate = estimate)
end

function worked_a()
    values = Union{Missing,Float64}[1, missing, 3]
    summary = observed_summary(values)
    @test summary == (total = 3, observed = 2, estimate = 2.0)
    replaced = coalesce.(values, 0.0)
    @test mean(replaced) ≈ 4/3
    @test ismissing(sum(values))
    println("Observed summary: ", summary, "; replaced mean: ", mean(replaced))
end

worked_a()
```

## Worked case B: skipmissing does not remove NaN

A NaN remains after missing values are skipped. The helper rejects it under its finite-measurement contract. A group with no observed values returns an explicit missing estimate and a zero observed count. This policy avoids inventing a perfect or zero-valued statistic for an empty observed set.

```julia
using Test
using Statistics

function observed_summary(values)
    observed = collect(skipmissing(values))
    all(isfinite, observed) || throw(DomainError(observed, "Observed values must be finite"))
    estimate = isempty(observed) ? missing : mean(observed)
    return (total = length(values), observed = length(observed), estimate = estimate)
end

function worked_b()
    @test_throws DomainError observed_summary([1.0, NaN, missing])
    empty_observed = observed_summary([missing, missing])
    @test empty_observed.observed == 0
    @test ismissing(empty_observed.estimate)
    @test something(nothing, 7) == 7
    @test coalesce(nothing, 7) === nothing
    @test (missing & false) === false
    println("No observed values: ", empty_observed)
end

worked_b()
```

## State the scientific assumption

Deleting incomplete rows can change a target population. Replacing a missing outcome with zero can also change the meaning of the metric. Imputation introduces modeling assumptions that need validation and uncertainty treatment. A data-manipulation function can implement a policy correctly while the policy remains unsuitable for the scientific question.

Preserve the original missingness indicators and rejected-row counts. If a downstream model requires complete numerical input, document which transformation produced it and whether it used information available at the intended prediction time. A convenient fill operation should not become an undocumented source of leakage.

## Diagnose propagation

Check the element type, count missing values, count nonfinite observed values and inspect the denominator before interpreting a surprising aggregate. A missing result may be a correct reflection of unavailable information. A NaN may instead indicate an arithmetic problem such as zero divided by zero. The appropriate response depends on provenance.

`something` handles absent `nothing` values under a separate convention. It does not silently replace every missing data value. This distinction is useful for an optional lookup result versus an unknown measurement stored in a table. Keep those contracts visible in returned records.

The examples establish the behavior of small authored arrays and one aggregation policy. They do not justify complete-case analysis, zero imputation or any other statistical strategy for an external dataset. Later table, time and modeling units retain these counts and assumptions through larger workflows.


## Six investigations

### 1. Retain the denominator

Summarize 1,missing,3 using observed values.

**Expected:** Total 3, observed 2 and mean 2.

**Hint:** Keep counts alongside the statistic.

### 2. Replace explicitly

Fill the missing value with zero.

**Expected:** The mean becomes 4/3.

**Hint:** Recalculate the denominator and numerator.

### 3. Reject numerical failure

Include NaN among otherwise observed values.

**Expected:** The finite-value guard rejects it.

**Hint:** skipmissing does not remove NaN.

### 4. Handle all-missing data

Summarize two missing observations.

**Expected:** The observed count is 0 and estimate is missing.

**Hint:** Do not fabricate a mean from an empty observed set.

### 5. Distinguish absence

Compare something(nothing,7) with coalesce(nothing,7).

**Expected:** The former returns 7; the latter retains nothing.

**Hint:** The helpers target different sentinel meanings.

### 6. Assess a real policy

Choose deletion or imputation for a scientific dataset.

**Expected:** State assumptions, affected population and uncertainty.

**Hint:** Correct manipulation does not prove valid inference.

## Primary references

- [Julia missing-value semantics](https://docs.julialang.org/en/v1/manual/missing/)
- [Statistics standard library](https://docs.julialang.org/en/v1/stdlib/Statistics/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
