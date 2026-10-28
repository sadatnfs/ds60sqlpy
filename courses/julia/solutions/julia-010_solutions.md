# julia-010: explained reference

The executable reference is `julia-010_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Validate a unit

Field types alone cannot distinguish supported and unsupported physical units.

**Expected observation:** Construction fails explicitly.

## 2. Inspect conversion

The conversion is deliberate and can have precision consequences for other numeric inputs.

**Expected observation:** Its stored value is Float64.

## 3. Try field reassignment

This says nothing about whether the original measurement was scientifically valid.

**Expected observation:** The operation is rejected.

## 4. Mutate nested storage

Deep immutability requires more than an immutable wrapper.

**Expected observation:** Its contents can change despite the immutable outer struct.

## 5. Create a snapshot

A snapshot policy must account for every nested mutable layer.

**Expected observation:** Later source-vector mutation does not affect that copied vector.

## 6. Review a convenience constructor

An API becomes inconsistent if one creation path bypasses its stated invariant.

**Expected observation:** It preserves the same validation contract.
