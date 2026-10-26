# jax-028: explained reference

If local sums are \(s_r\) and counts \(n_r\), the global mean is \(\sum_r s_r/\sum_r n_r\). For sums (2,12) and counts (1,3), it is 14/4=3.5, while the mean of local means is 3. For squared loss with y=2x at w=0, each sample contributes gradient \(-4x^2\). Splitting x=(1,2,3,4) into counts one and three gives gradient sums -4 and -116; the global mean is -30.

## Exercise 1: Check equal counts

Equal counts make the weighting rules coincide; that fixture alone would not expose the unequal-count bug.

**Expected:** Both outputs two, equal to the mean of local means in this special case.

```python
close(mapped_mean(jnp.array([2., 6.]), jnp.array([2., 2.])), [2., 2.])
```

## Exercise 2: Add a zero-count participant

A zero-count participant contributes neither observations nor numerator mass; the total count remains positive.

**Expected:** Three replicated outputs 3.5.

```python
close(mapped_mean(jnp.array([2., 12., 0.]), jnp.array([1., 3., 0.])), [3.5, 3.5, 3.5])
```

## Exercise 3: Gather participant identity

Gather retains a participant axis, whereas psum produces a reduced value.

**Expected:** Each participant receives [2,5].

```python
gather = jax.vmap(lambda x: jax.lax.all_gather(x, 'replica'), axis_name='replica')
close(gather(jnp.array([2., 5.])), [[2., 5.], [2., 5.]])
```

## Exercise 4: Check a global sum

Replication of the reduced value does not mean the global sum should be counted three times afterward.

**Expected:** Each participant receives 14.

```python
summed = jax.vmap(lambda x: jax.lax.psum(x, 'replica'), axis_name='replica')
close(summed(jnp.array([2., 5., 7.])), [14., 14., 14.])
```

## Exercise 5: Compile the collective model

Compilation parity does not add hardware or process evidence.

**Expected:** The same [3.5,3.5].

```python
close(jax.jit(mapped_mean)(local_sums, local_counts), [3.5, 3.5])
```

## Exercise 6: Detect the wrong weighting

This negative control would pass if only equal-sized shards were tested.

**Expected:** The unweighted result differs from -30.

```python
wrong = jnp.mean(jnp.array([-4., -116.]) / local_counts)
assert not np.isclose(float(wrong), -30.)
```

## Scope of this evidence

Check whether each quantity is a sum, mean, count, replicated global value or gathered per-participant array. The all-zero global-count case needs a declared admission policy before division. Correct mapped CPU arithmetic is not evidence of actual multi-host collective ordering or recovery.

Translate this calculation into a proposed data-parallel training step with unequal nonpadding token counts. Explain the actual collective order and ownership evidence a multi-process implementation would need, connecting to torch-030 and tf-030.
