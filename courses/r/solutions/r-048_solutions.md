# r-048: reference reasoning

Run the [complete reference](r-048_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The exact Kaplan-Meier oracle checks event coding and risk-set arithmetic. The changed-status case supplies a meaningful negative comparison: the same times produce a different survival curve when a censor is incorrectly declared an event.

The Cox fit and its proportional-hazards diagnostic are actual package operations on a synthetic fixture. Their interpretation remains conditional on the event definition, censoring assumptions and model. Finite coefficients and diagnostic output do not turn the example into a validated prediction system.

## Explained practice

### Exercise 1

Reconstruct the four-record Kaplan-Meier steps.

The factors at event times are 3/4,1/2 and 0; the censor creates no survival drop.

**Expected evidence:** 0.75,0.75,0.375,0 at times 1:4.

**Approach:** Walk the four times in order, multiplying survival by one minus events over the number at risk at each event time.

**Why it holds here:** At time 1, 4 are at risk and 1 fails, giving 3/4. The censor at time 2 removes one record without a drop. At time 3, 2 remain and 1 fails, giving 3/4 times 1/2 = 3/8. At time 4 the last record fails, giving 0.

**Tempting mistake:** Dividing events by the original 4 at every step. That gives 3/4, then 2/4 and 1/4, which ignores that the censored record had already left the risk set.

**Verify:** `summary(km, times = 1:4)$surv` returns 0.75, 0.75, 0.375 and 0 within 1e-12.

### Exercise 2

Treat the censor at time two as an event and compare the resulting curve.

The curve drops to 0.5 at time two instead of staying 0.75, showing that event coding changes the target.

**Expected evidence:** Different second-time survival.

**Approach:** Copy the data, set only `event[2]` to 1, refit, and read survival at time 2.

**Why it holds here:** As an event, time 2 has 3 at risk and 1 failure, so survival falls to 3/4 times 2/3 = 1/2. The same times now answer a different question because the coding changed what counts as failure.

**Tempting mistake:** Treating censoring as a detail that barely moves the curve. Here it moves survival at time 2 from 0.75 to 0.5, and at time 3 from 0.375 to 0.25.

**Verify:** `summary(wrong, times = 2)$surv` returns 0.5 within 1e-12.

### Exercise 3

Validate an event column before creating Surv.

Reject values outside 0/1 under this lesson contract. Other survival encodings require a different explicit specification.

**Expected evidence:** Invalid event code rejected.

**Approach:** Check that the event column has no NA and contains only 0 and 1 before building Surv.

**Why it holds here:** This lesson defines 1 as an observed event and 0 as censored. Any other value, such as the 2 in c(0, 2), cannot be read under that contract, so the validator stops.

**Tempting mistake:** Passing the column straight to Surv. Surv also accepts 1/2 coding, in which 1 means censored, so a column of 1s and 2s would be read with a meaning the lesson never declared.

**Verify:** `inherits(try(validate_event(c(0, 2)), silent = TRUE), "try-error")` returns TRUE.

### Exercise 4

Fit the Cox fixture and convert its coefficient to a hazard ratio.

The ratio is positive and finite for this fixture; it is not a ratio of survival probabilities or a causal estimate by itself.

**Expected evidence:** Correctly labeled coefficient and hazard ratio.

**Approach:** Fit coxph on the 12 record fixture, take coef(fit) as the log hazard ratio for group 1 against group 0, and exponentiate it.

**Why it holds here:** Group 0 has 5 events in 6 records and group 1 has 3 events with 3 censors. Solving the partial likelihood by hand gives a coefficient near -0.56 and a hazard ratio near 0.57, with a standard error near 0.74, so the data also fit a ratio of 1.

**Tempting mistake:** Reading 0.57 as group 1's survival probability relative to group 0's. It compares instantaneous event rates among those still at risk, and the survival curves differ by a nonconstant amount.

**Verify:** `all(is.finite(coef(fit)))` returns TRUE, and `exp(coef(fit))` returns a single positive value near 0.57.

### Exercise 5

Inspect cox.zph output without turning its p-value into proof of proportional hazards.

The test supplies model-diagnostic evidence; a small synthetic sample cannot establish the assumption universally.

**Expected evidence:** A finite diagnostic table with bounded interpretation.

**Approach:** Run cox.zph on the fit and read the group and GLOBAL rows as a diagnostic with stated limits.

**Why it holds here:** The test asks whether scaled Schoenfeld residuals drift with time. With 8 events in 12 records it has little power, so a large p value only says that no drift was detected here.

**Tempting mistake:** Writing that proportional hazards is proven because p is above 0.05. A sample this small would also miss many real violations, so absence of evidence is all it shows.

**Verify:** `all(is.finite(diagnostic$table))` returns TRUE and `"GLOBAL" %in% rownames(diagnostic$table)` returns TRUE.

### Exercise 6

Explain why averaging observed event times after dropping censored rows changes the analysis.

Dropping censored rows conditions on event observation and discards their at-risk exposure. It is not a substitute for the declared survival analysis.

**Expected evidence:** Selection and risk-set consequences stated.

**Approach:** Keep the censored record in the analysis so it contributes to every risk set until time 2.

**Why it holds here:** In the four record fixture the record censored at time 2 survived past time 1, so it belongs in the denominator at time 1. Kaplan-Meier uses that partial exposure; a plain average of event times cannot.

**Tempting mistake:** Dropping the censored row and averaging 1, 3 and 4 to get about 2.67. The curve on the remaining 3 rows becomes 2/3, 1/3 and 0, lower than 3/4, 3/8 and 0, because a known survivor vanished.

**Verify:** `sum(d$event)` returns 3 against `nrow(d)` of 4, which shows one record would be lost by dropping censored rows.

## What the checks establish

The checks confirm survival of 0.75, 0.75, 0.375 and 0 at times 1 to 4, a wrong analysis that treats the censored time as an event and drops to 0.5 at time 2, rejection of an event code of 2, finite Cox coefficients with positive hazard ratios, a proportional hazards diagnostic with a GLOBAL row, and three events among four rows. They do not show that the proportional hazards assumption holds for real data.

The reference makes 6 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
