# r-036: reference reasoning

Use the [complete reference](r-036_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The two chunks have unequal sizes. Sufficient totals reconstruct the observation mean while averaging the two chunk means changes the weighting.

Each input entry contributes to either observed or missing count. The total uses only observed measurements under the declared policy.

## Explained practice

### Exercise 1

Reconstruct a mean from count 4, total 100.

The mean is 25.

**Expected evidence:** The mean is 25.

### Exercise 2

Change chunk boundaries without changing observations.

The semantic total/count remain unchanged, subject to floating-point tolerance.

**Expected evidence:** The semantic total/count remain unchanged, subject to floating-point tolerance.

### Exercise 3

Implement an all-missing finalization rule.

Return an explicit missing mean when count is zero.

**Expected evidence:** Return an explicit missing mean when count is zero.

### Exercise 4

Diagnose averaging chunk medians.

Keep sufficient distribution state or recompute the exact combined median.

**Expected evidence:** Keep sufficient distribution state or recompute the exact combined median.

### Exercise 5

Process an empty chunk among nonempty chunks.

It leaves the accumulated state unchanged.

**Expected evidence:** It leaves the accumulated state unchanged.

### Exercise 6

State what a scalability claim still requires.

Measure representative peak memory, elapsed work and equivalent outputs under controlled conditions.

**Expected evidence:** Measure representative peak memory, elapsed work and equivalent outputs under controlled conditions.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
