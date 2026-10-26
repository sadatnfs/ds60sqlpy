# r-050: reference reasoning

Use the [complete reference](r-050_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The exact quadratic coefficients and affine held-out error provide independent arithmetic oracles. The keyed merge deliberately changes row order so an implementation relying on coincidental vector alignment would be exposed.

The report retains the metric denominator and a limitation rather than promoting one score into an unsupported scientific claim. Its JSON file is an owned temporary demonstration. Persistent storage, publication and browser delivery are separate workflow capabilities.

## Explained practice

### Exercise 1

Fit both candidate formulas using only the five training rows.

The quadratic coefficients recover 1,2,-0.5; the affine candidate is the stated baseline.

**Expected evidence:** Correct coefficient oracle.

### Exercise 2

Calculate both held-out MSE values on the same four IDs.

Affine error is 0.390625 and the exact quadratic fixture error is near zero.

**Expected evidence:** Two correctly labeled metrics and count 4.

### Exercise 3

Reorder one candidate table and realign by ID before scoring.

The correctly aligned score is unchanged; positional subtraction is not a valid substitute.

**Expected evidence:** Permutation-invariant keyed score.

### Exercise 4

Diagnose choosing the model repeatedly from the final held-out score.

Repeated tuning on that set turns it into development data; a new final assessment is needed for a clean final claim.

**Expected evidence:** Selection boundary stated.

### Exercise 5

Round-trip a report through an owned temporary JSON file.

Named fields survive serialization and the file is removed after the scoped operation.

**Expected evidence:** Report readback and owned cleanup.

### Exercise 6

Write the conclusion without extending the synthetic result to a population.

The quadratic representation fits this known rule and performs better on the four declared held-out points. Broader model choice and uncertainty remain unestablished.

**Expected evidence:** A bounded, factual conclusion.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
