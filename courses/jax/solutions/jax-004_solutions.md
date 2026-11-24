# jax-004: explained reference

Let state be \(s=(a,n)\), with accumulated total \(a\) and nonnegative count \(n\). One observation \(x\) gives \(T(s,x)=(a+x,n+1)\). The mean is \(a/n\) only for \(n>0\). Combining states uses \((a_1+a_2,n_1+n_2)\), so grouping observations does not change the mathematical mean. Averaging two means without their counts generally defines a different weighting rule.

## Solution approach

State is the pair `(total, count)` and `transition` returns a new pair instead of editing anything in place. Each task asks which pair results from a given sequence of observations, so trace the pair by hand: start at (0, 0), add the value to the total and one to the count, and divide only when the count is positive.

**Why it is correct here:** From (0, 0), the values 1, 3 and 8 produce (1, 1), (4, 2) and (12, 3), so the mean is 4. Feeding 20 into the saved (12, 3) gives (32, 4) and a mean of 8. The groups (6, 2), (9, 3) and (5, 1) combine to (20, 6), a mean of 10/3, because totals and counts add independently of grouping.

## Exercise 1: Replay a transition

Replay means identical inputs. It does not mean feeding the first result into the second call.

**Expected:** Both returned states are (5,1).

```python
left = transition(initial, 5.0)
right = transition(initial, 5.0)
close(left[0], right[0])
assert int(left[1]) == int(right[1]) == 1
```

**Plausible wrong approach:** Passing the first result into the second call, `transition(transition(initial, 5.0), 5.0)`, gives (10, 2) and makes the two runs differ. Replay means the same input state and value, which both produce (5, 1).

## Exercise 2: Accumulate a sequence

Each next transition consumes the previous returned state.

**Expected:** Total 12, count 3, mean 4.

```python
state = initial
for value in [1.0, 3.0, 8.0]:
    state = transition(state, value)
close(state[0], 12.0)
assert int(state[1]) == 3
close(mean_of(state), 4.0)
```

**Plausible wrong approach:** Keeping only a running mean and updating it as `(mean + value) / 2` starts at 1, moves to 2 after the 3 and ends at 5 after the 8, not 4. Without the count, the latest value is overweighted.

## Exercise 3: Refuse an empty mean

Zero observations does not imply a mean of zero.

**Expected:** ValueError.

```python
try:
    mean_of(initial)
except ValueError:
    pass
else:
    raise AssertionError("empty mean accepted")
```

**Plausible wrong approach:** Returning `total / max(count, 1)` reports a mean of 0 for the empty state. Zero observations do not have a mean of zero, so `mean_of` raises ValueError instead.

## Exercise 4: Extend a saved state

Continuation requires the actual state, not only the previous displayed mean.

**Expected:** Total 32, count 4, mean 8.

```python
state = transition((jnp.float64(12.0), jnp.int64(3)), 20.0)
close(mean_of(state), 8.0)
```

**Plausible wrong approach:** Continuing from the printed mean 4 alone cannot weight the new value of 20; `(4 + 20) / 2 = 12` is wrong. The saved total 12 and count 3 are what give the correct mean of 8.

## Exercise 5: Check order-independent totals

The mathematical aggregation is order-independent; larger floating reductions can still differ by rounding.

**Expected:** Equal sum/count and mean for these exactly representable values.

```python
state = initial
for value in [8.0, 3.0, 1.0]:
    state = transition(state, value)
close(state[0], 12.0)
assert int(state[1]) == 3
```

**Plausible wrong approach:** Concluding that floating sums are always order-independent overreaches. These values are small integers that float64 represents exactly; long sums of mixed magnitudes can round differently when reordered.

## Exercise 6: Merge states

The pair retains enough information for this objective. Variance would require additional information.

**Expected:** Total 20, count 6, mean 10/3.

```python
groups = [(6.0, 2), (9.0, 3), (5.0, 1)]
close(sum(a for a, n in groups) / sum(n for a, n in groups), 10 / 3)
```

**Plausible wrong approach:** Averaging the three group means 3, 3 and 5 gives 11/3, not 10/3. That treats each group as one observation, while the group with three items should count three times as much.

## How to verify

Run the reference and expect `jax-004: 8 asserted cases passed`. For an independent check, compute `sum([1, 3, 8]) / 3` and `sum([1, 3, 8, 20]) / 4` in plain Python and compare them with `mean_of` on the traced states. Calling `mean_of(initial)` must raise ValueError, and swapping the order of the three values must leave (12, 3) unchanged.

## Scope of this evidence

If replay differs, look for hidden mutable state or an external input. If merging groups changes the target quantity, inspect missing counts. The int(count) guard is a host-side boundary in this lesson; it is not yet a JIT-compatible dynamic validation rule.

List the state that would determine the next optimizer update, random draw and dataset position. Compare the explicit transition here with the checkpoint contracts in torch-028 and tf-028. Explain why a saved printed average is not a sufficient general checkpoint.
