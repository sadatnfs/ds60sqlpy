# julia-004: explained reference

The executable reference is `julia-004_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Distinguish zero and absent

A real zero rate is different from having no valid denominator.

**Expected observation:** The first is 0; the second is nothing.

## 2. Check a predicate

The language requires a Boolean decision rather than an implicit truthiness conversion.

**Expected observation:** Julia raises a type error.

## 3. Protect an access

This makes the precondition visible and prevents a predictable boundary error.

**Expected observation:** The access occurs only when the collection is nonempty.

## 4. Compare NaN keys

Dictionary-oriented equality needs consistent treatment of special values.

**Expected observation:** The data-key equality result is true.

## 5. Inspect signed zero

Choose the relation required by the application rather than assuming all equality operations are interchangeable.

**Expected observation:** == agrees; isequal distinguishes them.

## 6. Keep an unknown decision

A data policy must decide whether to reject, defer or explicitly replace the unknown value.

**Expected observation:** Its result can remain missing.
