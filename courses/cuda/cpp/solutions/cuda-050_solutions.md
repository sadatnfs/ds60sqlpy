# cuda-050: explanatory solutions

## Mechanism review

Parallel random-number generation needs a reproducible mapping from logical samples to independent streams or subsequences. Giving every thread identical initial state can repeat the same draws and destroy effective sample size. A seed identifies an experiment, but the generator, stream partition and sample-count mapping are also part of it. Monte Carlo error is sampling uncertainty, distinct from floating-point error or a bug. Increasing independent sample count usually reduces standard error at a square-root rate. RNG initialization can be expensive, so report setup separately from sustained generation when evaluating performance.

## Exercise 1

Estimate the integral of x squared on \([0,1]\) by averaging squared uniform samples. The exact answer is one third. A fixed CPU seed produces a reproducible educational estimate; its closeness is not evidence about cuRAND or independent GPU streams. Keep a broad deterministic sanity check separate from statistical claims.

**Approach:** Average squared uniform draws from a fixed CPU seed to estimate the integral of x squared on [0, 1].

**Why it is correct:** The expectation of U squared is one third, and 10,000 samples land near it.

**A plausible wrong approach:** Treating a close CPU estimate as validation of cuRAND confuses one generator's result with another's.

**How to verify:** The reference asserts the estimate is within 0.03 of 1 / 3 and prints 0.3322 for seed 7.

## Exercise 2

Four workers initialized with exactly the same stream each draw \([0.1,0.7]\). Concatenating gives eight entries but only two distinct draws repeated four times. Treating them as eight independent observations understates uncertainty. A correct design gives workers nonoverlapping documented subsequences.

**Approach:** Give each worker a distinct subsequence or seed so draws do not repeat.

**Why it is correct:** Four copies of [0.1, 0.7] hold two distinct values, so eight entries carry two observations of information.

**A plausible wrong approach:** Counting eight samples in the standard error understates uncertainty by treating repeats as independent.

**How to verify:** The reference asserts the repeated list has length 8 but only 2 distinct values.

## Exercise 3

It is approximately halved under the usual finite-variance assumptions, not divided by four.

**Approach:** Divide the standard error by the square root of four.

**Why it is correct:** Standard error scales as one over the square root of n, so it halves.

**A plausible wrong approach:** Dividing by four assumes error falls linearly with sample count.

**How to verify:** Compare estimated standard errors at n and 4n from a fixed generator.

## Exercise 4

No. Different generators or stream mappings need not produce identical draws. Compare stated reproducibility and statistical contracts.

**Approach:** Compare the GPU result statistically rather than draw by draw.

**Why it is correct:** Different generators or stream mappings legitimately produce different sequences.

**A plausible wrong approach:** Demanding identical numbers to a seeded CPU run rejects a valid GPU generator.

**How to verify:** Check the GPU estimate falls within the expected interval around one third.

## Exercise 5

An undefined-estimate status rather than division by zero or a false estimate of zero.

**Approach:** Return an undefined-estimate status when the sample count is zero.

**Why it is correct:** A mean of no samples is undefined.

**A plausible wrong approach:** Returning 0 claims an estimate that no data supports.

**How to verify:** Call with zero samples and assert the status.

## Exercise 6

Record generator/version, seed, subsequence assignment, sample count, estimator, uncertainty calculation and numeric precision.

**Approach:** Record generator and version, seed, subsequence mapping, sample count, estimator, error formula and precision.

**Why it is correct:** These fields let someone rerun and judge the estimate.

**A plausible wrong approach:** Recording only the final number makes the run impossible to reproduce or assess.

**How to verify:** Rerun from the receipt and confirm the same estimate.

## Self-check answers

1. **How much does standard error shrink with 100 times more independent samples?** By a factor of 10, the square root of 100.
2. **What is the exact value targeted in worked example 1?** One third, the integral of x squared from 0 to 1.
3. **What should a Monte Carlo receipt record besides the seed?** The generator, stream partition, sample count and the estimate with its standard error.

## Numerical reference and its limits

The [CPU reference](../references/cuda-050_cpu.py) reproduces worked example 1 and prints `{'CPU_integral_estimate': 0.3322235056104499, 'exact_integral': 0.3333333333333333, 'duplicated_stream_unique_draws': 2}`.

## Transfer review

Record generator/version, seed, subsequence assignment, sample count, estimator, uncertainty calculation and numeric precision.
