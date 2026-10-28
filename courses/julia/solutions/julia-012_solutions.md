# julia-012: explained reference

The executable reference is `julia-012_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Preserve a rational

A hardcoded floating accumulator would change the representation contract.

**Expected observation:** The result is exactly 1//1.

## 2. Handle an empty concrete vector

This empty-input policy is valid for this additive operation, not every statistic.

**Expected observation:** The explicit additive identity is 0.

## 3. Inspect invariance

The two vector types have different representation and mutation contracts.

**Expected observation:** It is not.

## 4. Accept a useful family

A suitable signature can preserve generic behavior and avoid unnecessary restrictions.

**Expected observation:** Concrete real vectors can be accepted.

## 5. Reject unrelated elements

Broadening a signature requires defining the corresponding arithmetic or behavior.

**Expected observation:** A MethodError occurs.

## 6. Connect to differentiation

Generic arithmetic is needed for methods such as forward-mode differentiation, subject to their own supported-operation contract.

**Expected observation:** It may discard or reject another numeric representation.
