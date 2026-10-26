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

### Exercise 2

Interpret the x coefficient as an odds ratio.

Odds are 0.25 and 1.5, so their ratio is 6. The probability ratio is 3, a different quantity.

**Expected evidence:** Odds ratio 6, probability ratio 3.

### Exercise 3

Calculate the trial-weighted Brier score.

Successes contribute (1-p)^2 and failures p^2; their sum over 20 trials gives 0.2.

**Expected evidence:** Brier 0.2.

### Exercise 4

Diagnose treating the proportions 0.2 and 0.6 as two equally weighted binary observations.

The aggregation represents 20 Bernoulli trials. Losing the denominators changes the likelihood and uncertainty interpretation.

**Expected evidence:** Trial count 20 retained.

### Exercise 5

Recognize complete separation for x=c(-2,-1,1,2) and y=c(0,0,1,1).

A threshold at zero separates all outcomes. An unpenalized logistic fit can lack a finite optimum; a numerical convergence flag alone is insufficient.

**Expected evidence:** Separation identified without inventing finite coefficient evidence.

### Exercise 6

Assess held-out group outcomes 1/10 and 8/10 under predictions 0.2 and 0.6.

The frequency gaps are-0.1 and 0.2. Their weighted absolute gap is 0.15 for equal counts; uncertainty and binning choices remain relevant.

**Expected evidence:** Held-out gaps and denominator reported.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
