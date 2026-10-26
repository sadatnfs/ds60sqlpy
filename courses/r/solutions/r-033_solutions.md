# r-033: reference reasoning

Use the [complete reference](r-033_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The lookup adds exactly one category per fact and retains the original line order. Key validation makes the first-match behavior safe for this contract.

The A fact appears twice. A duplicate-key guard would reject the dimension before the incorrect total becomes a report.

## Explained practice

### Exercise 1

Predict the category sequence for fact keys B, A, B.

Home, Paper, Home.

**Expected evidence:** Home, Paper, Home.

### Exercise 2

Add an unmatched key C.

The missing index must be rejected or retained under an explicit diagnostic policy.

**Expected evidence:** The missing index must be rejected or retained under an explicit diagnostic policy.

### Exercise 3

Write a many-to-one join guard.

No duplicated dimension key and no unmatched required fact key are admitted.

**Expected evidence:** No duplicated dimension key and no unmatched required fact key are admitted.

### Exercise 4

Diagnose a total rising after a dimension join.

The join may have multiplied fact records.

**Expected evidence:** The join may have multiplied fact records.

### Exercise 5

Join an empty fact table.

No facts or additive amounts should be created.

**Expected evidence:** No facts or additive amounts should be created.

### Exercise 6

Transfer the checks to SQL or Spark.

Declare join keys, expected matches, unmatched policy and before/after reconciliation.

**Expected evidence:** Declare join keys, expected matches, unmatched policy and before/after reconciliation.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
