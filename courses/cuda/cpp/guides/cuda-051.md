# cuda-051: Softmax and reductions for model workloads

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-020`, `cuda-029`, `cuda-036`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement a numerically stable row softmax and verify finite outputs and row sums against the CPU reference.

**Scope:** Numerically stable softmax, max subtraction, row reductions, normalization and shape-dependent strategies.

**Evidence to produce:** Finite outputs, row sums within justified tolerance and comparison with the CPU reference.

## Purpose, vocabulary and mental model

Softmax converts a row of logits into nonnegative weights that sum to one. Exponentiating large logits directly can overflow even when the final probabilities are ordinary finite values. Subtracting the row maximum preserves the exact mathematical ratios while keeping the largest exponential at one. A kernel needs a maximum reduction, exponentials, a sum reduction and division, with correct row boundaries and accumulation precision. Define behavior for masks and exceptional inputs separately; an all-masked row cannot be treated as an ordinary finite row without a policy. Test short, ragged and extreme-valued rows.

### Key terms

- **Logit:** An unnormalized score that softmax converts into a probability.
- **Max subtraction:** Subtracting the row maximum before exponentiation so no exponent overflows, without changing the softmax result.
- **Row reduction:** A maximum or sum computed across one row, which threads of a block or warp must combine.
- **Overflow:** A value that exceeds the largest representable floating-point number and becomes infinity.

## Mathematical contract

\[
p_i=\frac{e^{z_i-m}}{\sum_j e^{z_j-m}},\qquad m=\max_j z_j
\]

Subtracting one shared row maximum preserves ratios and prevents overflow from a large finite maximum. Exceptional/all-masked rows still need an explicit policy.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-051_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-051_cpu.py
```

## Worked example 1: trace the mechanism

For logits \([1000,1001]\), subtract maximum 1001 to obtain \([-1,0]\). Exponentials are approximately \([0.367879,1]\), giving probabilities \([0.268941,0.731059]\). Directly computing \(e^{1001}\) can overflow in common floating types although the normalized answer is well behaved.

**Why:** Softmax is unchanged by subtracting a constant, and e^-1 / (e^-1 + 1) gives 0.268941 while 1 / (e^-1 + 1) gives 0.731059.

```python
import math


def softmax(values):
    maximum = max(values)
    exp = [math.exp(v - maximum) for v in values]
    return [v / sum(exp) for v in exp]


p = softmax([1000, 1001])
assert abs(sum(p) - 1) < 1e-12 and abs(p[1] - 0.7310585786300049) < 1e-12
assert softmax([4, 4, 4]) == [1 / 3] * 3
print(p)
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
[0.2689414213699951, 0.7310585786300049]
```

**Check:** The reference asserts the sum is within 1e-12 of one and p[1] is within 1e-12 of 0.7310585786300049.

## Worked example 2: change a meaningful condition

For \([4,4,4]\), subtracting four produces three zeros, so each probability is one third. For a single finite logit, the output is one. These cases check normalization and row handling independently of large exponentials.

**Why:** Equal logits subtract to zeros, giving three ones over a sum of three, so each probability is one third; a single logit gives exactly one.

**Check:** The reference asserts softmax([4, 4, 4]) == [1 / 3] * 3; also assert a singleton returns [1.0].

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Subtract the row maximum 1001 from [1000, 1001] to get [-1, 0], exponentiate, and divide by the sum.

**Trap to avoid:** Calling exp(1001) directly overflows to infinity in float32 or float64, and infinity divided by infinity yields NaN.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Run [4, 4, 4] and a single-element row through the same kernel as distinct fixtures.

**Trap to avoid:** Testing only the large-logit case checks overflow handling but not that each row divides by its own sum.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute softmax for \([0,0]\).

**Trap to avoid:** Dividing by the row length instead of the exponential sum gives the same result here and hides that bug.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A row sums to one but entries are in the wrong columns. Why is the test insufficient?

**Trap to avoid:** Adding more rows that check only the sum keeps missing positional errors entirely.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What must an all-masked attention row do?

**Trap to avoid:** Letting the ordinary path run produces NaN that spreads through later layers.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a stable fused softmax contract.

**Trap to avoid:** Timing a fused kernel before testing extreme logits and ragged tails can reward a wrong one.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Replacing the expression with a mathematically equivalent floating-point formula always preserves stability.** Algebraically equal formulas can round and overflow differently. Exponentiating 1001 directly overflows in common types, while subtracting the row maximum keeps every exponential at one or below and gives the same ratios. Treat any rewrite as a new numerical contract and test it with large logits.

## Self-check, retrieval and transfer

1. What is the softmax of [0,0]?
2. A row sums to one but entries sit in the wrong columns. Why does the sum test miss it?
3. Why subtract the maximum rather than any other constant?

Short answers are in the [separate explanations](../solutions/cuda-051_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-051: Softmax and reductions for model workloads.
Read courses/cuda/cpp/guides/cuda-051.md and courses/cuda/cpp/lessons/cuda-051.md.
Direct prerequisites: `cuda-020`, `cuda-029`, `cuda-036`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-051_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-051_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
