# r-037: reference reasoning

Use the [complete reference](r-037_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

There are four ways to obtain exactly three heads and one way to obtain four, among sixteen equally likely sequences. The simulation approximates that model probability.

Quadrupling independent repetitions halves this standard error. It does not imply that a biased real-world model becomes correct.

## Explained practice

### Exercise 1

Derive the probability of at least three heads in four fair flips.

It is 5/16.

**Approach:** Count the sequences with exactly three heads and with four heads, then divide by all sequences.

**Why it holds here:** Three heads can occur in choose(4, 3) = 4 orders and four heads in 1, so 5 of 2^4 = 16 equally likely sequences qualify, which is 0.3125 for a fair coin.

**Tempting mistake:** Using `pbinom(3, 4, 0.5, lower.tail = FALSE)` or `heads > 3`. Both describe more than three heads and give 1/16, which leaves out the four sequences with exactly three.

**Verify:** `sum(choose(4, 3:4)) / 2^4` returns 0.3125, and the worked example's table shows 4 and 1 sequences for three and four heads.

### Exercise 2

Quadruple the number of independent simulation repetitions.

The standard error is halved under the same model.

**Approach:** Compute the standard error at 100 and at 400 repetitions with p = 0.3 and compare the two.

**Why it holds here:** The error is the square root of p(1 - p)/B. Multiplying B by 4 divides the quantity under the root by 4, so the error halves, from about 0.0458 to about 0.0229.

**Tempting mistake:** Expecting the error to fall to a quarter. That is what happens to the variance; the standard error only halves, so cutting it to a quarter takes 16 times the repetitions.

**Verify:** `isTRUE(all.equal(large, small / 2))` returns TRUE, and the printed values show about 0.0458 and 0.0229.

### Exercise 3

Simulate an event and retain seed, B, estimate and error estimate.

The report states both the model and finite-repetition uncertainty.

**Approach:** Keep the event indicator `heads >= 3` as its own step and report the seed, B, estimate and mcse together.

**Why it holds here:** With seed 41 and 20000 draws the mcse is about 0.0033, so the estimate is a value near 0.3125 with a stated precision, and anyone can rerun it and get the same number.

**Tempting mistake:** Reporting the estimate alone, for example 0.31. A reader cannot tell whether that came from 100 draws, with an error near 0.046, or from 20000.

**Verify:** Running `set.seed(41)` and the same rbinom call twice returns identical estimates, and the printed vector shows estimate, exact and mcse.

### Exercise 4

Diagnose choosing a seed because it produces a desired conclusion.

Fix a declared seed policy and evaluate the model honestly.

**Approach:** Fix the seed before looking at any results, and judge the model with a tolerance wider than the simulation noise.

**Why it holds here:** Seeds only change which draws are made. Across seeds the estimate varies by about 0.0033, so trying 20 seeds and keeping the one closest to a hoped for value can shift the answer by roughly two standard errors.

**Tempting mistake:** Running several seeds and reporting the one that gives the preferred estimate. The reported precision then overstates what the simulation supports.

**Verify:** Running seeds 1 to 20 shows estimates spread over a few thousandths around 0.3125, and the declared seed's result falls inside that range.

### Exercise 5

Explain p equal to zero or one.

The model-based Monte Carlo variance is zero, which is not proof that an uncertain real-world probability is known exactly.

**Approach:** Treat p = 0 and p = 1 as degenerate models whose draws do not vary, and say that the zero error is a property of the model.

**Why it holds here:** With p = 0 every draw is 0 heads and with p = 1 every draw is 4, so p(1 - p) = 0 and the mcse is 0 exactly.

**Tempting mistake:** Reporting a real probability as known exactly because the simulation shows no variation. If p were 0.001 and only 100 draws were made, most runs would also show zero events and a zero error.

**Verify:** `all(rbinom(10, 4, 0) == 0)` and `all(rbinom(10, 4, 1) == 4)` both return TRUE.

### Exercise 6

Separate more simulation from better scientific assumptions.

Increasing B reduces simulation noise but does not remove misspecification or observational bias.

**Approach:** Separate the simulation error, which more draws reduce, from model error, which comes from the fair, independent flips assumption.

**Why it holds here:** If the real coin lands heads 55 percent of the time, three or more heads has probability about 0.391, not 0.3125. That gap of about 0.078 is more than 20 times the mcse.

**Tempting mistake:** Running 2 million draws and reporting 0.3125 as settled. The simulation error shrinks to about 0.0003, while the error from assuming a fair coin stays the same.

**Verify:** `sum(dbinom(3:4, 4, 0.55))` returns about 0.391, while the fair coin model returns 0.3125.

## What the checks establish

The reference makes 5 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
