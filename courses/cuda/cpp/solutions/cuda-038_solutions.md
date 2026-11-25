# cuda-038: explanatory solutions

## Mechanism review

A defensible benchmark holds the problem contract fixed while changing one implementation decision. Record dtype, layout, supported shapes, numerical tolerance, data residency and required output. Compare against a competent baseline, not a deliberately poor CPU loop. Retain cold and warm measurements separately, avoid reporting only the fastest observation, and disclose device sharing, clocks and thermal conditions when relevant. A performance regression can coexist with improved kernel time if another phase grows. Report uncertainty and supported scope; no universal speed threshold is valid across every GPU and workload.

## Exercise 1

Baseline times are \([10,11,10,9,10]\) ms and candidate times \([8,8,9,8,7]\) ms. Median ratio is \(\frac{10}{8}=1.25\). This suggests an improvement for the measured fixture, but five synthetic samples do not establish stability across hardware, sizes or operating conditions.

**Approach:** Take the median of each sample set and divide 10 by 8.

**Why it is correct:** Medians of 10 ms and 8 ms give 1.25 for this fixture.

**A plausible wrong approach:** Claiming a general 25 percent improvement from five synthetic samples overstates what they show.

**How to verify:** The reference asserts the median speedup equals 1.25.

## Exercise 2

A candidate uses float16 while the baseline uses float64. It may legitimately target a different accuracy budget, but it is not a like-for-like implementation comparison until both satisfy the same required error contract. Include conversion cost if the application supplies and consumes another dtype.

**Approach:** Hold both versions to the same error contract before comparing speed.

**Why it is correct:** float16 changes accuracy and conversion cost, so its speed is a different trade.

**A plausible wrong approach:** Reporting float16 against float64 as a like-for-like speedup hides the accuracy loss.

**How to verify:** Measure error against a reference for both and include conversions in timing.

## Exercise 3

Specify exact input generation, dtype/layout, accumulation, alpha/beta semantics, output tolerance, residency, setup inclusion and sample policy.

**Approach:** List input generation, dtype, layout, accumulation, alpha and beta, tolerance, residency, setup and sampling.

**Why it is correct:** Each item changes the work or result, so all must match between versions.

**A plausible wrong approach:** Writing only the matrix size lets two runs differ in dtype or layout.

**How to verify:** Give the contract to another person and check they produce the same benchmark.

## Exercise 4

Apply the same summary policy to both and retain all raw samples; investigate outliers without selectively deleting them.

**Approach:** Apply one summary statistic to both sides and keep every raw sample.

**Why it is correct:** Minimum against median compares different statistics and inflates the speedup.

**A plausible wrong approach:** Dropping baseline outliers while keeping candidate ones biases the result.

**How to verify:** Recompute with medians on both sides and publish samples.

## Exercise 5

They expose launch overhead and boundary inefficiencies that a single large aligned workload conceals.

**Approach:** Add tiny and ragged shapes next to the large aligned one.

**Why it is correct:** Small shapes reveal launch overhead and ragged ones reveal tail handling.

**A plausible wrong approach:** Testing only 1,024 aligned sizes hides costs real requests pay.

**How to verify:** Report each shape's time separately and check correctness for all.

## Exercise 6

Ship only if it satisfies a documented application error budget and supported-input policy, with a fallback or rejection outside that contract.

**Approach:** Ship only if error stays within a documented budget, with a fallback outside it.

**Why it is correct:** Users need a promise about accuracy, not only speed.

**A plausible wrong approach:** Shipping because typical inputs look fine leaves edge inputs unprotected.

**How to verify:** Test inputs at the edge of the supported range against the budget.

## Self-check answers

1. **Why compare medians rather than the fastest run of each version?** The median resists outliers and reflects typical behavior; the minimum rewards luck.
2. **What makes a CPU baseline competent?** It uses a reasonable algorithm, optimization flags and threading for the same problem contract.
3. **Why record thermal state and device sharing?** Clocks drop when hot and shared devices add interference, so timings may not repeat elsewhere.

## Numerical reference and its limits

The [CPU reference](../references/cuda-038_cpu.py) reproduces worked example 1 and prints `{'synthetic_median_speedup': 1.25, 'baseline_samples_ms': [10, 11, 10, 9, 10], 'candidate_samples_ms': [8, 8, 9, 8, 7]}`.

## Transfer review

Ship only if it satisfies a documented application error budget and supported-input policy, with a fallback or rejection outside that contract.
