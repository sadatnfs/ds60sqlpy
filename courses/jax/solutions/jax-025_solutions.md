# jax-025: explained reference

For measured repeats \(t_1,\ldots,t_r\), retain the count, units and work boundary with any summary. A speed ratio \(t_A/t_B\) is interpretable only when the two measurements include equivalent work and correct results. Timing uncertainty and background activity can dominate tiny computations. The assertions here require finite nonnegative times and correct outputs, not a predetermined ordering between cold and warm measurements.

## Exercise 1: Reject an empty timing sample

An empty list does not support a meaningful elapsed-time summary.

**Expected:** ValueError.

```python
try:
    completed_times(product, values, 0)
except ValueError:
    pass
else:
    raise AssertionError('empty timing accepted')
```

## Exercise 2: Retain the shape contract

A fast result with the wrong output contract is not a performance success.

**Expected:** (16,16).

```python
result, times = completed_times(jax.jit(product), values, 1)
assert result.shape == (16, 16)
```

## Exercise 3: Compare eager and compiled outputs

This comparison fixes values and dtype before considering any timing difference.

**Expected:** Matching numerical results.

```python
close(product(values), jax.jit(product)(values))
```

## Exercise 4: Report a declared summary

The summary is descriptive of these measurements, not a confidence interval or a hardware guarantee.

**Expected:** Finite median within the observed minimum and maximum.

```python
_, times = completed_times(jax.jit(product), values, 3)
median = float(np.median(times))
assert float(times.min()) <= median <= float(times.max())
```

## Exercise 5: Change workload size explicitly

Changing shape can change both operation count and compilation specialization, so label it as another case.

**Expected:** Correct 8-by-8 result; a different workload identity.

```python
small = jnp.arange(64., dtype=jnp.float64).reshape(8, 8) / 64.
result, _ = completed_times(jax.jit(product), small, 1)
close(result, np.asarray(small) @ np.asarray(small).T)
```

## Exercise 6: Identify the executed backend

This establishes the local execution identity, not accelerator performance.

**Expected:** CPU backend and CPU-resident result.

```python
result = product(values)
result.block_until_ready()
assert jax.default_backend() == 'cpu'
assert all(device.platform == 'cpu' for device in result.devices())
```

## Scope of this evidence

If timings look implausibly small, inspect synchronization. If the first call is slow, separate compilation from warm work. If a claimed speedup changes after moving data construction, the measurement boundary changed. Never assert a universal speed ratio in a small correctness test.

Design a benchmark comparing two correct implementations with fixed shape/dtype, warmup, repeated measurements and explicit transfers. Then list the additional trace and hardware evidence needed for a GPU throughput or memory claim, connecting to cuda-031.
