# julia-005: explained reference

The executable reference is `julia-005_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Trace every loop by its iterable. Ranges such as `1:3` include both endpoints, `1:0` is empty, and a descending range needs a negative step. `sum_range` starts its accumulator at 0, so its empty result is 0. Positions come from `eachindex` or `enumerate`, and accumulation lives inside a function so its state is local.

## 1. Count an inclusive range

Inclusive syntax must match the intended number of observations.

**Expected observation:** The range contains 1, 2 and 3.

**Why it holds here:** `1:3` includes both endpoints, so it holds three values: 1, 2 and 3.

**Plausible wrong approach:** Expecting Python-like half-open ranges predicts two values and leaves the last observation out of every loop.

**How to verify:** Check `collect(1:3) == [1, 2, 3]` and `length(1:3) == 3`, the latter already in the reference.

## 2. Use zero iterations

The accumulator policy determines the empty-input result; other algorithms may need to reject emptiness.

**Expected observation:** The result is its initial zero.

**Why it holds here:** `1:0` is empty, so the loop body in `sum_range` never runs and `total` keeps its starting value 0.

**Plausible wrong approach:** Assuming every loop runs at least once predicts an error or a garbage value, when the accumulator simply returns its initial state.

**How to verify:** Assert `sum_range(1:0) == 0` and `[i for i = 1:0] == Int[]`, which the reference also checks.

## 3. Descend explicitly

A positive default step does not produce the requested descending traversal.

**Expected observation:** Use 3:-1:1.

**Why it holds here:** `3:-1:1` starts at 3 and adds -1 until it passes 1, giving 3, 2 and 1.

**Plausible wrong approach:** Writing `3:1` produces an empty range, because the default step is +1 and 3 is already past the stop.

**How to verify:** Compare `collect(3:-1:1)` with `[3, 2, 1]` and `isempty(3:1)` with `true`.

## 4. Keep identity separate

Record identity, position and measurement are distinct roles.

**Expected observation:** Positions are 1 and 2; values remain 10 and 20.

**Why it holds here:** `enumerate([10, 20])` yields pairs `(1, 10)` and `(2, 20)`, keeping positions separate from measured values.

**Plausible wrong approach:** Indexing with the values, as in `v[10]`, treats a measurement as a position and throws `BoundsError` on a two-element vector.

**How to verify:** Collect `enumerate([10, 20])` and compare it with `[(1, 10), (2, 20)]`; the reference checks `eachindex([4, 5])` gives 1 and 2.

## 5. Avoid an unnecessary collection

This changes materialization, but performance claims still need a measured workload.

**Expected observation:** A generator can supply the reduction directly.

**Why it holds here:** `sum(i^2 for i in 1:3 if isodd(i))` feeds 1 and 9 directly to `sum`, giving 10 without allocating an intermediate array.

**Plausible wrong approach:** Claiming the generator is faster without timing assumes allocation dominates, which this tiny input cannot show either way.

**How to verify:** Assert the generator sum equals `sum([i^2 for i in 1:3 if isodd(i)])`; the reference checks `sum(i for i = 1:3) == 6`.

## 6. Trace scope

Explicit inputs and outputs make both reasoning and runtime specialization easier to inspect.

**Expected observation:** Its local state is recreated on every call.

**Why it holds here:** Inside `sum_range`, `total = 0` runs on every call, so `sum_range(-2:2)` gives 0 and `sum_range(2:2)` gives 2 independently.

**Plausible wrong approach:** Updating a top-level `total` inside a script's `for` loop triggers the soft-scope ambiguity warning and then an undefined-variable error.

**How to verify:** The reference asserts `sum_range(2:2) == 2` and `sum_range(-2:2) == 0`; call them in either order and expect the same results.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-005: all reference checks passed`:

Each assertion covers a boundary of a counting loop. `sum_range(2:2)` has exactly one element, `-2:2` cancels to zero, and `1:0` is empty so the comprehension yields `Int[]`. `sum(i for i = 1:3) == 6` checks a generator without building an array, and `eachindex([4, 5])` returns the positions 1 and 2, not the stored values 4 and 5. A loop that started at zero would break the length check.

```julia
function exercise_checks()
    @test sum_range(2:2) == 2
    @test sum_range(-2:2) == 0
    @test length(1:3) == 3
    @test [i for i = 1:0] == Int[]
    @test sum(i for i = 1:3) == 6
    @test collect(eachindex([4, 5])) == [1, 2]
end
```
