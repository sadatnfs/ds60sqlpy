# julia-019: explained reference

The executable reference is `julia-019_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Solve with a factorization, then check the original equation. Worked example A factorizes `[3.0 1.0; 1.0 2.0]` with `lu` and solves for `[9.0, 8.0]`. Worked example B builds a design with two identical `x` columns, so its rank is 2 of 3 and many coefficient vectors give the same fitted values.

## 1. Verify a solution

A residual is a useful numerical check but must be interpreted alongside conditioning.

**Expected observation:** The residual is near zero.

**Why it holds here:** `[3 1; 1 2] * [2, 3]` gives 6 + 3 = 9 and 2 + 6 = 8, so the residual `matrix * solution - target` is close to zero.

**Plausible wrong approach:** Checking the solution against itself, for example by solving twice, cannot detect a transcription error in the matrix.

**How to verify:** Example A asserts `solution ≈ [2.0, 3.0]` and `norm(matrix * solution - target) < 1e-12`.

## 2. Reuse a factorization

Reusable factorization separates setup from repeated solves.

**Expected observation:** The solution doubles for this linear system.

**Why it holds here:** Linearity means `factorization \ (2target)` returns twice the old solution, `[4, 6]`, reusing the same LU factors.

**Plausible wrong approach:** Calling `matrix \ (2target)` inside a loop of many right-hand sides refactorizes each time and wastes the setup work.

**How to verify:** Example A asserts `factorization \ (2target) ≈ 2solution`.

## 3. Expose nonidentification

Fitted-value agreement does not uniquely identify every parameter.

**Expected observation:** Predictions on the design remain unchanged.

**Why it holds here:** The design has columns `1`, `x` and `x`, so `design * [0, 1, -1]` is zero and adding it leaves every prediction unchanged.

**Plausible wrong approach:** Reading the second coefficient as the effect of `x` assumes identification that the duplicated column removes.

**How to verify:** Example B asserts `rank(design) == 2` and that `design * alternative ≈ target`.

## 4. Interpret a pseudoinverse

It does not supply missing scientific identification assumptions.

**Expected observation:** The pseudoinverse solution has smaller norm than the shifted alternative.

**Why it holds here:** The pseudoinverse picks the minimum-norm solution, which splits the slope of 2 evenly to give `[1, 1, 1]` with norm sqrt(3), while the shifted `[1, 2, 0]` has norm sqrt(5).

**Plausible wrong approach:** Presenting the pseudoinverse coefficients as the true effects treats a tie-breaking rule as scientific evidence.

**How to verify:** Example B asserts `norm(coefficients) < norm(alternative)`; print both vectors and their norms.

## 5. Use the correct transpose

Matching dimensions alone is insufficient to choose the correct complex inner-product convention.

**Expected observation:** The products are 7 and 3-2im.

**Why it holds here:** `values' * values` conjugates, giving |1+i|^2 + |2-i|^2 = 2 + 5 = 7; `transpose(values) * values` does not, giving (1+i)^2 + (2-i)^2 = 3 - 2i.

**Plausible wrong approach:** Using `transpose` for a complex norm because the shapes match returns a complex number that is not a length.

**How to verify:** The reference asserts `values' * values == 7+0im`, `transpose(values) * values == 3-2im` and `norm(values)^2 ≈ 7`.

## 6. Assess sensitivity

Numerical accuracy and scientific interpretation require the appropriate assumptions and scales.

**Expected observation:** Inspect conditioning as well as residuals.

**Why it holds here:** A nearly singular matrix can have a tiny residual while its solution swings widely under small changes in the data.

**Plausible wrong approach:** Reporting a small residual as proof of reliable coefficients ignores the condition number that multiplies input errors.

**How to verify:** Print `cond(matrix)`, perturb the target slightly and compare the change in the solution with the change in the data; the reference shows `rank([1.0 2.0; 2.0 4.0]) == 1` as a singular case.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-019: all reference checks passed`:

For complex vectors, `dot` and the adjoint product both conjugate the first argument, giving 7, the squared norm. `transpose(values) * values` skips conjugation and returns `3 - 2im`, so the two operators must not be swapped. `rank([1 2; 2 4]) == 1` detects the dependent rows, and multiplying a two by two matrix by a length-three vector raises `DimensionMismatch`.

```julia
function exercise_checks()
    values = ComplexF64[1+im, 2-im]
    @test dot(values, values) == 7+0im
    @test values' * values == 7+0im
    @test transpose(values) * values == 3-2im
    @test norm(values)^2 ≈ 7
    @test rank([1.0 2.0; 2.0 4.0]) == 1
    @test_throws DimensionMismatch [1.0 0.0; 0.0 1.0] * [1.0, 2.0, 3.0]
end
```
