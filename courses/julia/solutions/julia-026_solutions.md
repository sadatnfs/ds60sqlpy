# julia-026: explained reference

The executable reference is `julia-026_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Trace a matrix step

The products[10,12] plus[1,-1] give[11,11].

**Expected observation:** The final vector is[11,11].

## 2. Repeat with new inputs

Multiplication overwrites both entries before adding the bias.

**Expected observation:** The new vector is[5,5].

## 3. Debug a width mismatch

The declared matrix width must equal input length; validation preserves the previous output here.

**Expected observation:** DimensionMismatch occurs before output mutation.

## 4. Find view overlap

The rejection uses mightalias, which conservatively checks possible shared storage.

**Expected observation:** They may address the same parent elements.

## 5. Design scratch ownership

A scratch buffer can preserve the original input, but its owner and lifetime must be explicit.

**Expected observation:** Use a documented private scratch copy before mutation.

## 6. Evaluate a speed claim

Allocation is one measurement. End-to-end timing and correctness remain necessary.

**Expected observation:** Access patterns, dispatch and workload sizes also matter.
