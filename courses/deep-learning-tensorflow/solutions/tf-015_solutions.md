# tf-015: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A data pipeline is part of the statistical experiment. It determines which records arrive, in what order, under which transformation and how many times. tf.data represents that sequence lazily. Constructing a Dataset is not evidence that its elements were visited. Carry record IDs through transformations so cardinality and pairing remain inspectable. A training-derived mean can be applied during mapping, but validation records must not participate in estimating it. Batching creates a new leading axis, and prefetch overlaps preparation with consumption without changing the desired order. This tiny pipeline uses literal arrays and no file or network side effects.

**Cardinality:** Number of dataset elements at a specific pipeline stage.

**Map:** A transformation applied to each element.

**Prefetch:** Bounded preparation of upcoming elements before consumption.

## Reading the implementation

from_tensor_slices slices the leading axis of each tuple component together. map receives one ID and one value; arithmetic can use a frozen scalar mean. batch(2,drop_remainder=False) retains the final singleton. as_numpy_iterator materializes values for small teaching assertions, not an approach for collecting an unbounded production dataset. prefetch(1) limits the look-ahead buffer.

## Exercise 1: Observe batches

The question is: Build a dataset from IDs0..4 and values1..5, then batch by2.

The input cardinality is five records but the batched cardinality is three elements. Naming the stage prevents a batch count from being mistaken for a dataset size.

```python
ds=tf.data.Dataset.from_tensor_slices((np.arange(5),np.arange(1,6,dtype='float32')))
batches=list(ds.batch(2).as_numpy_iterator())
assert [len(ids) for ids,values in batches]==[2,2,1]
```

**Expected:** batch sizes[2,2,1].

**Verify:** Compare the computed values or written argument with batch sizes[2,2,1].

## Exercise 2: Apply training statistics

The question is: Use values1,2,3 to fit mean 2, then transform all five values without refitting.

The held-out values4 and5 are transformed with the same mean. Their transformed average is not zero, which is expected when a frozen training transformation meets a different subset.

```python
mean=np.mean([1.,2.,3.]); centered=ds.map(lambda i,v:(i,v-tf.cast(mean,tf.float32)))
values=np.array([float(v) for i,v in centered.as_numpy_iterator()])
np.testing.assert_array_equal(values,[-1,0,1,2,3])
```

**Expected:** centered values[-1,0,1,2,3].

**Verify:** Compare the computed values or written argument with centered values[-1,0,1,2,3].

## Exercise 3: Retain IDs through mapping

The question is: Reassemble the IDs after centering, batching and prefetch1.

Value-only comparisons cannot detect reordered or duplicated observations when values repeat. IDs provide an independent conservation check across the pipeline.

```python
got=np.concatenate([i for i,v in centered.batch(2).prefetch(1).as_numpy_iterator()])
np.testing.assert_array_equal(got,np.arange(5))
```

**Expected:** IDs0,1,2,3,4 in order.

**Verify:** Compare the computed values or written argument with IDs0,1,2,3,4 in order.

## Exercise 4: Compare explicit dropping

The question is: Use drop_remainder=True and report which record disappears.

Dropping can be intentional for fixed-shape training, but it changes the effective population of an epoch. A learner should record the omitted tail instead of calling the pipeline equivalent.

```python
dropped=list(ds.batch(2,drop_remainder=True).as_numpy_iterator())
assert [len(i) for i,v in dropped]==[2,2]
assert np.concatenate([i for i,v in dropped]).tolist()==[0,1,2,3]
```

**Expected:** sizes[2,2]; ID4 absent.

**Verify:** Compare the computed values or written argument with sizes[2,2]; ID4 absent.

## Exercise 5: Recreate a deterministic traversal

The question is: Construct the same literal dataset twice and compare complete ordered values.

A repeated traversal is meaningful because there is no hidden random map, file update or external fetch. Later random augmentation requires an additional policy and invariants.

```python
again=tf.data.Dataset.from_tensor_slices((np.arange(5),np.arange(1,6,dtype='float32')))
a=[(int(i),float(v)) for i,v in ds.as_numpy_iterator()]
b=[(int(i),float(v)) for i,v in again.as_numpy_iterator()]
assert a==b==[(0,1.),(1,2.),(2,3.),(3,4.),(4,5.)]
```

**Expected:** both traversals equal the original five pairs.

**Verify:** Compare the computed values or written argument with both traversals equal the original five pairs.

## Exercise 6: Check paired transformation

The question is: Scale values by2 and preserve IDs, then verify the value relation2*(ID+1).

Keeping paired components in one dataset tuple prevents independent reorderings. The exact arithmetic relation detects a pipeline that transforms values while selecting unrelated IDs.

```python
scaled=ds.map(lambda i,v:(i,2*v))
assert all(float(v)==2*(int(i)+1) for i,v in scaled.as_numpy_iterator())
```

**Expected:** all five pairs satisfy the relation.

**Verify:** Compare the computed values or written argument with all five pairs satisfy the relation.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
