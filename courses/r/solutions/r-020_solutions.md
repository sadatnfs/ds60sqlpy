# r-020: reference reasoning

Use the [complete reference](r-020_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The independent expected amount is(10+60)/4. Scaling every weight by the same positive constant is a useful invariant that tests meaning rather than source text.

Resetting the same seed before each draw reproduces this generator stream in the same environment. The range assertion checks a separate distribution-support property.

## Explained practice

### Exercise 1

Derive the weighted mean of 10 and 20 with weights 1 and 3.

The result is 17.5.

**Expected evidence:** The result is 17.5.

### Exercise 2

Multiply every weight by five.

The weighted mean stays 17.5.

**Expected evidence:** The weighted mean stays 17.5.

### Exercise 3

Add tests for mismatched lengths and zero total weight.

Both should be rejected explicitly.

**Expected evidence:** Both should be rejected explicitly.

### Exercise 4

Diagnose a test comparing a function with the same copied formula.

Add independently derived fixtures and invariants.

**Expected evidence:** Add independently derived fixtures and invariants.

### Exercise 5

Repeat a random draw under the same seed.

The vectors match within the declared environment/generator configuration.

**Expected evidence:** The vectors match within the declared environment/generator configuration.

### Exercise 6

Write a useful bug report for a dropped matrix dimension.

A reviewer can reproduce the failure without the original private data or hidden session.

**Expected evidence:** A reviewer can reproduce the failure without the original private data or hidden session.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
