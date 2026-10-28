# julia-015: explained reference

The executable reference is `julia-015_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Name the derived field

Names and shape are part of the resulting schema.

**Expected observation:** The output column contains 1,2,3 under the explicit name scaled.

## 2. Observe a shared column

A caller must request a copy when independent storage is required.

**Expected observation:** The source DataFrame changes.

## 3. Retain a column snapshot

A snapshot is useful for comparison and provenance when future mutation is possible.

**Expected observation:** The copied values remain unchanged.

## 4. Report group coverage

Row accounting remains necessary after grouping.

**Expected observation:** It reports 2 rows,1 observed score and mean 1.

## 5. Handle an all-missing group

A fabricated zero could change later model or business decisions.

**Expected observation:** The result is missing.

## 6. Interpret a mean of means

Group-level and row-level summaries represent different populations.

**Expected observation:** The answers can differ.
