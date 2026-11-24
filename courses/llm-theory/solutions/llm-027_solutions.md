# llm-027: explanatory solutions

Read these calibration and comparable evaluation answers after attempting *Weight three documents* through *Reject incompatible tokenizer scores*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Represent an empty bin* points to one step. `llm-027_solution.py` holds the assertions; this page explains how they test calibration. Then try *Reject incompatible tokenizer scores* on a fresh input you chose before looking.

## Mechanism review

Evaluation needs compatible units. Token-weighted loss averages over token events; averaging document means gives equal weight to documents regardless of length. Calibration compares predicted confidence with observed frequency within declared bins, always reporting bin counts. A confident prediction can be wrong, and a low average error can coexist with poor confidence estimates. Empty bins contain no evidence and should not be assigned a zero observed rate. Comparing perplexity across incompatible tokenizers changes the event definition, so it cannot be treated as a direct quality ranking. Saved predictions let these issues be studied without executing an online model.

**Calibration:** Agreement between predicted confidence and observed frequency.

**Bin count:** Number of observations supporting a calibration summary.

**Comparable unit:** An event definition shared by the quantities being compared.

## Reading the implementation

Store per-event confidence and a boolean correctness outcome. Use explicit half-open bin boundaries, with the final bin including 1. Compute each bin count, mean confidence and observed accuracy separately. For loss, retain sums and counts until the final division. Join model comparisons by stable event IDs rather than relying on array order.

## Exercise 1: Weight three documents

The question is: Combine document mean losses 2, 4 and 1 with token counts 2, 1 and 5.

The long, low-loss document dominates the token-weighted mean, while each document counts once in the document mean. The two summaries answer different questions and must be labelled.

```python
means3 = np.array([2.0, 4.0, 1.0])
counts3 = np.array([2, 1, 5])
np.testing.assert_allclose(np.average(means3, weights=counts3), 13 / 8, atol=1e-12, rtol=0)
np.testing.assert_allclose(means3.mean(), 7 / 3, atol=1e-12, rtol=0)
```

**Expected:** token-weighted mean 13/8 = 1.625; document mean 7/3, about 2.333.

**Verify:** For *Weight three documents*, a fresh-process check confirms `np.average(means3, weights=counts3)` matches `13 / 8` within 1e-12 and `means3.mean()` matches `7 / 3` within 1e-12.

## Exercise 2: Summarize a second calibration bin

The question is: Use confidences 0.9, 0.9, 0.7, 0.9, 0.6 with correctness 1, 0, 1, 1, 0 in a single bin.

The bin has the same mean confidence as Example B but lower accuracy, so its calibration gap is larger. Five predictions remain a small sample for estimating that gap.

```python
conf2 = np.array([0.9, 0.9, 0.7, 0.9, 0.6])
correct2 = np.array([1, 0, 1, 1, 0])
assert len(conf2) == 5
np.testing.assert_allclose(conf2.mean(), 0.8, atol=1e-12, rtol=0)
assert correct2.mean() == 0.6
np.testing.assert_allclose(conf2.mean() - correct2.mean(), 0.2, atol=1e-12, rtol=0)
```

**Expected:** count 5, mean confidence 0.8, accuracy 0.6: overconfident by 0.2.

**Verify:** For *Summarize a second calibration bin*, a fresh-process check confirms `len(conf2) == 5`, `conf2.mean()` matches `0.8` within 1e-12, `correct2.mean() == 0.6` and `conf2.mean() - correct2.mean()` matches `0.2` within 1e-12.

## Exercise 3: Represent an empty bin

The question is: Select confidence values below 0.5 and summarize without fabricating a rate.

Zero accuracy would imply observed failures, while perfect accuracy would imply observed successes. An empty bin supports neither statement.

```python
mask = confidence < 0.5
summary = {
    "count": int(mask.sum()),
    "accuracy": None if not mask.any() else float(correct[mask].mean()),
}
assert summary == {"count": 0, "accuracy": None}
```

**Expected:** count 0 and accuracy None.

**Verify:** For *Represent an empty bin*, a fresh-process check confirms `summary == {'count': 0, 'accuracy': None}`.

## Exercise 4: Check boundary membership

The question is: Use bins [0.5, 0.8) and [0.8, 1] on the fixture.

A value exactly on a boundary must enter only one bin. Double inclusion or omission changes denominators and can distort calibration plots.

```python
low = (confidence >= 0.5) & (confidence < 0.8)
high = (confidence >= 0.8) & (confidence <= 1)
assert (int(low.sum()), int(high.sum())) == (1, 3) and int((low | high).sum()) == 4
```

**Expected:** counts 1 and 3, total 4.

**Verify:** For *Check boundary membership*, a fresh-process check confirms `(int(low.sum()), int(high.sum())) == (1, 3)` and `int((low | high).sum()) == 4`.

## Exercise 5: Align paired errors

The question is: Compare dictionaries A q1=0, q2=1 and B q2=0, q1=1 by IDs.

A zero mean can hide opposite per-question outcomes. Pairing preserves which system fails on which case.

```python
a = {"q1": 0, "q2": 1}
b = {"q2": 0, "q1": 1}
ids = sorted(a)
diff = np.array([a[i] - b[i] for i in ids])
np.testing.assert_array_equal(diff, [-1, 1])
assert diff.mean() == 0
```

**Expected:** differences [-1, 1], mean 0.

**Verify:** For *Align paired errors*, a fresh-process check confirms `diff` equals `[-1, 1]` and `diff.mean() == 0`.

## Exercise 6: Reject incompatible tokenizer scores

The question is: Compare evaluation metadata with tokenizer hash v1 versus v2.

The same text can be divided into different numbers and identities of tokens. A new common evaluation unit is needed before treating the scores as directly comparable.

```python
left = {"tokenizer": "v1", "unit": "token"}
right = {"tokenizer": "v2", "unit": "token"}
assert left != right
```

**Expected:** direct token-loss comparison marked incompatible.

**Verify:** For *Reject incompatible tokenizer scores*, a fresh-process check confirms `left != right`.

## Review after comparison

Change one input to *Check boundary membership* and predict the result first; keep *Align paired errors* failing beside the repair. Log a missing NumPy separately from a wrong calibration value in `llm-027`.
