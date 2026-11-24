# r-043: reference reasoning

Use the [complete reference](r-043_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The design-matrix reconstruction connects formula notation to the actual numerical fit. The interaction example fixes the factor reference level so the coefficient names have a defined interpretation; the two group-specific slopes remain the substantive quantities.

The alias example intentionally separates identifiable fitted values from nonunique parameter coordinates. Residual orthogonality is an algebraic least-squares property, while uncertainty intervals rely on further assumptions. The reference reports extrapolation and interval targets explicitly rather than treating predict as a scientific interpretation engine.

## Explained practice

### Exercise 1

Recover the design matrix for y~x on the five-row fixture.

The first column is all ones and the second is x; multiplying by coefficients reconstructs fitted values.

**Expected evidence:** Shape 5-by 2 and exact prediction reconstruction.

**Approach:** Call model.matrix on the fitted object, confirm a 5 by 2 shape with a column of ones, and multiply it by coef(fit).

**Why it holds here:** With x = 0:4 and y = 1, 3, 4, 7, 8, the centered cross products sum to 18 and the squared x deviations to 10, so the slope is 1.8 and the intercept is 4.6 minus 3.6, which is 1. X times (1, 1.8) gives 1, 2.8, 4.6, 6.4 and 8.2, which are exactly the fitted values.

**Tempting mistake:** Building the matrix from x alone, which amounts to `lm(y ~ x - 1)`. That forces the line through the origin and gives a slope of 64/30, about 2.13, so the products no longer match fitted(fit).

**Verify:** `identical(dim(X), c(5L, 2L))` returns TRUE, and the largest gap between `X %*% coef(fit)` and `fitted(fit)` returns a value below 1e-10.

### Exercise 2

Predict at x=5 and label its support relative to training.

The fitted value is 10; this is extrapolation beyond the observed predictor range.

**Expected evidence:** Prediction 10 with an explicit extrapolation qualification.

**Approach:** Pass data.frame(x = 5) to predict and report the value together with the training range of x.

**Why it holds here:** 1 + 1.8 times 5 is 10. The training x values stop at 4, so this point is one step outside the data, and its leverage, 1/5 + (5 - 2)^2 / 10 = 1.1, is more than five times the 0.2 at the center.

**Tempting mistake:** Presenting 10 with the same confidence as a fitted value inside 0 to 4. Nothing in five points shows that the straight line continues past x = 4.

**Verify:** `predict(fit, data.frame(x = 5))` returns 10 within the 1e-10 tolerance, and `range(d$x)` returns 0 and 4.

### Exercise 3

Fit y~x*group to two exact group lines A:1+2x and B:4+x.

Coefficients are intercept 1, x = 2, group B coefficient 3 and interaction-1 under the declared reference coding.

**Expected evidence:** Correct group-specific slopes 2 and 1.

**Approach:** Set the group factor levels to A then B, fit y ~ x * group and read each coefficient as a difference from A.

**Why it holds here:** Group A follows 1 + 2x and group B follows 4 + x, so with A as reference the intercept is 1, the x slope is 2, groupB is 4 - 1 = 3 and x:groupB is 1 - 2 = -1. Both lines are exact, so the fit recovers them with no residual.

**Tempting mistake:** Reading groupB = 3 as B's intercept or x:groupB = -1 as B's slope. B's intercept is 1 + 3 = 4 and its slope is 2 - 1 = 1, so the raw coefficients are offsets.

**Verify:** The largest gap between `unname(coef(interaction))` and c(1, 2, 3, -1) returns a value below 1e-10.

### Exercise 4

Add double_x=2*x and diagnose y~x+double_x.

The design is rank deficient and at least one coefficient is aliased; fitted values do not identify both slopes uniquely.

**Expected evidence:** Rank below column count and an NA coefficient.

**Approach:** Add double_x = 2 * x, fit y ~ x + double_x, and compare the QR rank of its design with its column count.

**Why it holds here:** The design has 3 columns, intercept, x and double_x, but double_x is an exact multiple of x, so the rank is 2. lm keeps x with slope 1.8, reports NA for double_x and returns the same five fitted values as the simple fit.

**Tempting mistake:** Reading the NA as evidence that double_x has no effect on y. It only means the data cannot split one slope between two copies of the same column; keeping double_x instead of x would give a coefficient of 0.9.

**Verify:** `qr(model.matrix(aliased))$rank` returns 2 against 3 columns, and `anyNA(coef(aliased))` returns TRUE.

### Exercise 5

Check residual orthogonality for the simple fit.

The result is approximately zero for the fitted least-squares projection. It is not a proof of independent errors.

**Expected evidence:** Two near-zero normal-equation residuals.

**Approach:** Compute crossprod(X, residuals(fit)) and check both entries against a small tolerance.

**Why it holds here:** The residuals are 0, 0.2, -0.6, 0.6 and -0.2. The first entry sums them to 0 and the second weights them by x, 0.2 - 1.2 + 1.8 - 0.8 = 0. These are the least squares normal equations, so they hold for any data fitted this way.

**Tempting mistake:** Treating the zero products as evidence that the errors are independent or normally distributed. Testing them with `== 0` is a second trap, because floating point sums can leave values near 1e-16.

**Verify:** `max(abs(crossprod(X, residuals(fit))))` returns a value below 1e-10.

### Exercise 6

Explain why the prediction interval is wider than the mean confidence interval.

A new response includes residual outcome variation; uncertainty in its mean alone omits that variation.

**Expected evidence:** Correct target distinction and matched-point comparison.

**Approach:** Request both intervals at the same point, x = 2, and compare their widths.

**Why it holds here:** Both are centered on 4.6. The residual variance is 0.8 / 3, and the leverage at x = 2 is 0.2, so the mean has standard error sqrt(0.8 / 15), about 0.23, while a new response has sqrt(0.32), about 0.57. With qt(0.975, 3) about 3.18, the widths are about 1.47 and 3.60.

**Tempting mistake:** Comparing the prediction interval at x = 5 with the confidence interval at x = 2. The larger leverage at 5 widens any interval there, so the comparison mixes location with target.

**Verify:** `diff(pi[1, c("lwr", "upr")]) > diff(ci[1, c("lwr", "upr")])` returns TRUE, and both `fit` columns show 4.6.

## What the checks establish

The reference makes 7 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
