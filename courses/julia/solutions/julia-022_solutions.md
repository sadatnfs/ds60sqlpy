# julia-022: explained reference

The executable reference is `julia-022_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Differentiate analytically

An analytic case provides an independent reference for the AD implementation.

**Expected observation:** The result is[4,18].

## 2. Check Jacobian axes

A transposed derivative array can have plausible values but the wrong meaning.

**Expected observation:** Rows correspond to outputs and columns to inputs.

## 3. Preserve numeric types

Ordinary evaluation alone does not reveal a differentiation-incompatible conversion.

**Expected observation:** The dual-number path can retain derivative information.

## 4. Compare reductions

A reduction change alters gradient scale and cannot be treated as a cosmetic refactor.

**Expected observation:** Gradients are[1,1] and[0.5,0.5].

## 5. Inspect a branch boundary

At a nondifferentiable point, a returned convention should not be promoted to a unique mathematical derivative.

**Expected observation:** A library result needs a differentiability interpretation.

## 6. Validate a new gradient

Derivative checks should inspect shapes, scales and domain assumptions before optimization.

**Expected observation:** Use meaningful tolerances and retain failures.
