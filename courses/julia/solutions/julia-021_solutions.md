# julia-021: explained reference

The executable reference is `julia-021_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

`fit_ridge` checks aligned finite inputs and a nonnegative penalty, refuses an unidentified unpenalized design, then solves an augmented least-squares system with one extra row `[0, sqrt(penalty)]` that shrinks only the slope. Penalties are chosen by development error on x = 4 and 5, and the final rows x = 6 and 7 are used once afterward.

## 1. Recover the known model

A correct numerical recovery validates this fixture, not a population inference.

**Expected observation:** The coefficients are approximately `[1, 2]`.

**Why it holds here:** Targets `1 .+ 2x` lie exactly on a line, so with zero penalty the least-squares solution is `[1, 2]` and the training error is essentially zero.

**Plausible wrong approach:** Comparing the fit to coefficients produced by the same function cannot catch an error in the augmented system.

**How to verify:** Example A asserts `coefficients ≈ [1, 2]` and `predict(coefficients, [4, 5]) ≈ [9, 11]`.

## 2. Trace penalty selection

The final outcomes remain assessment inputs rather than selection inputs.

**Expected observation:** The selected penalty is 2.

**Why it holds here:** Among penalties 0, 1, 2 and 4, the development error is smallest for 2, so `argmin` selects index 3 and penalty 2.

**Plausible wrong approach:** Choosing the penalty with the lowest training error always picks 0, because the penalty only adds bias on the training rows.

**How to verify:** Example B asserts `penalties[selected] == 2` and `development_errors[selected] ≈ 1/98`.

## 3. Inspect the selected fit

An independent derivation checks the implementation and penalty convention.

**Expected observation:** They are 12/7 and 13/7.

**Why it holds here:** Penalty 2 gives intercept 12/7 and slope 13/7, which predict 64/7 at x = 4 and 11 at x = 5, so the errors are 1/7 and 0 and the MSE is 1/98.

**Plausible wrong approach:** Penalizing the intercept as well changes both coefficients and no longer matches the augmented row `[0, sqrt(penalty)]`.

**How to verify:** Example B asserts `fits[selected] ≈ [12/7, 13/7]`; recompute the two predictions by hand.

## 4. Keep the final set separate

If final labels change the selection, the procedure is leaking assessment information.

**Expected observation:** The chosen penalty must remain unchanged.

**Why it holds here:** The selection uses only `development_errors`, so changing the final labels 13 and 15 cannot change `selected`.

**Plausible wrong approach:** Picking the penalty after looking at final error turns the final set into a second development set and biases the reported 5/98.

**How to verify:** Edit the final labels in an owned copy and confirm `penalties[selected]` is still 2.

## 5. Reject nonidentification

A numerical solution selection rule should not be mistaken for scientific identification.

**Expected observation:** The teaching helper raises an explicit error.

**Why it holds here:** `x = [1, 1]` makes the design columns proportional, so with penalty 0 `rank(design) < 2` and the helper throws `ArgumentError`.

**Plausible wrong approach:** Letting `\` return some least-squares answer and reporting its slope pretends a slope can be estimated from one x value.

**How to verify:** The reference asserts `@test_throws ArgumentError fit_ridge([1, 1], [2, 3], 0)`.

## 6. Report scope

Real deployment evidence needs representative independent data, uncertainty and diagnostics.

**Expected observation:** Report the observed error without a broad accuracy guarantee.

**Why it holds here:** The final error 5/98 comes from two hand-built rows, so it describes this fixture and nothing about other data.

**Plausible wrong approach:** Quoting 5/98 as expected accuracy on new data treats an arithmetic exercise as a validation study.

**How to verify:** Report the final error with its row count and a statement that the rows are synthetic.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-021: all reference checks passed`:

Four `ArgumentError` cases cover a constant x column with no penalty, mismatched lengths, a negative penalty and a nonfinite input, so `fit_ridge` rejects each before solving. `predict([1, 2], [0, 1]) == [1, 3]` uses literal coefficients, and `mse([1, 2], [1, 4]) == 2` averages squared errors of 0 and 4.

```julia
function exercise_checks()
    @test_throws ArgumentError fit_ridge([1, 1], [2, 3], 0)
    @test_throws ArgumentError fit_ridge([1, 2], [3], 1)
    @test_throws ArgumentError fit_ridge([1, 2], [2, 3], -1)
    @test_throws ArgumentError fit_ridge([1, Inf], [2, 3], 1)
    @test predict([1, 2], [0, 1]) == [1, 3]
    @test mse([1, 2], [1, 4]) == 2
end
```
