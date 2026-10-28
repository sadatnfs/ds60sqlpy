# julia-006: explained reference

The executable reference is `julia-006_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Use defaults

A default is part of the function contract and should be recorded when it matters scientifically.

**Expected observation:** The result is 5.

## 2. Override one choice

Explicit keyword configuration makes a transformation reproducible.

**Expected observation:** The result is 3.

## 3. Build a closure

A closure packages a transformation and context; it does not necessarily copy mutable captured objects.

**Expected observation:** The result is 6.

## 4. Trace a rebound argument

Rebinding the argument name is different from mutating the shared object.

**Expected observation:** The caller array remains unchanged.

## 5. Trace a mutated argument

The naming convention warns callers that the operation changes shared state.

**Expected observation:** Its first element becomes 99 and the returned object aliases it.

## 6. Reject an empty mutation

A clear input contract produces a more useful diagnostic than an accidental indexing failure.

**Expected observation:** An explicit ArgumentError is raised.
