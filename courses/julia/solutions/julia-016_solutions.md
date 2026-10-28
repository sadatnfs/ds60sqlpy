# julia-016: explained reference

The executable reference is `julia-016_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Trace the duplicate pair

Join multiplicity can inflate a sum even when every individual match is syntactically valid.

**Expected observation:** The left entity 1 weight appears twice.

## 2. Enforce a lookup contract

An executable cardinality check prevents an unintended many-to-many relationship from passing silently.

**Expected observation:** The duplicate-key input is rejected.

## 3. Aggregate at a declared grain

Preaggregation is a semantic decision, not a universal repair for duplicates.

**Expected observation:** Two entity rows and weight total 300 are preserved.

## 4. Choose missing-key behavior

The policy must reflect the data model and should be reported with excluded counts.

**Expected observation:** The fixture yields 1 or 0 matched rows.

## 5. Inspect unmatched keys

A row-count total is not enough to explain which entities failed to match.

**Expected observation:** The fixture exposes left-only, both and right-only rows.

## 6. Avoid cosmetic deduplication

Distinct operations can conceal a modeling error and need their own justified rule.

**Expected observation:** The scientific meaning remains unresolved.
