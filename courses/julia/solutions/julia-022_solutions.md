# julia-022: explained reference

The executable reference is `julia-022_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Check every automatic derivative against an independent calculation and its shape. `quadratic(x) = x[1]^2 + 3x[2]^2` has gradient `[2x1, 6x2]`, `vector_function` has a 2 by 2 Jacobian, and `generic_storage` uses `similar(x)` so dual numbers can pass through, while `hardcoded_storage` forces `Float64`.

## 1. Differentiate analytically

An analytic case provides an independent reference for the AD implementation.

**Expected observation:** The result is `[4, 18]`.

**Why it holds here:** At `[2, 3]`, 2 times 2 is 4 and 6 times 3 is 18, so the gradient is `[4, 18]`.

**Plausible wrong approach:** Testing the gradient only against another AD call reproduces any mistake in the function definition.

**How to verify:** Example A asserts `ForwardDiff.gradient(quadratic, x) ≈ [4, 18]` and a central finite difference along `[1, -1]` matching `dot([4, 18], direction)`.

## 2. Check Jacobian axes

A transposed derivative array can have plausible values but the wrong meaning.

**Expected observation:** Rows correspond to outputs and columns to inputs.

**Why it holds here:** Row 1 is the derivative of `x1^2 + x2`, giving `[4, 1]`, and row 2 is the derivative of `x1 * x2`, giving `[3, 2]`.

**Plausible wrong approach:** Transposing the Jacobian produces `[4 3; 1 2]`, which has plausible numbers but swaps outputs with inputs.

**How to verify:** Example A asserts `ForwardDiff.jacobian(vector_function, x) ≈ [4 1; 3 2]`; the reference checks its size is `(2, 2)`.

## 3. Preserve numeric types

Ordinary evaluation alone does not reveal a differentiation-incompatible conversion.

**Expected observation:** The dual-number path can retain derivative information.

**Why it holds here:** `similar(x)` allocates storage with the input's element type, so dual numbers fit and the gradient `[4, 6]` is returned.

**Plausible wrong approach:** Keeping `zeros(Float64, length(x))` works for plain evaluation but cannot store a dual number, so differentiation fails.

**How to verify:** Example B asserts `@test_throws MethodError ForwardDiff.gradient(hardcoded_storage, x)` and the generic gradient `[4, 6]`.

## 4. Compare reductions

A reduction change alters gradient scale and cannot be treated as a cosmetic refactor.

**Expected observation:** Gradients are `[1, 1]` and `[0.5, 0.5]`.

**Why it holds here:** Each input contributes once to a sum, giving `[1, 1]`, while dividing by `length(x) = 2` halves that to `[0.5, 0.5]`.

**Plausible wrong approach:** Switching a loss from sum to mean without adjusting the learning rate halves every step and changes training behavior.

**How to verify:** The reference asserts both gradients at `[1.0, 2.0]`.

## 5. Inspect a branch boundary

At a nondifferentiable point, a returned convention should not be promoted to a unique mathematical derivative.

**Expected observation:** A library result needs a differentiability interpretation.

**Why it holds here:** At the kink of `abs` at 0, ForwardDiff follows whichever branch the code executes and returns that branch's slope.

**Plausible wrong approach:** Reporting that value as the derivative of `abs` at 0 claims a unique derivative where only a subgradient set exists.

**How to verify:** Evaluate the derivative just left and right of 0 and state the convention the library used at 0 itself.

## 6. Validate a new gradient

Derivative checks should inspect shapes, scales and domain assumptions before optimization.

**Expected observation:** Use meaningful tolerances and retain failures.

**Why it holds here:** A directional finite difference with a small step approximates the derivative up to truncation and rounding error.

**Plausible wrong approach:** Shrinking the step toward 1e-15 to tighten the check lets cancellation error dominate and makes a correct gradient look wrong.

**How to verify:** Compare at several inputs with a stated tolerance, as example A does with `atol = 1e-8`, and keep any failing input.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-022: all reference checks passed`:

```julia
function exercise_checks()
    @test ForwardDiff.derivative(sin, 0.0) == 1
    @test ForwardDiff.derivative(x -> x^3, 2.0) == 12
    @test size(ForwardDiff.jacobian(vector_function, [2.0, 3.0])) == (2, 2)
    @test ForwardDiff.gradient(x -> sum(x), [1.0, 2.0]) == [1, 1]
    @test ForwardDiff.gradient(x -> sum(x)/length(x), [1.0, 2.0]) == [0.5, 0.5]
    @test generic_storage(Float32[2, 3]) isa Float32
end
```
