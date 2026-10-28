# julia-011: explained reference

The executable reference is `julia-011_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Add a zero-size shape

The constructor permits nonnegative dimensions, including zero.

**Expected observation:** Its area is 0.

## 2. Reject an invalid dimension

A method for the right type can still receive scientifically invalid values unless its contract prevents them.

**Expected observation:** Construction raises ArgumentError.

## 3. Trace both arguments

There is no requirement that one argument be a special receiver.

**Expected observation:** Different methods handle the two cases.

## 4. Resolve the overlap

An intersection method documents behavior and prevents ambiguity.

**Expected observation:** The explicit intersection method is selected.

## 5. Keep an unsupported case visible

A catch-all fallback should be added only when its semantics are defined.

**Expected observation:** A MethodError is raised.

## 6. Extend an owned interface

Test the new method and invariants rather than assuming subtype membership proves interface correctness.

**Expected observation:** The generic total can use the operation if its laws hold.
