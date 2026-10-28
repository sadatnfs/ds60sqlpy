# julia-003: explained reference

The executable reference is `julia-003_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Advance safely

Adding one to a valid byte index can enter a multibyte character.

**Expected observation:** nextind returns 3.

## 2. Count visible units

A visible text unit can contain multiple code points.

**Expected observation:** Two characters form one grapheme.

## 3. Normalize deliberately

Canonical equivalence is a specific Unicode relation, not arbitrary semantic equivalence.

**Expected observation:** It matches the precomposed form.

## 4. Handle empty text

A parser or display routine needs a documented empty-input policy.

**Expected observation:** The empty case is identified explicitly.

## 5. Choose offset units

Offsets are only reproducible against the same representation and indexing contract.

**Expected observation:** Name byte, character or grapheme units and the text version.

## 6. Add a counterexample

A representative boundary fixture checks a mechanism that ASCII alone cannot exercise.

**Expected observation:** The invalid byte-index assumption becomes visible.
