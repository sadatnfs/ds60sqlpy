# julia-030: explained reference

The executable reference is `julia-030_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Derive the reduction oracle

The independent formula checks the reduction without copying its loop.

**Expected observation:** The result is 338350.

## 2. Trace an empty chunk

The additive identity makes the empty partial result well-defined.

**Expected observation:** The empty range contributes 0.

## 3. Explain lost updates

Locking the full read-modify-write operation prevents this schedule under the stated protocol.

**Expected observation:** One update can overwrite the other.

## 4. Review scratch ownership

Task-owned state or explicit synchronization is safer than undocumented schedule assumptions.

**Expected observation:** Tasks may migrate or interleave.

## 5. Analyze floating reduction

Use a justified tolerance or a numerically stable reduction when extending the integer example.

**Expected observation:** Floating addition rounds intermediate values.

## 6. Design a performance comparison

Measure the full warmed operation with identical correct outputs and representative data.

**Expected observation:** Include scheduling, work, reduction and thread configuration.
