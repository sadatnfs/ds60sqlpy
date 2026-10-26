# r-034: reference reasoning

Use the [complete reference](r-034_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The unique id/visit key determines one value per output cell. No aggregation is necessary.

The missing B visit 2 cell means no supplied record here. Keeping the original long rows or a separate presence table preserves that distinction.

## Explained practice

### Exercise 1

Identify the cell key for person/visit/value data.

The key is person plus visit.

**Expected evidence:** The key is person plus visit.

### Exercise 2

Add a third visit for every person.

The wide schema gains the declared third-visit value column.

**Expected evidence:** The wide schema gains the declared third-visit value column.

### Exercise 3

Reverse a complete wide table to long form.

The unique measurement records are recovered under the stated complete-table contract.

**Expected evidence:** The unique measurement records are recovered under the stated complete-table contract.

### Exercise 4

Diagnose two values for one person/visit.

Reject duplicates or perform an explicitly justified aggregation first.

**Expected evidence:** Reject duplicates or perform an explicitly justified aggregation first.

### Exercise 5

Distinguish an absent visit from an observed NA.

Retain presence metadata when the difference matters.

**Expected evidence:** Retain presence metadata when the difference matters.

### Exercise 6

Choose a shape for a model or chart.

Document the chosen observation grain and avoid treating reshaping as an implicit aggregation.

**Expected evidence:** Document the chosen observation grain and avoid treating reshaping as an implicit aggregation.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
