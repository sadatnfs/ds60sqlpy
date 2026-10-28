# julia-028: explained reference

The executable reference is `julia-028_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Derive an oracle

The hand-derived asymmetric case prevents a uniform-output bug from passing.

**Expected observation:** The result is[0.2,0.5,0.3].

## 2. Diagnose overflow

Scaling by the maximum gives[1,1], then divides by 2 without overflowing.

**Expected observation:** The sum exceeds Float64 range.

## 3. Test a permutation

Equivariance checks alignment and catches accidental sorting.

**Expected observation:** The first and last probabilities swap.

## 4. Find a weak property

Properties constrain behavior from different directions; one broad invariant is insufficient.

**Expected observation:** A uniform vector passes it.

## 5. Add an input contract

A rejected input gives the caller a chance to correct the model rather than silently changing its meaning.

**Expected observation:** Each is rejected with ArgumentError.

## 6. Transfer to a regression library

Tests should detect coefficient swaps, row reordering and missing intercepts independently of the fitting implementation.

**Expected observation:** Known points, shape preservation and permutation alignment.
