# r-022: reference reasoning

Use the [complete reference](r-022_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference tests two dispatch paths and two kinds of domain failure. An incompatible unit pair is structurally valid and matches the formal signature, but still fails the operation's compatibility rule. An empty unit passes the slot's character type and fails validObject.

The conversion function makes the scale factor visible and returns a newly validated value. The assertion about the unchanged seconds object separates conversion from in-place mutation. This is a checked local class definition, not an installed package or a claim that every S4 slot mutation automatically runs all invariants.

## Explained practice

### Exercise 1

Predict the result of combining c(1,3) ms with 5 ms.

The result is a FormalMeasure containing c(1,3,5), unit ms.

**Expected evidence:** Three observations in original order.

### Exercise 2

Change the second input to seconds and test the failure.

The typed-pair method raises incompatible units. Dispatch is not a unit conversion system.

**Expected evidence:** The incompatible-units error.

### Exercise 3

Construct a new object with an infinite measurement.

new invokes validity and rejects the nonfinite value.

**Expected evidence:** Finite-vector error.

### Exercise 4

Diagnose a direct x@unit <- character(0) assignment.

Run validObject before exposing the changed value; the domain check fails. Prefer a validated replacement interface.

**Expected evidence:** A semantic validity failure.

### Exercise 5

Test the FormalMeasure,numeric method separately.

combine_measure(x,2) raises the no-declared-unit error rather than accepting it as milliseconds.

**Expected evidence:** Distinct explicit rejection path.

### Exercise 6

Design a safe seconds-to-milliseconds conversion boundary.

A dedicated conversion function checks the original unit, multiplies values by 1000, sets unit ms, and constructs a validated new FormalMeasure. It must reject unknown units.

**Expected evidence:** Two seconds converts to 2000 ms without changing the input.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
