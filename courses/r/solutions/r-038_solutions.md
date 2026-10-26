# r-038: reference reasoning

Use the [complete reference](r-038_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

Thirty of one hundred A records are alerted, while thirty of forty alerted records are A. Both calculations are correct for different questions.

The total alert probability combines both segments. Bayes rule reconstructs the same finite-table conditional rather than introducing new observations.

## Explained practice

### Exercise 1

Identify the denominator for P(A given alert).

The denominator is 40 in the supplied table.

**Expected evidence:** The denominator is 40 in the supplied table.

### Exercise 2

Change the A base rate to 0.2 with alert rates unchanged.

P(alert)=0.14 and P(A given alert)=3/7.

**Expected evidence:** P(alert)=0.14 and P(A given alert)=3/7.

### Exercise 3

Construct joint probabilities from the count table.

The four cells sum to one.

**Expected evidence:** The four cells sum to one.

### Exercise 4

Diagnose swapping P(alert given A) with P(A given alert).

Keep event and conditioning event explicit in names and denominators.

**Expected evidence:** Keep event and conditioning event explicit in names and denominators.

### Exercise 5

Handle a conditioning event with zero count.

Return a missing result or reject the query under a stated policy.

**Expected evidence:** Return a missing result or reject the query under a stated policy.

### Exercise 6

Explain the limit of exporting these proportions to a new population.

Assess sampling, base rates and stable conditional mechanisms before generalizing.

**Expected evidence:** Assess sampling, base rates and stable conditional mechanisms before generalizing.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
