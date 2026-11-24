# julia-028: explained reference

The executable reference is `julia-028_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

`probabilities` rejects empty, nonfinite, negative and all-zero weights, divides by the largest weight to avoid overflow and then normalizes. Tests combine three kinds of evidence: hand-derived asymmetric cases, properties checked on generated inputs from `Xoshiro(140)`, and invariants such as unchanged input and ratio preservation.

## 1. Derive an oracle

The hand-derived asymmetric case prevents a uniform-output bug from passing.

**Expected observation:** The result is `[0.2, 0.5, 0.3]`.

**Why it holds here:** The weights `[2, 5, 3]` total 10, so the probabilities are 2/10, 5/10 and 3/10.

**Plausible wrong approach:** Checking only `[1, 1, 1]` lets a function that always returns equal shares pass, because the correct answer is uniform too.

**How to verify:** The reference asserts `probabilities(values) ≈ [0.2, 0.5, 0.3]` and that the ratio of the second to the first is 2.5.

## 2. Diagnose overflow

Scaling by the maximum gives `[1, 1]`, then divides by 2 without overflowing.

**Expected observation:** The sum exceeds Float64 range.

**Why it holds here:** `1e308 + 1e308` exceeds `floatmax(Float64)` and becomes `Inf`, while dividing by the maximum first gives `[1, 1]` and then `[0.5, 0.5]`.

**Plausible wrong approach:** Dividing each weight by `sum(weights)` directly returns `[0, 0]` here because every weight is divided by infinity.

**How to verify:** Example A asserts `probabilities([1e308, 1e308]) == [0.5, 0.5]`.

## 3. Test a permutation

Equivariance checks alignment and catches accidental sorting.

**Expected observation:** The first and last probabilities swap.

**Why it holds here:** Swapping the first and last weights to `[3, 5, 2]` should give `[0.3, 0.5, 0.2]`, because each output is tied to its own input position.

**Plausible wrong approach:** An implementation that sorts weights first returns the same order for both inputs and passes sum-to-one checks.

**How to verify:** Example B checks `probabilities(values[permutation]) ≈ result[permutation]` on 20 generated inputs.

## 4. Find a weak property

Properties constrain behavior from different directions; one broad invariant is insufficient.

**Expected observation:** A uniform vector passes it.

**Why it holds here:** A uniform output always sums to 1, so the sum property cannot tell correct weighting from ignoring the weights.

**Plausible wrong approach:** Relying on `sum(result) ≈ 1` as the only test gives confidence that is not earned.

**How to verify:** Combine the sum property with the hand case and the scaling property `probabilities(7 .* values) ≈ result`.

## 5. Add an input contract

A rejected input gives the caller a chance to correct the model rather than silently changing its meaning.

**Expected observation:** Each is rejected with ArgumentError.

**Why it holds here:** Negative weights, all zeros and NaN or Inf each violate the definition, so `ArgumentError` lets the caller fix the model.

**Plausible wrong approach:** Clamping negatives to zero or returning a uniform vector for all zeros changes the model's meaning without telling the caller.

**How to verify:** The reference asserts `ArgumentError` for empty, `[Inf, 1]` and `[NaN]`; example A covers `[0, 0]` and `[1, -1]`.

## 6. Transfer to a regression library

Tests should detect coefficient swaps, row reordering and missing intercepts independently of the fitting implementation.

**Expected observation:** Known points, shape preservation and permutation alignment.

**Why it holds here:** For a line with known intercept 1 and slope 2, predictions at x = 0 and 1 must be 1 and 3, the output length must match the input, and reordering rows must reorder predictions.

**Plausible wrong approach:** Deriving expected predictions from the fitted coefficients of the same code cannot catch swapped coefficients.

**How to verify:** Write these properties with literal coefficients, as in `predict([1, 2], [0, 1]) == [1, 3]` from lesson julia-021.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-028: all reference checks passed`:

`probabilities([3]) == [1]` covers the single-weight case. The final three lines combine a hand-derived answer, a check that `values` still equals `before`, and the ratio 2.5, which holds because normalizing divides both entries by the same total.

```julia
function exercise_checks()
    @test_throws ArgumentError probabilities(Float64[])
    @test_throws ArgumentError probabilities([Inf, 1])
    @test_throws ArgumentError probabilities([NaN])
    @test probabilities([3]) == [1]
    values = [2.0, 5.0, 3.0]
    before = copy(values)
    @test probabilities(values) ≈ [0.2, 0.5, 0.3]
    @test values == before
    @test probabilities(values)[2] / probabilities(values)[1] ≈ 2.5
end
```
