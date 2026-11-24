# jax-025: explained reference

For measured repeats \(t_1,\ldots,t_r\), retain the count, units and work boundary with any summary. A speed ratio \(t_A/t_B\) is interpretable only when the two measurements include equivalent work and correct results. Timing uncertainty and background activity can dominate tiny computations. The assertions here require finite nonnegative times and correct outputs, not a predetermined ordering between cold and warm measurements.

## Solution approach

Make each timing measure finished work. `completed_times` validates its count, calls the function, waits with `block_until_ready`, and records the elapsed time for each repetition. Before any time is reported, the result's shape and values are checked, and the workload, backend and summary statistic are named explicitly.

**Why it is correct here:** Zero repetitions raise ValueError, since an empty sample has no median. The product of a (16, 16) array with its transpose is (16, 16). Eager and compiled products agree on values. A median of three finite times lies between their minimum and maximum. The 8 by 8 product matches NumPy. On this lesson's profile the default backend and the result's device are both CPU.

## Exercise 1: Reject an empty timing sample

An empty list does not support a meaningful elapsed-time summary.

**Expected:** ValueError.

```python
try:
    completed_times(product, values, 0)
except ValueError:
    pass
else:
    raise AssertionError("empty timing accepted")
```

**Plausible wrong approach:** Stopping the clock as soon as `function(argument)` returns can measure only dispatch, because JAX runs asynchronously. Waiting with `block_until_ready` makes each time include the completed computation.

## Exercise 2: Retain the shape contract

A fast result with the wrong output contract is not a performance success.

**Expected:** (16,16).

```python
result, times = completed_times(jax.jit(product), values, 1)
assert result.shape == (16, 16)
```

**Plausible wrong approach:** Passing `repeats=3.0` or `True` might seem harmless, but the guard uses `type(repeats) is not int`, which rejects both. The count must be a genuine positive integer.

## Exercise 3: Compare eager and compiled outputs

This comparison fixes values and dtype before considering any timing difference.

**Expected:** Matching numerical results.

```python
close(product(values), jax.jit(product)(values))
```

**Plausible wrong approach:** Comparing eager and compiled times before comparing their values could reward a faster function that computes something else. The value check comes first.

## Exercise 4: Report a declared summary

The summary is descriptive of these measurements, not a confidence interval or a hardware guarantee.

**Expected:** Finite median within the observed minimum and maximum.

```python
_, times = completed_times(jax.jit(product), values, 3)
median = float(np.median(times))
assert float(times.min()) <= median <= float(times.max())
```

**Plausible wrong approach:** Reporting the mean of three times lets one slow first call, which can include tracing and compilation, dominate the summary. The median is the declared statistic, and it describes only these runs.

## Exercise 5: Change workload size explicitly

Changing shape can change both operation count and compilation specialization, so label it as another case.

**Expected:** Correct 8-by-8 result; a different workload identity.

```python
small = jnp.arange(64.0, dtype=jnp.float64).reshape(8, 8) / 64.0
result, _ = completed_times(jax.jit(product), small, 1)
close(result, np.asarray(small) @ np.asarray(small).T)
```

**Plausible wrong approach:** Placing the 8 by 8 time next to the 16 by 16 time as one series mixes two workloads. The smaller shape does less arithmetic and gets its own compiled specialization.

## Exercise 6: Identify the executed backend

This establishes the local execution identity, not accelerator performance.

**Expected:** CPU backend and CPU-resident result.

```python
result = product(values)
result.block_until_ready()
assert jax.default_backend() == "cpu"
assert all(device.platform == "cpu" for device in result.devices())
```

**Plausible wrong approach:** Quoting these CPU times as evidence about accelerators extrapolates beyond the measurement. The backend check records where the work ran; it says nothing about GPU or TPU speed.

## How to verify

Run the reference and confirm `jax-025: 8 asserted cases passed`. Print the three times from `completed_times(jax.jit(product), values, 3)` and note whether the first is larger. Then time the same call without `block_until_ready` in a scratch copy and compare, keeping both values labeled as local observations.

## Scope of this evidence

If timings look implausibly small, inspect synchronization. If the first call is slow, separate compilation from warm work. If a claimed speedup changes after moving data construction, the measurement boundary changed. Never assert a universal speed ratio in a small correctness test.

Design a benchmark comparing two correct implementations with fixed shape/dtype, warmup, repeated measurements and explicit transfers. Then list the additional trace and hardware evidence needed for a GPU throughput or memory claim, connecting to cuda-031.
