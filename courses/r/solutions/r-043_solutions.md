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

### Exercise 2

Predict at x=5 and label its support relative to training.

The fitted value is 10; this is extrapolation beyond the observed predictor range.

**Expected evidence:** Prediction 10 with an explicit extrapolation qualification.

### Exercise 3

Fit y~x*group to two exact group lines A:1+2x and B:4+x.

Coefficients are intercept 1, x = 2, group B coefficient 3 and interaction-1 under the declared reference coding.

**Expected evidence:** Correct group-specific slopes 2 and 1.

### Exercise 4

Add double_x=2*x and diagnose y~x+double_x.

The design is rank deficient and at least one coefficient is aliased; fitted values do not identify both slopes uniquely.

**Expected evidence:** Rank below column count and an NA coefficient.

### Exercise 5

Check residual orthogonality for the simple fit.

The result is approximately zero for the fitted least-squares projection. It is not a proof of independent errors.

**Expected evidence:** Two near-zero normal-equation residuals.

### Exercise 6

Explain why the prediction interval is wider than the mean confidence interval.

A new response includes residual outcome variation; uncertainty in its mean alone omits that variation.

**Expected evidence:** Correct target distinction and matched-point comparison.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
