# julia-008: explained reference

The executable reference is `julia-008_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Make one tuple element

The tuple syntax distinguishes a one-field collection from the scalar value.

**Expected observation:** Use(7,), including its comma.

## 2. Name a returned record

The representation makes a small fixed schema inspectable.

**Expected observation:** Callers can access fields by their names.

## 3. Preserve multiplicity

Deduplication intentionally discards multiplicity and can change a scientific denominator.

**Expected observation:** Counts are 1 and 2 while the set has two distinct labels.

## 4. Control presentation order

Stable presentation requires an explicit contract rather than an incidental implementation order.

**Expected observation:** The report follows the chosen ordering rule.

## 5. Separate absent and zero

Only use an absent-to-zero convention when the measurement contract justifies it.

**Expected observation:** haskey distinguishes them.

## 6. Inspect special keys

Dictionary equality semantics should match the application meaning of the keys.

**Expected observation:** NaN is retrievable and the signed zeros remain distinct in this fixture.
