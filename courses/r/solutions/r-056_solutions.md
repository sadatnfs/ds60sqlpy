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

**Approach:** Fit lm(y ~ x) and build z from d$id, fitted(fit) and residuals(fit) in the model's own row order.

**Why it holds here:** The authored errors -0.3, 0.2, 0.1, -0.2, 0.4, -0.1, 0.2, -0.3 sum to 0 and their products with x 0 to 7 also sum to 0. They are orthogonal to the intercept and slope, so lm recovers exactly 1 and 2 and each residual equals its authored error.

**Tempting mistake:** Building z with residual = sort(residuals(fit)). The ids stop pointing at their own rows, so id 5, whose residual is 0.4, is paired with 0.1 and any follow up on a flagged id inspects the wrong record.

**Verify:** `nrow(z)` returns 8, `anyDuplicated(z$id)` returns 0, and `unname(coef(fit))` returns 1 and 2 within 1e-10.

### Exercise 2

Check that the residual plot uses the model's actual residual vector.

Its y coordinates agree with residuals(fit) in the retained row order.

**Expected evidence:** Layer-to-model parity.

**Approach:** Map fitted to x and residual to y, add a dashed reference at 0, and compare the built point layer with z$residual.

**Why it holds here:** The residuals here lie between -0.3 and 0.4, so a panel on the residual scale makes their spread around 0 visible, and the comparison confirms the plot draws those values and not a transformed copy.

**Tempting mistake:** Mapping the response y against fitted values instead. y runs from about 0.7 to 14.7, so the errors of a few tenths are swamped and the panel just shows the rising line.

**Verify:** `max(abs(ggplot2::ggplot_build(p)$data[[1]]$y - z$residual))` returns a value below 1e-12.

### Exercise 3

Construct a normal Q-Q graphic of those residuals.

The layer contains one ordered sample value per residual, with a clearly labeled reference comparison.

**Expected evidence:** Eight Q-Q sample values.

**Approach:** Map sample = residual and add stat_qq and stat_qq_line, with axis titles naming the reference quantile and the ordered residual.

**Why it holds here:** stat_qq sorts the eight residuals, -0.3, -0.3, -0.2, -0.1, 0.1, 0.2, 0.2 and 0.4, and pairs them with normal quantiles from about -1.53 to 1.53. The line gives the comparison the eye needs.

**Tempting mistake:** Mapping y = residual for stat_qq. The statistic requires the sample aesthetic and stops with a missing aesthetic error instead of drawing anything.

**Verify:** `nrow(ggplot2::ggplot_build(qq)$data[[1]])` returns 8.

### Exercise 4

Diagnose increasing residual magnitude in the symmetric spread fixture.

The slope can be correct while error spread varies; investigate variance assumptions and uncertainty procedures separately.

**Expected evidence:** A spread concern, not an automatic slope failure.

**Approach:** Fit lm(y ~ x) to the spread fixture f and check the slope and the relation between residual size and fitted value separately.

**Why it holds here:** At each x the two responses are 2x minus x and 2x plus x, so their mean is exactly 2x and the slope is 2. The residuals are plus and minus x, and their size rises in step with the fitted value 2x, which is a variance problem, not a mean problem.

**Tempting mistake:** Adding a quadratic term because the residual plot fans out. The group means lie exactly on 2x, so the squared term contributes nothing while the growing spread, which affects the default standard errors, is left untreated.

**Verify:** `coef(ff)[["x"]]` returns 2, and `cor(abs(residuals(ff)), fitted(ff))` returns 1.

### Exercise 5

Explain why deleting a visually unusual residual is not an automatic valid repair.

It may represent legitimate variation, a measurement issue or model misspecification. Any exclusion needs an explicit justified policy and sensitivity analysis.

**Expected evidence:** No appearance-only deletion rule.

**Approach:** Trace the largest residual, 0.4 at id 5, to its source before deciding anything, and write the exclusion rule down if one is applied.

**Why it holds here:** That value is one of the authored errors from the same process as the others, not a recording mistake. Removing it refits to intercept about 0.96 and slope about 1.99, and id 7 then holds the largest residual, about 0.27, so the same visual rule would call for another deletion.

**Tempting mistake:** Dropping whichever point looks furthest from the dashed line and refitting once. The residual spread shrinks from about 0.28 to about 0.24, which looks like a better model but only reflects lost data.

**Verify:** `coef(lm(y ~ x, data = d[d$id != 5, ]))` returns about 0.96 and 1.99 instead of 1 and 2.

### Exercise 6

State what a Q-Q plot cannot prove from eight fitted residuals.

The display is diagnostic evidence, not a proof of normal independent errors or of predictive/causal validity.

**Expected evidence:** Bounded interpretation.

**Approach:** Report the Q-Q plot as diagnostic evidence for these eight residuals and list what it leaves open.

**Why it holds here:** Residuals from a fitted line are constrained: they sum to 0 and are orthogonal to x, so the eight values carry only six degrees of freedom. Eight points also cannot separate a mild tail difference from chance.

**Tempting mistake:** Concluding from points near the line that the errors are normal and independent and that the model is valid for prediction or causal claims. Dependence and misspecification do not show up in a Q-Q plot.

**Verify:** `sum(z$residual)` and `sum(z$residual * d$x)` both return 0 within rounding error, which shows the constraint.

## What the checks establish

The reference makes 4 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
