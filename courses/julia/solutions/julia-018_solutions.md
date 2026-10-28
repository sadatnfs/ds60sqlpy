# julia-018: explained reference

The executable reference is `julia-018_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Choose a calendar window

The window definition changes which observations belong to a period.

**Expected observation:** They end on February 29 and March 1.

## 2. Inspect repeated month addition

Calendar operations should follow the intended business rule rather than an assumed arithmetic identity.

**Expected observation:** The fixture ends on March 29 versus March 31.

## 3. Exclude a future correction

A correction about a past event can still be future information.

**Expected observation:** The available value is 10.

## 4. State cutoff equality

Real ingestion timing may require another rule, which must be documented and tested.

**Expected observation:** The inclusive fixture admits the row.

## 5. Preserve entity identity

An information boundary also needs the correct relational key.

**Expected observation:** The result is missing.

## 6. Handle local civil time

Use a separately prepared timezone-aware policy rather than silently labeling a local clock value as UTC.

**Expected observation:** The standard fixture does not resolve it.
