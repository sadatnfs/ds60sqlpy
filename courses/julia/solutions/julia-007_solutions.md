# julia-007: explained reference

The executable reference is `julia-007_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Read a shape

Operations can dispatch or broadcast differently for these shapes.

**Expected observation:** Their sizes are(2,) and(2,1).

## 2. Trace column order

The storage order is explicit and should not be confused with the scientific interpretation of axes.

**Expected observation:** It is at row 1,column 3.

## 3. Take a snapshot

A snapshot protects later reads from this mutation, with an allocation cost.

**Expected observation:** The original scalar-element vector is unchanged.

## 4. Use a shared window

A view is useful when shared mutation or avoided copying is intended.

**Expected observation:** The original array changes.

## 5. Copy nested state

The required independence level depends on the data structure and algorithm.

**Expected observation:** A shallow copy shares inner vectors; a deep copy does not in this fixture.

## 6. Retain a bound check

Bounds checking makes a violated indexing contract observable before considering lower-level optimizations.

**Expected observation:** A BoundsError is raised.
