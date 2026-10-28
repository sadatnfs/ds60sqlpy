# julia-009: explained reference

The executable reference is `julia-009_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Keep valid zero

The input satisfies the contract and its arithmetic mean happens to be zero.

**Expected observation:** The result is the valid number 0.

## 2. Reject empty input

A fabricated zero would hide the absence of evidence.

**Expected observation:** ArgumentError identifies the missing observation requirement.

## 3. Reject nonfinite values

Nonfinite values need a declared policy rather than silent propagation into a report.

**Expected observation:** DomainError is raised.

## 4. Preserve an unexpected error

A broad catch can hide a programming defect behind a normal-looking outcome.

**Expected observation:** The unexpected method error is rethrown.

## 5. Test independently

Different reasoning paths reduce the chance that code and test share one unnoticed error.

**Expected observation:** The assertion has an independent basis.

## 6. Report rejected rows

Selection through validation can change the target population and should remain visible.

**Expected observation:** Retain counts and reasons for rejected rows.
