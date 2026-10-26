# r-056: reference reasoning

Use the [complete reference](r-056_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference keeps diagnostic observations aligned with the fitted model and verifies the actual values supplied to each graphic. It prints one residual plot and one Q-Q plot, staying within the two-figure contract.

The symmetric spread fixture provides an independent example of heteroskedastic structure with the correct mean slope. Its role is explanatory. Diagnostics should guide further checks and sensitivity analysis rather than certify assumptions or justify deleting points without a substantive rule.

## Explained practice

### Exercise 1

Fit the authored linear fixture and retain IDs with fitted values and residuals.

The fit recovers intercept 1 and slope 2, and the diagnostic table has eight aligned records.

**Expected evidence:** Correct coefficients and row identities.

### Exercise 2

Check that the residual plot uses the model's actual residual vector.

Its y coordinates agree with residuals(fit) in the retained row order.

**Expected evidence:** Layer-to-model parity.

### Exercise 3

Construct a normal Q-Q graphic of those residuals.

The layer contains one ordered sample value per residual, with a clearly labeled reference comparison.

**Expected evidence:** Eight Q-Q sample values.

### Exercise 4

Diagnose increasing residual magnitude in the symmetric spread fixture.

The slope can be correct while error spread varies; investigate variance assumptions and uncertainty procedures separately.

**Expected evidence:** A spread concern, not an automatic slope failure.

### Exercise 5

Explain why deleting a visually unusual residual is not an automatic valid repair.

It may represent legitimate variation, a measurement issue or model misspecification. Any exclusion needs an explicit justified policy and sensitivity analysis.

**Expected evidence:** No appearance-only deletion rule.

### Exercise 6

State what a Q-Q plot cannot prove from eight fitted residuals.

The display is diagnostic evidence, not a proof of normal independent errors or of predictive/causal validity.

**Expected evidence:** Bounded interpretation.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
