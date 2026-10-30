# tf-030: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A distributed or accumulated gradient must represent the intended global objective. If shards have different numbers of examples, averaging shard means equally weights shards rather than observations. A one-example shard with mean gradient2 and a three-example shard with mean6 combine to5 under an example mean, not4. Gradient accumulation has the same issue when microbatches differ in size. Accumulate gradient sums and counts, divide once, then apply one optimizer update. Applying an update after each microbatch is a different trajectory because later gradients use changed parameters. This lesson simulates all shards on one CPU and does not claim a distributed runtime was exercised.

**Shard:** A subset of observations processed as one partition.

**Gradient accumulation:** Combining gradients before one optimizer update.

**Global denominator:** The total participating example count across partitions.

## Reading the implementation

The identity global_mean=sum(count*local_mean)/sum(count) is independent of a communication library. tf.reduce_sum exposes numerators. Hold weights fixed while accumulating gradients, then assign once. A regularization term needs a deliberate global scaling convention so it is not accidentally multiplied by the number of shards. The examples distinguish mathematical reduction from runtime placement.

## Exercise 1: Weight shard means

The question is: Combine means2,6 with counts1,3 and compare equal shard averaging.

Multiplying each local mean by its count restores the gradient numerator. The final division then gives each example equal weight.

```python
means = np.array([2.0, 6.0])
counts = np.array([1, 3])
assert np.average(means, weights=counts) == 5 and means.mean() == 4
```

**Expected:** global5; naive4.

**Verify:** Compare the computed values or written argument with global5; naive4.

## Exercise 2: Recover a full-batch mean

The question is: Partition gradients[2,4,6,8] into sizes 1 and3 and reconstruct their mean.

The explicit per-example values are an independent oracle for the shard calculation. A test that compares two formulas using the same wrong weights would miss the error.

```python
g = np.array([2.0, 4.0, 6.0, 8.0])
parts = [g[:1], g[1:]]
recombined = sum(p.sum() for p in parts) / sum(len(p) for p in parts)
assert recombined == g.mean() == 5
```

**Expected:** both full and reconstructed means5.

**Verify:** Compare the computed values or written argument with both full and reconstructed means5.

## Exercise 3: Accumulate squared-loss gradients

The question is: At w = 0 use x = [1, 2, 3, 4],y = 2x; compare full-batch gradient with sum-then-divide microbatches.

The variable remains fixed while all microbatch gradients are calculated. This is the condition under which accumulation matches the full-batch gradient.

```python
x = tf.constant([1.0, 2.0, 3.0, 4.0])
y = 2 * x
w = tf.Variable(0.0)
with tf.GradientTape() as tape:
    full = tf.reduce_mean((w * x - y) ** 2)
full_g = tape.gradient(full, w)
total = 0.0
for start, end in [(0, 1), (1, 4)]:
    with tf.GradientTape() as tape:
        summed = tf.reduce_sum((w * x[start:end] - y[start:end]) ** 2)
    total += float(tape.gradient(summed, w))
assert float(full_g) == total / 4 == -30
```

**Expected:** gradient-30 for both.

**Verify:** Compare the computed values or written argument with gradient-30 for both.

## Exercise 4: Apply exactly one update

The question is: Use rate 0.01 with accumulated global gradient-30.

The update counter should increment once for this effective batch. Incrementing a learning-rate schedule once per microbatch changes the optimizer policy even if gradients are combined correctly.

```python
w.assign_sub(0.01 * (total / 4))
np.testing.assert_allclose(float(w), 0.3, atol=1e-6, rtol=0)
```

**Expected:** updated weight.3.

**Verify:** Compare the computed values or written argument with updated weight.3.

## Exercise 5: Expose per-batch updates

The question is: Update separately for the two microbatches and compare the final weight with.3.

The second gradient uses the weight changed by the first update. This is ordinary minibatch training, not a numerical implementation of one full-batch step.

```python
other = tf.Variable(0.0)
for start, end in [(0, 1), (1, 4)]:
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean((other * x[start:end] - y[start:end]) ** 2)
    other.assign_sub(0.01 * tape.gradient(loss, other))
assert abs(float(other) - 0.3) > 1e-6
```

**Expected:** endpoint differs from.3.

**Verify:** Compare the computed values or written argument with endpoint differs from.3.

## Exercise 6: Handle an empty shard

The question is: Combine an empty shard and the four real gradients using sums and counts; reject a globally empty batch.

A local empty shard need not invalidate a nonempty global batch, but mean(empty) is undefined. Carrying sums and counts avoids producing a NaN local mean.

```python
parts = [np.array([], dtype=float), g]
count = sum(len(p) for p in parts)
assert count == 4 and sum(p.sum() for p in parts) / count == 5
assert sum(len(p) for p in [np.array([])]) == 0
```

**Expected:** empty shard contributes0; total remains5.

**Verify:** Compare the computed values or written argument with empty shard contributes0; total remains5.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
