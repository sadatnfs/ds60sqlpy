# r-021: reference reasoning

Use the [complete reference](r-021_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference separates assembly, validation and dispatch, so each failed input has a stated cause. The matrix case is numeric but has a shape that the vector contract excludes. The NA case demonstrates a declared policy rather than accidental na.rm behavior.

The count generic is an independent operation with the same object invariant. Its default rejection prevents unrelated values from silently acquiring domain meaning. Copy assertions establish behavior for the actual numeric-list representation. They are not a proof that all S3 objects are immutable or that package registration has already occurred.

## Explained practice

### Exercise 1

Trace measurement_total(measurement(c(3,7), "ms")).

UseMethod selects measurement_total.measurement; it returns c(ms=10).

**Expected evidence:** Named total ms=10.

### Exercise 2

Add one observation five to the input and check that the earlier object is unchanged.

measurement(c(x$values,5), x$unit) has total 15; x retains total 10.

**Expected evidence:** Totals 10 and 15 with the same unit.

### Exercise 3

Implement an observed-count generic for measurement objects.

measurement_count uses UseMethod and its measurement method returns length(validate_measurement(x)$values). The three-observation object returns 3L.

**Expected evidence:** Count 3L and explicit default rejection.

### Exercise 4

Diagnose structure(list(values=c(1,Inf),unit="ms"), class="measurement").

The object dispatches as a measurement but violates the finite-vector invariant. The public operation must reject it.

**Expected evidence:** A matching finite-vector validation error.

### Exercise 5

Define the empty-vector and empty-unit cases.

measurement(numeric(0),"ms") has total 0 and count 0; an empty unit string is rejected.

**Expected evidence:** Zero total; malformed unit rejected.

### Exercise 6

Explain whether a measurement containing an environment would have the same copy guarantee.

An environment can be shared across list copies. The current constructor excludes such values, so its tested numeric representation has a narrower value-semantics claim.

**Expected evidence:** State the representation-specific limit.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
