# r-044: reference reasoning

Use the [complete reference](r-044_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The two-column response retains successes and failures as trial counts. The exact fixture probabilities make link-scale and odds calculations independently checkable. Brier score and classification accuracy evaluate different properties of those same predictions.

The separation example is diagnosed from the geometry of its inputs rather than forcing an unstable fit and presenting a huge coefficient as a valid estimate. The held-out frequency comparison uses new outcomes and remains a descriptive calibration check with its count visible. It does not infer population calibration from two bins.

## Explained practice

### Exercise 1

Fit the two-group binomial model and reconstruct probabilities from the link scale.

The fitted probabilities are 0.2 and 0.6; inverse-link predictions agree with response predictions.

**Expected evidence:** Two matching probability paths.

**Approach:** Fit glm with cbind(successes, failures) on the left, take the link scale predictions and apply plogis.

**Why it holds here:** The groups have 2 of 10 and 6 of 10 successes, so the fitted probabilities are 0.2 and 0.6 and the log odds are log(0.25), about -1.39, and log(1.5), about 0.41. plogis inverts the logit, so both routes give the same two numbers.

**Tempting mistake:** Applying exp to the link scale. That returns the odds 0.25 and 1.5, and 1.5 cannot be a probability, so the mix up is visible at x = 1.

**Verify:** `max(abs(plogis(predict(fit, type = "link")) - p))` returns a value below 1e-10.

### Exercise 2

Interpret the x coefficient as an odds ratio.

Odds are 0.25 and 1.5, so their ratio is 6. The probability ratio is 3, a different quantity.

**Expected evidence:** Odds ratio 6, probability ratio 3.

**Approach:** Convert each probability to odds, p / (1 - p), and divide the x = 1 odds by the x = 0 odds.

**Why it holds here:** The odds are 0.2/0.8 = 0.25 and 0.6/0.4 = 1.5, so the ratio is 6, which equals exp of the x coefficient log(6), about 1.79. The probability ratio is 0.6/0.2 = 3.

**Tempting mistake:** Saying x = 1 makes success six times as likely. Success becomes three times as likely; six is the change in the odds, and the two diverge because 0.6 is far from 0.

**Verify:** `odds[2] / odds[1]` returns 6 and `p[2] / p[1]` returns 3, both within 1e-7.

### Exercise 3

Calculate the trial-weighted Brier score.

Successes contribute (1-p)^2 and failures p^2; their sum over 20 trials gives 0.2.

**Expected evidence:** Brier 0.2.

**Approach:** Score each trial separately: a success adds (1 - p)^2, a failure adds p^2, and the sum is divided by the 20 trials.

**Why it holds here:** At x = 0 the 2 successes add 2 times 0.64 = 1.28 and the 8 failures add 8 times 0.04 = 0.32. At x = 1 the 6 successes add 6 times 0.16 = 0.96 and the 4 failures add 4 times 0.36 = 1.44. The total is 4, and 4/20 = 0.2.

**Tempting mistake:** Squaring the gap between each fitted probability and its group rate. Both gaps are 0 because the fit reproduces 0.2 and 0.6, so that score hides the outcome variation that the Brier score measures.

**Verify:** `n == 20` returns TRUE and `abs(brier - 0.2) < 1e-10` returns TRUE.

### Exercise 4

Diagnose treating the proportions 0.2 and 0.6 as two equally weighted binary observations.

The aggregation represents 20 Bernoulli trials. Losing the denominators changes the likelihood and uncertainty interpretation.

**Expected evidence:** Trial count 20 retained.

**Approach:** Keep each group's 10 trials in the response through the two column form or through prior weights.

**Why it holds here:** Each row summarizes 10 Bernoulli trials, so the likelihood counts 20 outcomes. With 2 parameters for 2 groups the point estimates match the rates either way, but the standard errors depend on the trial count.

**Tempting mistake:** Fitting the proportions as one trial each, such as `glm(rate ~ x, family = binomial())` without weights. R warns about non-integer successes, the coefficients stay at log(0.25) and log(6), and the standard errors grow by `sqrt(10)`, about 3.16.

**Verify:** `sum(d$successes + d$failures)` returns 20.

### Exercise 5

Recognize complete separation for x=c(-2,-1,1,2) and y=c(0,0,1,1).

A threshold at zero separates all outcomes. An unpenalized logistic fit can lack a finite optimum; a numerical convergence flag alone is insufficient.

**Expected evidence:** Separation identified without inventing finite coefficient evidence.

**Approach:** Before fitting, check whether a cut on x separates the outcomes completely.

**Why it holds here:** In x = -2, -1, 1, 2 with y = 0, 0, 1, 1, every 0 sits below zero and every 1 above it. A steeper logistic curve always fits these four points better, so the likelihood has no finite maximum.

**Tempting mistake:** Running glm anyway and reporting the large slope and its huge standard error as an estimate. R warns that fitted probabilities are numerically 0 or 1, and a converged flag can still be TRUE, so the flag says nothing about a finite optimum.

**Verify:** `all(x_sep[y_sep == 0] < 0)` and `all(x_sep[y_sep == 1] > 0)` both return TRUE.

### Exercise 6

Assess held-out group outcomes 1/10 and 8/10 under predictions 0.2 and 0.6.

The observed-minus-predicted gaps are -0.1 and 0.2. Their weighted absolute gap is 0.15 for equal counts; uncertainty and binning choices remain relevant.

**Expected evidence:** Held-out gaps and denominator reported.

**Approach:** Subtract the training predictions from the new rates, 1/10 and 8/10, and report the absolute gaps with their 10 trial counts.

**Why it holds here:** 0.1 - 0.2 = -0.1 and 0.8 - 0.6 = 0.2. With equal group sizes the mean absolute gap is 0.15, and 10 outcomes per group are few enough that a gap of 0.1 or 0.2 is weak evidence.

**Tempting mistake:** Comparing the predictions with the training rates 0.2 and 0.6, which shows zero gaps because the model fit those rates. Averaging the signed gaps is a second error: -0.1 and 0.2 average to 0.05, which hides that one group is overpredicted and the other underpredicted.

**Verify:** The largest gap between `gaps` and c(-0.1, 0.2) returns a value below 1e-8, and `mean(abs(gaps))` returns 0.15.

## What the checks establish

The reference makes 6 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
