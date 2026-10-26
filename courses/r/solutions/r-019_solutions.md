# r-019: reference reasoning

Use the [complete reference](r-019_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The ID remains character, and the empty missing marker is a deliberate part of this synthetic CSV contract.

The JSON contract contains a scalar ID and an array of values. The RDS round trip additionally retains factor levels, including the unused level.

## Explained practice

### Exercise 1

Explain why row.names=FALSE matters in a CSV export.

It prevents an unintended extra column.

**Expected evidence:** It prevents an unintended extra column.

### Exercise 2

Preserve an ID with leading zeros.

The restored ID stays"001" rather than numeric 1.

**Expected evidence:** The restored ID stays"001" rather than numeric 1.

### Exercise 3

Round-trip one trusted R object with attributes.

saveRDS/readRDS preserve the intended local R structure.

**Expected evidence:** saveRDS/readRDS preserve the intended local R structure.

### Exercise 4

Diagnose default type inference as a schema guarantee.

Specify and validate required column types and missing markers.

**Expected evidence:** Specify and validate required column types and missing markers.

### Exercise 5

State the JSON shape of a one-element measurement vector.

Choose array versus scalar explicitly and test that representation.

**Expected evidence:** Choose array versus scalar explicitly and test that representation.

### Exercise 6

Explain whether a temporary output survives a later classroom run.

Do not rely on arbitrary temporary files; retain source and supported captured artifacts through the documented UI.

**Expected evidence:** Do not rely on arbitrary temporary files; retain source and supported captured artifacts through the documented UI.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
