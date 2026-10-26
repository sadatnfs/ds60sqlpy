# r-029: reference reasoning

Use the [complete reference](r-029_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference tests ordinary completion, a deliberately failed callback and an initially absent seed. Each checks a separate restoration obligation. The numeric output is compared within the same explicit generator configuration rather than asserted as an eternal cross-version sequence.

The digest test changes one known value and retains the original object. Metadata is an explicit allowlist of analysis-relevant fields, so the example does not expose unrelated session state. A reproducible ledger supports review but cannot establish unbiasedness or sound experimental design.

## Explained practice

### Exercise 1

Predict whether two with_rng calls with seed 2026 and identical callbacks match.

They match in the prepared runtime, while the caller stream is restored after each call.

**Expected evidence:** Equal output vectors and equal caller state.

### Exercise 2

Test cleanup after a callback raises an error.

The error propagates and the prior generator kind and seed remain unchanged.

**Expected evidence:** Matched error plus restored state.

### Exercise 3

Test the case where .Random.seed did not exist before the call.

After completion, remove the temporary seed rather than creating ambient RNG state for the caller.

**Expected evidence:** No .Random.seed remains.

### Exercise 4

Change one fixture value and compare its content digest.

The altered fixture has a different SHA256 digest; that identifies a content change without judging its validity.

**Expected evidence:** Different digest and bounded meaning.

### Exercise 5

Record only the configuration and software metadata needed to reproduce this calculation.

Keep seed, draws, missingness rule, input digest, R version, relevant package versions and RNG kinds.

**Expected evidence:** A bounded ledger without unrelated state.

### Exercise 6

Explain why a repeated result is not evidence that the estimator is unbiased.

The same selection bias or model misspecification can repeat exactly. Evaluate design and assumptions separately.

**Expected evidence:** No validity claim from repeatability.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
