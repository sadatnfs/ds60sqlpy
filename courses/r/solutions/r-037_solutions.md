# r-037: reference reasoning

Use the [complete reference](r-037_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

There are four ways to obtain exactly three heads and one way to obtain four, among sixteen equally likely sequences. The simulation approximates that model probability.

Quadrupling independent repetitions halves this standard error. It does not imply that a biased real-world model becomes correct.

## Explained practice

### Exercise 1

Derive the probability of at least three heads in four fair flips.

It is 5/16.

**Expected evidence:** It is 5/16.

### Exercise 2

Quadruple the number of independent simulation repetitions.

The standard error is halved under the same model.

**Expected evidence:** The standard error is halved under the same model.

### Exercise 3

Simulate an event and retain seed, B, estimate and error estimate.

The report states both the model and finite-repetition uncertainty.

**Expected evidence:** The report states both the model and finite-repetition uncertainty.

### Exercise 4

Diagnose choosing a seed because it produces a desired conclusion.

Fix a declared seed policy and evaluate the model honestly.

**Expected evidence:** Fix a declared seed policy and evaluate the model honestly.

### Exercise 5

Explain p equal to zero or one.

The model-based Monte Carlo variance is zero, which is not proof that an uncertain real-world probability is known exactly.

**Expected evidence:** The model-based Monte Carlo variance is zero, which is not proof that an uncertain real-world probability is known exactly.

### Exercise 6

Separate more simulation from better scientific assumptions.

Increasing B reduces simulation noise but does not remove misspecification or observational bias.

**Expected evidence:** Increasing B reduces simulation noise but does not remove misspecification or observational bias.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
