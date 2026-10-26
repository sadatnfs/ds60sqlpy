# r-048: reference reasoning

Use the [complete reference](r-048_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The exact Kaplan-Meier oracle checks event coding and risk-set arithmetic. The changed-status case supplies a meaningful negative comparison: the same times produce a different survival curve when a censor is incorrectly declared an event.

The Cox fit and its proportional-hazards diagnostic are actual package operations on a synthetic fixture. Their interpretation remains conditional on the event definition, censoring assumptions and model. Finite coefficients and diagnostic output do not turn the example into a validated prediction system.

## Explained practice

### Exercise 1

Reconstruct the four-record Kaplan-Meier steps.

The factors at event times are 3/4,1/2 and 0; the censor creates no survival drop.

**Expected evidence:** 0.75,0.75,0.375,0 at times 1:4.

### Exercise 2

Treat the censor at time two as an event and compare the resulting curve.

The curve drops to 0.5 at time two instead of staying 0.75, showing that event coding changes the target.

**Expected evidence:** Different second-time survival.

### Exercise 3

Validate an event column before creating Surv.

Reject values outside 0/1 under this lesson contract. Other survival encodings require a different explicit specification.

**Expected evidence:** Invalid event code rejected.

### Exercise 4

Fit the Cox fixture and convert its coefficient to a hazard ratio.

The ratio is positive and finite for this fixture; it is not a ratio of survival probabilities or a causal estimate by itself.

**Expected evidence:** Correctly labeled coefficient and hazard ratio.

### Exercise 5

Inspect cox.zph output without turning its p-value into proof of proportional hazards.

The test supplies model-diagnostic evidence; a small synthetic sample cannot establish the assumption universally.

**Expected evidence:** A finite diagnostic table with bounded interpretation.

### Exercise 6

Explain why averaging observed event times after dropping censored rows changes the analysis.

Dropping censored rows conditions on event observation and discards their at-risk exposure. It is not a substitute for the declared survival analysis.

**Expected evidence:** Selection and risk-set consequences stated.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
