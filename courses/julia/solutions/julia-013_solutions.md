# julia-013: explained reference

The executable reference is `julia-013_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Choose the axis

The explicit singleton axis documents the intended broadcast alignment.

**Expected observation:** Reshape the offsets into a one-row array.

## 2. Reject incompatible axes

Shape validation prevents a silent interpretation of an unintended operation.

**Expected observation:** A DimensionMismatch occurs.

## 3. Update in place

This dependence pattern makes the specific self-update straightforward to reason about.

**Expected observation:** The destination values change to the expected affine result.

## 4. Trace a manual recurrence

The loop implements a recurrence, not a simultaneous snapshot assignment.

**Expected observation:** The example becomes[1,1,1,1].

## 5. Preserve a snapshot

The copy changes the read/write dependency and therefore the algorithm.

**Expected observation:** The example becomes[1,1,2,3].

## 6. Choose a destination type

Allocate a representation that can express the intended result.

**Expected observation:** The incompatible conversion is rejected.
