# julia-025: explained reference

The executable reference is `julia-025_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Keep correctness and timing in separate claims. `sum_squares` is parametric in `T<:AbstractFloat` and starts at `zero(T)`, so its return type is inferable and matches the element type. `measured` calls the kernel once to compile it, then wraps a second call in `@timed` and returns the value, seconds and bytes, and only the value is asserted.

## 1. Trace the accumulator

The accumulator is Float64 throughout; the final value is 14.

**Expected observation:** The values are 1, 5 and 14.

**Why it holds here:** The loop adds 1 squared to reach 1, then 4 to reach 5, then 9 to reach 14, all as `Float64` because `zero(Float64)` started the total.

**Plausible wrong approach:** Adding the items before squaring gives 6 and then 36, which is the square of the sum rather than the sum of squares.

**How to verify:** Print `total` inside an owned copy of the loop and compare with `sum_squares([1.0, 2.0, 3.0]) == 14`.

## 2. Preserve precision

`zero(T)` and floating multiplication preserve the specified small-case element arithmetic.

**Expected observation:** The result is `Float32(5)`.

**Why it holds here:** With `T = Float32`, `zero(T)` and each product stay `Float32`, so the result is exactly `Float32(5)`.

**Plausible wrong approach:** Initializing `total = 0.0` promotes the sum to `Float64` and makes `@inferred` report a type other than the element type.

**How to verify:** The reference asserts `(@inferred sum_squares(Float32[1, 2])) === Float32(5)`.

## 3. Change workload size

A larger workload changes the experiment. Multiple observations are needed to compare scaling.

**Expected observation:** Both return four times their length; observed time may vary.

**Why it holds here:** Every element of `fill(2.0, n)` contributes 4, so the value is 400 for length 100 and 40000 for length 10000.

**Plausible wrong approach:** Asserting that the longer run takes about 100 times longer turns a machine-dependent observation into a test that can fail randomly.

**How to verify:** Assert the two values, collect several `measured` observations per length and report their spread rather than one number.

## 4. Diagnose invalid science

Inference concerns types. Scientific input validation is a separate contract.

**Expected observation:** The numerical result is NaN.

**Why it holds here:** NaN is a `Float64`, so inference finds the same concrete type and the kernel returns NaN, since NaN times NaN is NaN.

**Plausible wrong approach:** Reading a clean `@code_warntype` report as proof that inputs are valid confuses type stability with data validation.

**How to verify:** The reference asserts `sum_squares([NaN]) |> isnan` and `sum_squares([Inf]) == Inf`; add an explicit `isfinite` check where needed.

## 5. Design a benchmark record

A benchmark record identifies environment and work; a number without these cannot support a transferable claim.

**Expected observation:** Include input, versions, threads, cold/warm boundary and repetitions.

**Why it holds here:** A timing is reproducible only if the record names the input size, Julia version, thread count, warm or cold state and the number of repeats.

**Plausible wrong approach:** Publishing a single `@time` line from a laptop gives readers no way to tell whether compilation or other load was included.

**How to verify:** Store the correctness check result beside each timing row and rerun the record on another machine to compare.

## 6. Transfer to a data pipeline

Phase measurements explain bottlenecks while end-to-end time captures the actual user experience.

**Expected observation:** Separate phases plus end-to-end time.

**Why it holds here:** Timing parsing, fitting and plotting separately locates the slow phase, while one outer timer measures what a user waits for.

**Plausible wrong approach:** Adding the phase times to an outer timer that already contains them counts each phase twice.

**How to verify:** Check that the phase times sum to less than or equal to the end-to-end time and explain any gap.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-025: all reference checks passed`:

```julia
function exercise_checks()
    @test (@inferred sum_squares(Float32[1, 2])) === Float32(5)
    @test sum_squares([-3.0, 4.0]) == 25
    @test sum_squares([NaN]) |> isnan
    @test sum_squares([Inf]) == Inf
    @test measured([2.0]).value == 4
    @test_throws MethodError sum_squares([1, 2])
end
```
