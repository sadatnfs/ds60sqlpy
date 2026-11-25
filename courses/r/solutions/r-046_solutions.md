# r-046: reference reasoning

Run the [complete reference](r-046_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The reference compares sign-invariant quantities and reconstructs the original data using saved preprocessing. It does not assume one implementation's arbitrary loading signs are authoritative. The constant-feature failure and new-row transformation exercise the admission and application boundaries separately.

Explained variance is computed from squared component standard deviations under the selected scaling. It describes this feature representation. A predictive or scientific interpretation must connect it to an independent question and evaluation design.

## Explained practice

### Exercise 1

Compare scaled and unscaled PCA for the proportional two-feature fixture.

The larger-unit column dominates the raw loading; standardization yields equal-magnitude loadings.

**Expected evidence:** Expected loading magnitudes.

**Approach:** Run prcomp twice on the short and long matrix, once with scale. = FALSE and once with scale. = TRUE, and compare absolute first loadings.

**Why it holds here:** long is short multiplied by 10, so its raw variance is 100 times larger. The raw first loading is (1, 10)/sqrt(101), about 0.0995 and 0.995. After standardizing, the columns are identical and each gets 1/sqrt(2), about 0.707.

**Tempting mistake:** Reading the raw 0.995 as long carrying ten times more information. The two columns hold the same values in different units, and changing long from tens to ones would flip the conclusion.

**Verify:** `abs(raw$rotation[2, 1])` returns 10/sqrt(101) within 1e-10, and both entries of `abs(scaled$rotation[, 1])` return 1/sqrt(2).

### Exercise 2

Reconstruct a full two-component standardized fit.

Multiply scores by rotation transpose, restore column scales, then add centers.

**Expected evidence:** Maximum reconstruction error below 1e-10.

**Approach:** Multiply the scores by the transposed rotation, multiply each column by its saved scale, then add its saved center.

**Why it holds here:** prcomp standardized a and b by subtracting 3 and dividing by about 1.826, so the inverse must multiply before adding. With both components kept, the rotation is orthogonal and nothing is discarded, so the rebuild matches y exactly.

**Tempting mistake:** Adding the center before multiplying by the scale. For a = 1 the standardized value is about -1.095, and (-1.095 + 3) times 1.826 is about 3.48 instead of 1.

**Verify:** `max(abs(rebuild(pc$x, pc$rotation) - y))` returns a value below 1e-10.

### Exercise 3

Reverse the first loading and score signs together.

The reconstructed data is unchanged, showing why signs alone are not a stable comparison target.

**Expected evidence:** Equivalent reconstruction.

**Approach:** Negate column 1 of the scores and column 1 of the rotation together, then rebuild.

**Why it holds here:** Each reconstructed value is a sum of score times loading terms, and two negations cancel, so the matrix is unchanged. Either sign of (1, 1)/sqrt(2) describes the same axis.

**Tempting mistake:** Flipping only the rotation, or comparing raw loading signs between two runs. Flipping one side leaves the first component's contribution reversed, so the rebuild of a no longer returns 1, 2, 4 and 5.

**Verify:** `max(abs(rebuild(scores, rotation) - y))` returns a value below 1e-10 after both flips.

### Exercise 4

Diagnose a constant feature under scale.=TRUE.

Division by zero makes standardization undefined; reject or remove the constant feature under a declared policy.

**Expected evidence:** The attempted standardization raises an error.

**Approach:** Attempt prcomp with scale. = TRUE on a matrix with a constant column and treat the error as a decision point.

**Why it holds here:** rep(1, 4) has standard deviation 0, so dividing by it is undefined, and prcomp stops instead of producing values. Dropping that column under a declared rule is then a choice that can be recorded.

**Tempting mistake:** Replacing the zero standard deviation with 1 inside the code so the call succeeds. The column then becomes zeros after centering, and a feature with no variation silently enters the reported shape of the data.

**Verify:** `inherits(try(prcomp(cbind(v = 1:4, constant = rep(1, 4)), scale. = TRUE), silent = TRUE), "try-error")` returns TRUE.

### Exercise 5

Transform a new row using predict and the saved center/scale/rotation.

The manual training-parameter transformation equals predict(pc,newdata).

**Expected evidence:** Matching new-row scores.

**Approach:** Standardize the new row with the training center and scale, multiply by the training rotation, and compare with predict(pc, newdata = new).

**Why it holds here:** The row (3, 2) becomes (0, -1/1.826), about (0, -0.548), using a and b centers of 3. Multiplying by the saved loadings gives scores of magnitude about 0.387 on each component, the same as predict.

**Tempting mistake:** Calling prcomp on the new row by itself. A single row centered on its own mean becomes all zeros and has no spread to scale, so its scores say nothing about where it sits relative to the training data.

**Verify:** `max(abs(manual - predict(pc, newdata = new)))` returns a value below 1e-10.

### Exercise 6

Explain why nearly 100% explained variance is not a downstream prediction-quality result.

PCA optimizes representation variance, not target prediction or causal identification. A held-out downstream task needs separate evaluation.

**Expected evidence:** Scope of the PCA claim stated.

**Approach:** Divide each squared sdev by their total, report the shares, and say what objective produced them.

**Why it holds here:** For a and b the correlation is 0.8, so the shares are 0.9 and 0.1. For short and long the first share is 1. Both describe how well a direction summarizes the inputs, and no outcome variable entered either calculation.

**Tempting mistake:** Claiming that a component explaining 90 or 100 percent of input variance will predict a target well. A target could depend entirely on the 10 percent direction, and only a held out evaluation of that target can show it.

**Verify:** `sum(pc$sdev^2 / sum(pc$sdev^2))` returns 1 within 1e-12, and the printed shares show 0.9 and 0.1.

## What the checks establish

The checks confirm that the unscaled first loading on long has magnitude 10 over the square root of 101, that scaling gives both loadings magnitude one over the square root of 2, that scores times the transposed rotation rebuild the preprocessed data, including after flipping a loading and its scores together, that a constant column cannot be scaled, that a manual projection matches `predict()` on new rows, and that variance shares sum to 1. They do not assign meaning to a component.

The reference makes 7 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
