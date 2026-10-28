# julia-005: explained reference

The executable reference is `julia-005_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Count an inclusive range

Inclusive syntax must match the intended number of observations.

**Expected observation:** The range contains 1,2,3.

## 2. Use zero iterations

The accumulator policy determines the empty-input result; other algorithms may need to reject emptiness.

**Expected observation:** The result is its initial zero.

## 3. Descend explicitly

A positive default step does not produce the requested descending traversal.

**Expected observation:** Use 3:-1:1.

## 4. Keep identity separate

Record identity, position and measurement are distinct roles.

**Expected observation:** Positions are 1 and 2; values remain 10 and 20.

## 5. Avoid an unnecessary collection

This changes materialization, but performance claims still need a measured workload.

**Expected observation:** A generator can supply the reduction directly.

## 6. Trace scope

Explicit inputs and outputs make both reasoning and runtime specialization easier to inspect.

**Expected observation:** Its local state is recreated on every call.
