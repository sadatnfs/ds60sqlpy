# julia-024: explained reference

The executable reference is `julia-024_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Refine the time step

This checks the stated smooth problem and does not imply that every refinement improves every numerical task.

**Expected observation:** The fine final value is closer to exp(-1).

## 2. Inspect the complete path

A positive final value alone can hide an unphysical intermediate state.

**Expected observation:** The path includes a negative intermediate value.

## 3. Require a root bracket

A numerical routine cannot create a real root where the stated evidence does not support one.

**Expected observation:** The helper rejects the absent sign change.

## 4. Bound the iteration budget

A stopped computation needs a clear termination reason and evidence about its remaining error.

**Expected observation:** The helper reports budget exhaustion.

## 5. Compare quadrature resolution

A known integral helps separate discretization error from implementation errors.

**Expected observation:** The refined approximation is closer to 1/3.

## 6. Name tolerance units

A small residual alone does not always imply a small position error in an ill-conditioned problem.

**Expected observation:** They have different units and meanings.
