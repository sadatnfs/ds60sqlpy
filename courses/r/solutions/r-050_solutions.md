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

**Approach:** Fit `y ~ x` and `y ~ x + I(x^2)` on the five training rows and compare the quadratic coefficients with the generating rule.

**Why it holds here:** The training y values are -5, -1.5, 1, 2.5 and 3, which follow 1 + 2x - 0.5x^2 exactly, so the quadratic recovers 1, 2 and -0.5. Because x is symmetric around 0, the affine fit is 0 + 2x.

**Tempting mistake:** Writing `y ~ x + x^2`. In a formula, x^2 means x crossed with itself, which is just x, so the second model silently becomes the affine one.

**Verify:** `max(abs(unname(coef(quadratic)) - c(1, 2, -0.5)))` returns a value below 1e-10.

### Exercise 2

Calculate both held-out MSE values on the same four IDs.

Affine error is 0.390625 and the exact quadratic fixture error is near zero.

**Expected evidence:** Two correctly labeled metrics and count 4.

**Approach:** Predict both models on the same four held out x values and average squared errors over those 4 rows.

**Why it holds here:** The affine error is 1 - 0.5x^2, which is -0.125 at x = 1.5 or -1.5 and 0.875 at x = 0.5 or -0.5. The squares sum to 1.5625, and dividing by 4 gives 0.390625. The quadratic error is zero up to rounding.

**Tempting mistake:** Scoring the affine model on its training rows, where its MSE is 0.7, and setting that against the quadratic's held out score. The two numbers then differ in rows as well as model.

**Verify:** `abs(score - 0.390625) < 1e-10` returns TRUE and `nrow(paired)` returns 4.

### Exercise 3

Reorder one candidate table and realign by ID before scoring.

The correctly aligned score is unchanged; positional subtraction is not a valid substitute.

**Expected evidence:** Permutation-invariant keyed score.

**Approach:** Reverse the prediction table, merge it with the held out rows by id, and confirm that no id is duplicated before scoring.

**Why it holds here:** The merge pairs each id with its own prediction regardless of row order, so reversing the table leaves the score at 0.390625.

**Tempting mistake:** Subtracting the reversed predictions by position. The actual values -3.125, -0.125, 1.875 and 2.875 then meet predictions 3, 1, -1 and -3, and the MSE jumps to 20.390625.

**Verify:** `!anyDuplicated(paired$id)` returns TRUE and the keyed score returns 0.390625 within 1e-10.

### Exercise 4

Diagnose choosing the model repeatedly from the final held-out score.

Repeated tuning on that set turns it into development data; a new final assessment is needed for a clean final claim.

**Expected evidence:** Selection boundary stated.

**Approach:** Fix both candidate formulas before looking at the four held out points, and score them there once.

**Why it holds here:** With only four held out rows, trying many formulas against them and keeping the best one makes the winner look better than it would on fresh points. That set has then been used for selection.

**Tempting mistake:** Trying cubic, quartic and other variants, keeping whichever scores lowest on these points, and reporting that score as the final error. The four points chose the model, so they no longer measure it.

**Verify:** A run log shows the four ids q1 to q4 scored once, after both formulas were fixed, and `nrow(heldout)` returns 4.

### Exercise 5

Round-trip a report through an owned temporary JSON file.

Named fields survive serialization and the file is removed after the scoped operation.

**Expected evidence:** Report readback and owned cleanup.

**Approach:** Write the report to a tempfile path, register `unlink` with on.exit before writing, read it back and compare fields.

**Why it holds here:** The report holds the metric name, count 4, the affine score, the R version and a limitation. on.exit runs even if the readback check fails, so the file the function created is removed either way.

**Tempting mistake:** Writing to a fixed name such as report.json in the working directory. It can overwrite a file the user owns and stays behind after the function returns.

**Verify:** `restored$count == 4` returns TRUE inside the function, and `file.exists(removed)` returns FALSE afterward.

### Exercise 6

Write the conclusion without extending the synthetic result to a population.

The quadratic representation fits this known rule and performs better on the four declared held-out points. Broader model choice and uncertainty remain unestablished.

**Expected evidence:** A bounded, factual conclusion.

**Approach:** Name the task, the 4 held out points, both scores and the fact that the target was generated by a quadratic rule.

**Why it holds here:** The quadratic wins here because the data were built from a quadratic with no noise, so a zero error is guaranteed rather than discovered. The affine gap of 0.390625 rests on four points.

**Tempting mistake:** Concluding that quadratic models are generally better for data like this. Nothing in five training rows with no noise says how either model behaves on real measurements.

**Verify:** The printed `mse` shows 0.390625 for affine and a value below 1e-20 for quadratic, and the written conclusion names the 4 held out points.

## What the checks establish

The reference makes 6 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
