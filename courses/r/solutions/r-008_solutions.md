# r-008: reference reasoning

Run the [complete reference](r-008_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

Each row combines an intercept and one feature with the same coefficient vector. Matrix multiplication preserves one output per observation.

The residual checks the solved equation. The extraction comparison shows why a one-column matrix needs an explicit shape policy.

## Explained practice

### Exercise 1

Predict the first row of matrix(1:6, nrow=2).

The first row is 1,3,5.

**Approach:** Build the matrix with the default fill and read its first row with `m[1, ]`.

**Why it holds here:** R fills down columns: the first column takes 1 and 2, the second 3 and 4, the third 5 and 6. The first row is therefore 1, 3, 5.

**Tempting mistake:** Reading the input order 1, 2, 3 as the first row, which assumes filling across rows. That only happens with `byrow = TRUE`.

**Verify:** The reference asserts `identical(m[1, ], c(1L, 3L, 5L))`, and `print(m)` shows row `[1,]` as 1 3 5.

### Exercise 2

Construct the same dimensions with byrow=TRUE.

The first row becomes 1,2,3.

**Approach:** Pass `byrow = TRUE` with the same `nrow = 2`.

**Why it holds here:** The shape stays 2 by 3, but the six values now fill across, so the first row is 1, 2, 3 and the second 4, 5, 6.

**Tempting mistake:** Transposing with `t(m)` instead. That produces a 3 by 2 matrix whose first row is 1, 2, a different shape from the one requested.

**Verify:** `by_row[1, ]` returns 1, 2, 3 as the reference checks, and `dim(by_row)` returns 2 and 3.

### Exercise 3

Compute predictions for intercept two and slope three at x=3,4.

The predictions are 11 and 14.

**Approach:** Bind a column of ones to the feature values and multiply: `cbind(1, c(3, 4)) %*% c(2, 3)`.

**Why it holds here:** Each row computes 2 * 1 + 3 * x, so x = 3 gives 11 and x = 4 gives 14. The column of ones is what lets the intercept enter every row.

**Tempting mistake:** Leaving out the ones column. `c(3, 4) %*% c(2, 3)` treats both as vectors and returns their inner product, a 1 by 1 matrix holding 18.

**Verify:** `as.numeric(design %*% c(2, 3))` returns 11 and 14, and `dim()` of the product shows 2 and 1.

### Exercise 4

Diagnose replacing %*% with *.

Keep the matrix product and validate dimensions.

**Approach:** Keep `%*%` and add a shape guard, `ncol(design) == length(beta)`, before multiplying.

**Why it holds here:** The matrix product sums feature times coefficient within each row. The elementwise `*` in Example 3 recycles beta by row instead, so no feature receives its own coefficient.

**Tempting mistake:** Patching the elementwise result with `rowSums(design * beta)`. It returns a plausible-looking 8 and 15, but those are not the predictions.

**Verify:** The matrix product returns 11 and 14, while `rowSums(design * beta)` returns 8 and 15 for the same inputs.

### Exercise 5

Retain one selected column as a matrix.

Use drop=FALSE and test dim.

**Approach:** Extract with `design[, 1, drop = FALSE]` and test the dimensions of the result.

**Why it holds here:** The intercept column is one column of two rows. Keeping it as a matrix means later matrix code still sees a 2 by 1 object.

**Tempting mistake:** Writing `design[, 1]`. R simplifies to the vector 1, 1, `dim()` becomes NULL, and `nrow()` of it returns NULL.

**Verify:** The reference asserts `identical(dim(one), c(2L, 1L))`, so `nrow(one)` returns 2 rather than NULL.

### Exercise 6

Explain why a residual check is useful after solve.

A small residual supports this numerical solution but does not by itself establish good conditioning or correct model assumptions.

**Approach:** After `solve(a, b)`, substitute the solution back and measure the largest absolute residual.

**Why it holds here:** For `diag(c(2, 4))` and b = 6, 8, the solution is 3 and 2, and multiplying back reproduces b exactly. The check tests the returned numbers against the equation itself.

**Tempting mistake:** Treating a tiny residual as proof the coefficients are trustworthy. A nearly singular matrix can return a solution with a small residual that changes wildly when b moves slightly, and the check says nothing about whether the model is right.

**Verify:** The residual value here is 0, below the 1e-12 threshold; `kappa(a, exact = TRUE)` returns 2, showing this system is well conditioned.

## What the checks establish

The checks pin column-major filling with a first row of 1, 3 and 5, `byrow = TRUE` giving 1, 2 and 3, an intercept design that predicts 11 and 14 from intercept 2 and slope 3 at x of 3 and 4, `drop = FALSE` keeping a 2 by 1 shape, and a solved system whose residual stays below 1e-12. They do not test conditioning for larger or nearly singular matrices.

The reference makes 5 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
