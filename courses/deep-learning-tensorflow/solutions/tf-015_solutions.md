# tf-015: explanatory solutions

Open these answers after an attempt; they reuse the guide's inputs ([comparison steps](../STUDY-GUIDE.md#after-the-solutions)).

## Mechanism review

A data pipeline is part of the statistical experiment. It determines which records arrive, in what order, under which transformation and how many times. tf.data represents that sequence lazily. Constructing a Dataset is not evidence that its elements were visited. Carry record IDs through transformations so cardinality and pairing remain inspectable. A training-derived mean can be applied during mapping, but validation records must not participate in estimating it. Batching creates a new leading axis, and prefetch overlaps preparation with consumption without changing the desired order. This tiny pipeline uses literal arrays and no file or network side effects.

**Cardinality:** Number of dataset elements at a specific pipeline stage.

**Map:** A transformation applied to each element.

**Prefetch:** Bounded preparation of upcoming elements before consumption.

## Reading the implementation

from_tensor_slices slices the leading axis of each tuple component together. map receives one ID and one value; arithmetic can use a frozen scalar mean. batch (2, drop_remainder=False) retains the final singleton. as_numpy_iterator materializes values for small teaching assertions, not an approach for collecting an unbounded production dataset. prefetch(1) limits the look-ahead buffer. shuffle(5, seed=7, reshuffle_each_iteration=False) draws from a five-record buffer, so it can reorder the whole fixture; the seed fixes that order and reshuffle_each_iteration=False repeats it on every traversal.

## Exercise 1: Replay a seeded shuffle

The question is: Shuffle the five records with shuffle(5, seed=7, reshuffle_each_iteration=False). Traverse it twice, rebuild the same pipeline from the literal arrays, and compare the ID orders.

A buffer of five holds the whole fixture, so any order is possible. The operation seed fixes the order and reshuffle_each_iteration=False repeats it on every pass; with the default True, each epoch would draw a new order. Shuffling the (ID, value) tuple keeps each pair together, which the ID+1 check confirms.

```python
replay = ds.shuffle(5, seed=7, reshuffle_each_iteration=False)
first = [int(i) for i, v in replay.as_numpy_iterator()]
assert [int(i) for i, v in replay.as_numpy_iterator()] == first
rebuilt = tf.data.Dataset.from_tensor_slices(
    (np.arange(5), np.arange(1, 6, dtype="float32"))
).shuffle(5, seed=7, reshuffle_each_iteration=False)
assert [int(i) for i, v in rebuilt.as_numpy_iterator()] == first
assert sorted(first) == [0, 1, 2, 3, 4]
assert all(float(v) == int(i) + 1 for i, v in replay.as_numpy_iterator())
```

**Expected:** the same ID order on both passes and after rebuilding; IDs 0-4 each appear once; every value is still ID+1.

**Verify:** In a fresh process, the exercise checks confirm `[int(i) for i, v in replay.as_numpy_iterator()] == first`; `[int(i) for i, v in rebuilt.as_numpy_iterator()] == first`; `sorted(first) == [0, 1, 2, 3, 4]` and `all((float(v) == int(i) + 1 for i, v in replay.as_numpy_iterator()))`.

## Exercise 2: Predict a different batch size

The question is: Predict the batch sizes for batch(3), then the surviving IDs when drop_remainder=True, before running the pipeline.

Five records in batches of three leave a remainder of two. Dropping it removes 40 percent of this fixture, far more than the single record lost with batches of two, so the ledger of absent IDs matters more as the batch grows.

```python
sizes = [len(i) for i, v in ds.batch(3).as_numpy_iterator()]
kept = np.concatenate([i for i, v in ds.batch(3, drop_remainder=True).as_numpy_iterator()])
assert sizes == [3, 2]
assert kept.tolist() == [0, 1, 2]
```

**Expected:** sizes [3, 2]; with drop_remainder=True only IDs 0, 1, 2 remain.

**Verify:** In a fresh process, the exercise checks confirm `sizes == [3, 2]` and `kept.tolist() == [0, 1, 2]`.

## Exercise 3: Retain IDs through mapping

The question is: Reassemble the IDs after centering, batching and prefetch 1.

Value-only comparisons cannot detect reordered or duplicated observations when values repeat. IDs provide an independent conservation check across the pipeline.

```python
got = np.concatenate([i for i, v in centered.batch(2).prefetch(1).as_numpy_iterator()])
np.testing.assert_array_equal(got, np.arange(5))
```

**Expected:** IDs 0, 1, 2, 3, 4 in order.

**Verify:** In a fresh process, the exercise checks confirm `got` equals `np.arange(5)`.

## Exercise 4: Compare explicit dropping

The question is: Use drop_remainder=True and report which record disappears.

Dropping can be intentional for fixed-shape training, but it changes the effective population of an epoch. A learner should record the omitted tail instead of calling the pipeline equivalent.

```python
dropped = list(ds.batch(2, drop_remainder=True).as_numpy_iterator())
assert [len(i) for i, v in dropped] == [2, 2]
assert np.concatenate([i for i, v in dropped]).tolist() == [0, 1, 2, 3]
```

**Expected:** sizes [2, 2]; ID 4 absent.

**Verify:** In a fresh process, the exercise checks confirm `[len(i) for i, v in dropped] == [2, 2]` and `np.concatenate([i for i, v in dropped]).tolist() == [0, 1, 2, 3]`.

## Exercise 5: Recreate a deterministic traversal

The question is: Construct the same literal dataset twice and compare complete ordered values.

A repeated traversal is meaningful because there is no hidden random map, file update or external fetch. Later random augmentation requires an additional policy and invariants.

```python
again = tf.data.Dataset.from_tensor_slices((np.arange(5), np.arange(1, 6, dtype="float32")))
a = [(int(i), float(v)) for i, v in ds.as_numpy_iterator()]
b = [(int(i), float(v)) for i, v in again.as_numpy_iterator()]
assert a == b == [(0, 1.0), (1, 2.0), (2, 3.0), (3, 4.0), (4, 5.0)]
```

**Expected:** both traversals equal the original five pairs.

**Verify:** In a fresh process, the exercise checks confirm `a == b == [(0, 1.0), (1, 2.0), (2, 3.0), (3, 4.0), (4, 5.0)]`.

## Exercise 6: Check paired transformation

The question is: Scale values by 2 and preserve IDs, then verify the value relation 2*(ID+1).

Keeping paired components in one dataset tuple prevents independent reorderings. The exact arithmetic relation detects a pipeline that transforms values while selecting unrelated IDs.

```python
scaled = ds.map(lambda i, v: (i, 2 * v))
assert all(float(v) == 2 * (int(i) + 1) for i, v in scaled.as_numpy_iterator())
```

**Expected:** all five pairs satisfy the relation.

**Verify:** In a fresh process, the exercise checks confirm `all((float(v) == 2 * (int(i) + 1) for i, v in scaled.as_numpy_iterator()))`.

