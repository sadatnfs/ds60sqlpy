# tf-033: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Inference is a function with a data contract, not just a call to model.predict. The model expects a nonempty batch of two finite float32 features per record and accepts at most four records. Inputs outside that boundary should receive named failures rather than silent coercion. Batching should preserve record identity: predicting one record alone or alongside others should give the same result for this stateless model. This local contract does not start a server or claim security isolation. It establishes a small, reviewable boundary that an eventual service would need to enforce consistently.

**Inference contract:** Accepted inputs and guaranteed output structure for prediction.

**Batch limit:** Maximum number of observations accepted in one call.

**Finite value:** A numeric value that is neither NaN nor infinity.

## Reading the implementation

np.asarray inspects the incoming data without automatically changing its dtype. Check rank, feature width, batch limit and finiteness before converting to a tensor. A fixed coefficient vector[2,-1] gives an independent expected output. Returning a new array prevents a caller from mutating stored input through a shared view. Validation order should make errors predictable enough to diagnose.

## Exercise 1: Predict a valid batch

The question is: Predict for float32 rows[1,2],[3,4].

The reference coefficient vector makes output arithmetic transparent. Shape validation ensures the result is one scalar per input record.

```python
x = np.array([[1, 2], [3, 4]], dtype="float32")
result = predict(x)
np.testing.assert_array_equal(result, [0, 2])
assert result.shape == (2,)
```

**Expected:** outputs 0,2 with shape(2,).

**Verify:** Compare the computed values or written argument with outputs 0,2 with shape(2,).

## Exercise 2: Compare batch independence

The question is: Predict each row independently and compare concatenated outputs with the batch result.

A stateless affine model should not depend on neighboring records. A training-mode normalization layer could violate this behavior, so the test is valuable when the implementation grows.

```python
single = np.concatenate([predict(x[i : i + 1]) for i in range(2)])
np.testing.assert_array_equal(single, result)
```

**Expected:** exact equality for this fixed linear fixture.

**Verify:** Compare the computed values or written argument with exact equality for this fixed linear fixture.

## Exercise 3: Reject empty and oversized batches

The question is: Pass shapes(0,2) and(5,2).

An empty batch provides no predictions, and an oversized batch violates the declared resource budget. Both failures occur before the model computation.

```python
for bad in [np.empty((0, 2), dtype="float32"), np.zeros((5, 2), dtype="float32")]:
    try:
        predict(bad)
    except ValueError as error:
        assert "batch" in str(error)
    else:
        raise AssertionError("bad batch accepted")
```

**Expected:** ValueError with batch in the message.

**Verify:** Compare the computed values or written argument with ValueError with batch in the message.

## Exercise 4: Reject wrong feature structure

The question is: Pass a vector[1,2] and a matrix with three columns.

A single record still needs a batch axis. Guessing whether a vector represents one record or many one-feature records can silently change the meaning of data.

```python
for bad in [np.array([1, 2], dtype="float32"), np.zeros((2, 3), dtype="float32")]:
    try:
        predict(bad)
    except ValueError as error:
        assert "shape" in str(error)
    else:
        raise AssertionError("bad shape accepted")
```

**Expected:** ValueError with shape in the message.

**Verify:** Compare the computed values or written argument with ValueError with shape in the message.

## Exercise 5: Reject nonfinite values and wrong dtype

The question is: Pass a NaN row and an int64 row under the explicit float32 policy.

A strict dtype boundary makes precision changes visible. A different API could deliberately cast, but it would need to document and test that policy rather than do it implicitly.

```python
try:
    predict(np.array([[np.nan, 1]], dtype="float32"))
except ValueError:
    pass
else:
    raise AssertionError("NaN accepted")
try:
    predict(np.array([[1, 2]], dtype="int64"))
except TypeError:
    pass
else:
    raise AssertionError("dtype silently coerced")
```

**Expected:** ValueError for nonfinite; TypeError for dtype.

**Verify:** Compare the computed values or written argument with ValueError for nonfinite; TypeError for dtype.

## Exercise 6: Preserve the input

The question is: Snapshot a valid batch, predict and mutate the returned result; compare the original input.

Ownership is part of the contract. An output view into caller or model state can turn a harmless downstream edit into a hidden data mutation.

```python
before = x.copy()
answer = predict(x)
answer[0] = 999
np.testing.assert_array_equal(x, before)
```

**Expected:** input remains byte-identical.

**Verify:** Compare the computed values or written argument with input remains byte-identical.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
