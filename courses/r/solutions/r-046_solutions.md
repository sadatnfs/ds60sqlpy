# r-046: reference reasoning

Use the [complete reference](r-046_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference compares sign-invariant quantities and reconstructs the original data using saved preprocessing. It does not assume one implementation's arbitrary loading signs are authoritative. The constant-feature failure and new-row transformation exercise the admission and application boundaries separately.

Explained variance is computed from squared component standard deviations under the selected scaling. It describes this feature representation. A predictive or scientific interpretation must connect it to an independent question and evaluation design.

## Explained practice

### Exercise 1

Compare scaled and unscaled PCA for the proportional two-feature fixture.

The larger-unit column dominates the raw loading; standardization yields equal-magnitude loadings.

**Expected evidence:** Expected loading magnitudes.

### Exercise 2

Reconstruct a full two-component standardized fit.

Multiply scores by rotation transpose, restore column scales, then add centers.

**Expected evidence:** Maximum reconstruction error below 1e-10.

### Exercise 3

Reverse the first loading and score signs together.

The reconstructed data is unchanged, showing why signs alone are not a stable comparison target.

**Expected evidence:** Equivalent reconstruction.

### Exercise 4

Diagnose a constant feature under scale.=TRUE.

Division by zero makes standardization undefined; reject or remove the constant feature under a declared policy.

**Expected evidence:** The attempted standardization raises an error.

### Exercise 5

Transform a new row using predict and the saved center/scale/rotation.

The manual training-parameter transformation equals predict(pc,newdata).

**Expected evidence:** Matching new-row scores.

### Exercise 6

Explain why nearly 100% explained variance is not a downstream prediction-quality result.

PCA optimizes representation variance, not target prediction or causal identification. A held-out downstream task needs separate evaluation.

**Expected evidence:** Scope of the PCA claim stated.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
