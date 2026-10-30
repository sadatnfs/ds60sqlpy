# jax-004: explained reference

Let state be \(s=(a,n)\), with accumulated total \(a\) and nonnegative count \(n\). One observation \(x\) gives \(T(s,x)=(a+x,n+1)\). The mean is \(a/n\) only for \(n>0\). Combining states uses \((a_1+a_2,n_1+n_2)\), so grouping observations does not change the mathematical mean. Averaging two means without their counts generally defines a different weighting rule.

## Exercise 1: Replay a transition

Replay means identical inputs. It does not mean feeding the first result into the second call.

**Expected:** Both returned states are (5,1).

```python
left = transition(initial, 5.0)
right = transition(initial, 5.0)
close(left[0], right[0])
assert int(left[1]) == int(right[1]) == 1
```

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

## Exercise 4: Extend a saved state

Continuation requires the actual state, not only the previous displayed mean.

**Expected:** Total 32, count 4, mean 8.

```python
state = transition((jnp.float64(12.0), jnp.int64(3)), 20.0)
close(mean_of(state), 8.0)
```

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

## Exercise 6: Merge states

The pair retains enough information for this objective. Variance would require additional information.

**Expected:** Total 20, count 6, mean 10/3.

```python
groups = [(6.0, 2), (9.0, 3), (5.0, 1)]
close(sum(a for a, n in groups) / sum(n for a, n in groups), 10 / 3)
```

## Scope of this evidence

If replay differs, look for hidden mutable state or an external input. If merging groups changes the target quantity, inspect missing counts. The int(count) guard is a host-side boundary in this lesson; it is not yet a JIT-compatible dynamic validation rule.

List the state that would determine the next optimizer update, random draw and dataset position. Compare the explicit transition here with the checkpoint contracts in torch-028 and tf-028. Explain why a saved printed average is not a sufficient general checkpoint.
