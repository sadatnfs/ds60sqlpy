# jax-028: explained reference

If local sums are \(s_r\) and counts \(n_r\), the global mean is \(\sum_r s_r/\sum_r n_r\). For sums (2,12) and counts (1,3), it is 14/4=3.5, while the mean of local means is 3. For squared loss with y=2x at w=0, each sample contributes gradient \(-4x^2\). Splitting x=(1,2,3,4) into counts one and three gives gradient sums -4 and -116; the global mean is -30.

## Solution approach

Combine sums and counts, never local means. Each participant contributes its local sum and its local count, `psum` adds both across the named `replica` axis, and one division produces the global mean on every participant. `jax.vmap` with `axis_name` simulates the participants on one CPU so the arithmetic can be checked exactly.

**Why it is correct here:** Sums [2, 12] over counts [1, 3] give 14 / 4 = 3.5 on both participants. Sums [2, 6] over counts [2, 2] give 8 / 4 = 2, the same as the mean of local means because the counts are equal. Adding a participant with sum 0 and count 0 leaves 14 / 4. `all_gather` of [2, 5] gives each participant [2, 5], while `psum` of [2, 5, 7] gives each one 14.

## Exercise 1: Check equal counts

Equal counts make the weighting rules coincide; that fixture alone would not expose the unequal-count bug.

**Expected:** Both outputs two, equal to the mean of local means in this special case.

```python
close(mapped_mean(jnp.array([2.0, 6.0]), jnp.array([2.0, 2.0])), [2.0, 2.0])
```

**Plausible wrong approach:** Validating with the equal-count fixture alone accepts the mean of local means, since 1 and 3 averaged equals 2 there. Unequal counts are the case that exposes the wrong weighting.

## Exercise 2: Add a zero-count participant

A zero-count participant contributes neither observations nor numerator mass; the total count remains positive.

**Expected:** Three replicated outputs 3.5.

```python
close(mapped_mean(jnp.array([2.0, 12.0, 0.0]), jnp.array([1.0, 3.0, 0.0])), [3.5, 3.5, 3.5])
```

**Plausible wrong approach:** Having each participant divide first, `local_sum / local_count`, makes the empty participant compute 0 / 0 and inject NaN into the reduction. Summing before dividing keeps the denominator 4.

## Exercise 3: Gather participant identity

Gather retains a participant axis, whereas psum produces a reduced value.

**Expected:** Each participant receives [2,5].

```python
gather = jax.vmap(lambda x: jax.lax.all_gather(x, "replica"), axis_name="replica")
close(gather(jnp.array([2.0, 5.0])), [[2.0, 5.0], [2.0, 5.0]])
```

**Plausible wrong approach:** Expecting `all_gather` to return 7 confuses it with `psum`. Gather keeps one entry per participant, so the output gains a participant axis of length two.

## Exercise 4: Check a global sum

Replication of the reduced value does not mean the global sum should be counted three times afterward.

**Expected:** Each participant receives 14.

```python
summed = jax.vmap(lambda x: jax.lax.psum(x, "replica"), axis_name="replica")
close(summed(jnp.array([2.0, 5.0, 7.0])), [14.0, 14.0, 14.0])
```

**Plausible wrong approach:** Adding up the three replicated `psum` outputs reports 42, counting the global total three times. Each participant already holds the full sum 14.

## Exercise 5: Compile the collective model

Compilation parity does not add hardware or process evidence.

**Expected:** The same [3.5,3.5].

```python
close(jax.jit(mapped_mean)(local_sums, local_counts), [3.5, 3.5])
```

**Plausible wrong approach:** Treating the compiled run as evidence of a multi-device collective overstates it. `jax.jit(mapped_mean)` checks compilation parity on one CPU and says nothing about network communication.

## Exercise 6: Detect the wrong weighting

This negative control would pass if only equal-sized shards were tested.

**Expected:** The unweighted result differs from -30.

```python
wrong = jnp.mean(jnp.array([-4.0, -116.0]) / local_counts)
assert not np.isclose(float(wrong), -30.0)
```

**Plausible wrong approach:** Averaging the local gradient means -4 and about -38.67 gives about -21.33, not the true -120 / 4 = -30. The participant with three observations deserves three times the weight.

## How to verify

Run the reference and confirm `jax-028: 8 asserted cases passed`. Compute `local_sums.sum() / local_counts.sum()` with ordinary array operations and compare it with `mapped_mean`. Then compute `(local_sums / local_counts).mean()` and see (2 + 4) / 2 = 3 instead of 3.5, the same weighting error on the value side.

## Scope of this evidence

Check whether each quantity is a sum, mean, count, replicated global value or gathered per-participant array. The all-zero global-count case needs a declared input-validation policy before division. Correct mapped CPU arithmetic is not evidence of actual multi-host collective ordering or recovery.

Translate this calculation into a proposed data-parallel training step with unequal nonpadding token counts. Explain the actual collective order and ownership evidence a multi-process implementation would need, connecting to torch-030 and tf-030.
