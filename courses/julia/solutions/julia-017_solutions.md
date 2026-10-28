# julia-017: explained reference

The executable reference is `julia-017_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Preserve a textual ID

Numeric-looking keys can lose meaning when inference converts them to integers.

**Expected observation:** Its leading zeros remain.

## 2. Declare missingness

A missing marker should not silently become a valid numeric zero.

**Expected observation:** The second amount is missing.

## 3. Reject a wrong type

Changing the schema or using a repair policy requires an explicit decision.

**Expected observation:** The parser raises its typed-input error.

## 4. Retain quoted content

Correct quoting preserves structure without promising byte-identical formatting to every original file.

**Expected observation:** The restored field values agree.

## 5. Handle buffer position

An empty read after a write can reflect the current position rather than missing source data.

**Expected observation:** Reset or take the bytes explicitly.

## 6. Separate parsing and meaning

Types and delimiters do not establish grain, units or scientific validity.

**Expected observation:** The relational data contract still needs validation.
