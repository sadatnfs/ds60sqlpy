# julia-019: explained reference

The executable reference is `julia-019_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Verify a solution

A residual is a useful numerical check but must be interpreted alongside conditioning.

**Expected observation:** The residual is near zero.

## 2. Reuse a factorization

Reusable factorization separates setup from repeated solves.

**Expected observation:** The solution doubles for this linear system.

## 3. Expose nonidentification

Fitted-value agreement does not uniquely identify every parameter.

**Expected observation:** Predictions on the design remain unchanged.

## 4. Interpret a pseudoinverse

It does not supply missing scientific identification assumptions.

**Expected observation:** The pseudoinverse solution has smaller norm than the shifted alternative.

## 5. Use the correct transpose

Matching dimensions alone is insufficient to choose the correct complex inner-product convention.

**Expected observation:** The products are 7 and 3-2im.

## 6. Assess sensitivity

Numerical accuracy and scientific interpretation require the appropriate assumptions and scales.

**Expected observation:** Inspect conditioning as well as residuals.
