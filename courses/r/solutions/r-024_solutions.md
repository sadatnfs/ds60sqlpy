# r-024: reference reasoning

Use the [complete reference](r-024_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The implementation uses the pinned replacement-method syntax and the S7 NULL validator convention. It separately tests constructor validation, property replacement and a compatibility check inside a multi-argument method. These are different sources of guarantees.

The count operation demonstrates an independent generic with the same public class. The all-empty case is deliberate and preserves units. Class-system interoperability is deferred to explicit adapters; the shared @ notation is not used as evidence of S4 inheritance.

## Explained practice

### Exercise 1

Predict the total of Series(values=c(3,7),unit="ms").

series_total returns c(ms=10).

**Expected evidence:** Named total ms=10.

### Exercise 2

Join that Series to a five-millisecond Series.

The result contains c(3,7,5), has unit ms and total 15.

**Expected evidence:** Three values and total 15.

### Exercise 3

Add a series_count generic returning the number of observations.

S7::new_generic("series_count","x") and S7::method(series_count,Series) <- function(x) length(x@values) return 3L for the joined value.

**Expected evidence:** An integer count 3L.

### Exercise 4

Diagnose a validator returning TRUE on success.

The S7 validator must return NULL on success. TRUE belongs to the S4 validity convention taught in r-022.

**Expected evidence:** Use the correct S7 success result.

### Exercise 5

Test invalid property replacement and verify retained state.

Replacing unit with character(0) fails; the previous "ms" unit remains.

**Expected evidence:** Error plus unchanged property.

### Exercise 6

Explain why @ access does not make an S7 object an S4 object.

Use the public S7 interface and explicit adapters rather than assuming S4 slot introspection or methods apply.

**Expected evidence:** No inferred cross-system inheritance.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
