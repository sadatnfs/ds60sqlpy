# r-038: reference reasoning

Use the [complete reference](r-038_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

Thirty of one hundred A records are alerted, while thirty of forty alerted records are A. Both calculations are correct for different questions.

The total alert probability combines both segments. Bayes rule reconstructs the same finite-table conditional rather than introducing new observations.

## Explained practice

### Exercise 1

Identify the denominator for P(A given alert).

The denominator is 40 in the supplied table.

**Approach:** Restrict to the alerted records first: the yes column, then divide A's alerted count by that column total.

**Why it holds here:** The yes column holds 30 A records and 10 B records, so the denominator is 40 and P(A given alert) is 30/40 = 0.75.

**Tempting mistake:** Dividing by A's row total of 100, which gives 0.3, the probability of an alert given A, or by all 200 records, which gives 0.15, the joint probability.

**Verify:** `sum(counts[, 1])` returns 40, and `counts[1, 1] / sum(counts[, 1])` returns 0.75.

### Exercise 2

Change the A base rate to 0.2 with alert rates unchanged.

P(alert)=0.14 and P(A given alert)=3/7.

**Approach:** Recompute the total alert probability with the new base rate, then apply Bayes' rule.

**Why it holds here:** With P(A) = 0.2, P(alert) is 0.3 times 0.2 plus 0.1 times 0.8, which is 0.06 + 0.08 = 0.14. The posterior is 0.06/0.14 = 3/7, about 0.429.

**Tempting mistake:** Keeping the old P(alert) of 0.2. That gives 0.06/0.2 = 0.3, which mixes the new base rate with the old alert mix and matches no consistent population.

**Verify:** `isTRUE(all.equal(p_alert, 0.14))` and `isTRUE(all.equal(0.3 * p_a / p_alert, 3 / 7))` both return TRUE.

### Exercise 3

Construct joint probabilities from the count table.

The four cells sum to one.

**Approach:** Divide every cell by the grand total of 200 so that the four cells form one joint distribution.

**Why it holds here:** The matrix is filled by row, so the cells are A yes 30, A no 70, B yes 10 and B no 90. Divided by 200 they become 0.15, 0.35, 0.05 and 0.45, which add to 1.

**Tempting mistake:** Using `prop.table(counts, 1)`, which divides by row totals. Each row then sums to one and the four cells sum to 2, so the result is two conditional distributions, not a joint one.

**Verify:** `isTRUE(all.equal(sum(joint), 1))` returns TRUE, and `joint[1, 1]` returns 0.15.

### Exercise 4

Diagnose swapping P(alert given A) with P(A given alert).

Keep event and conditioning event explicit in names and denominators.

**Approach:** Name each quantity by its event and its condition, such as alert_given_a, and compute it with the matching denominator.

**Why it holds here:** In this table the two directions differ by a factor of 2.5: 0.3 conditions on segment A, 0.75 conditions on the alert. Names and denominators that state the condition keep them from being swapped.

**Tempting mistake:** Writing that 75 percent of A records trigger an alert. Only 30 of A's 100 records did; 75 percent is A's share of the 40 alerts.

**Verify:** `conditional(30, 100) != conditional(30, 40)` returns TRUE, since the two calls return 0.3 and 0.75.

### Exercise 5

Handle a conditioning event with zero count.

Return a missing result or reject the query under a stated policy.

**Approach:** Check the conditioning count before dividing and return NA_real_ when it is zero.

**Why it holds here:** A segment with no records has no alert rate; there is nothing to condition on. In R, 0/0 is NaN and 30/0 is Inf, and neither is a probability.

**Tempting mistake:** Returning 0 for an empty segment. That would claim the segment never alerts when it has simply not been observed, and averaging it with other segments would pull rates down.

**Verify:** `is.na(conditional(0, 0))` returns TRUE, while `conditional(30, 100)` returns 0.3.

### Exercise 6

Explain the limit of exporting these proportions to a new population.

Assess sampling, base rates and stable conditional mechanisms before generalizing.

**Approach:** Before applying these proportions elsewhere, check how the 200 records were sampled and what the target population's base rate is.

**Why it holds here:** Here A and B have 100 records each. If the new population is 5 percent A, the same alert rates give P(A given alert) of about 0.136, not 0.75, and the alert rates themselves may differ if the alert rule or behavior differs.

**Tempting mistake:** Applying 0.75 to the new population as though the share of A were a fixed property of alerts.

**Verify:** Computing `0.3 * 0.05 / (0.3 * 0.05 + 0.1 * 0.95)` returns about 0.136.

## What the checks establish

The reference makes 5 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
