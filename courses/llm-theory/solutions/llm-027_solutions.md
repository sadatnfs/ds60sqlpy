# llm-027: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Evaluation needs compatible units. Token-weighted loss averages over token events; averaging document means gives equal weight to documents regardless of length. Calibration compares predicted confidence with observed frequency within declared bins, always reporting bin counts. A confident prediction can be wrong, and a low average error can coexist with poor confidence estimates. Empty bins contain no evidence and should not be assigned a zero observed rate. Comparing perplexity across incompatible tokenizers changes the event definition, so it cannot be treated as a direct quality ranking. Saved predictions let these issues be studied without executing an online model.

**Calibration:** Agreement between predicted confidence and observed frequency.

**Bin count:** Number of observations supporting a calibration summary.

**Comparable unit:** An event definition shared by the quantities being compared.

## Reading the implementation

Store per-event confidence and a boolean correctness outcome. Use explicit half-open bin boundaries, with the final bin including1. Compute each bin count, mean confidence and observed accuracy separately. For loss, retain sums and counts until the final division. Join model comparisons by stable event IDs rather than relying on array order.

## Exercise 1: Weight token losses

The question is: Combine document mean losses1 and3 with token counts1 and3.

The two statistics answer different questions. Neither should be labelled average loss without naming its weighting unit.

```python
means=np.array([1.,3.]); counts=np.array([1,3])
assert np.average(means,weights=counts)==2.5 and means.mean()==2
```

**Expected:** token mean 2.5; document mean 2.

**Verify:** Compare the computed values or written argument with token mean 2.5; document mean 2.

## Exercise 2: Build a calibration bin

The question is: Use confidences.6,.8,.8,1 with correctness1,1,0,1 in a single bin.

The gap between confidence and frequency is observable for this small sample. Its sampling uncertainty remains large, so the bin is not a population guarantee.

```python
confidence=np.array([.6,.8,.8,1.]); correct=np.array([1,1,0,1])
assert len(confidence)==4; np.testing.assert_allclose(confidence.mean(),.8,atol=1e-12,rtol=0); assert correct.mean()==.75
```

**Expected:** count4,mean confidence.8,accuracy.75.

**Verify:** Compare the computed values or written argument with count4,mean confidence.8,accuracy.75.

## Exercise 3: Represent an empty bin

The question is: Select confidence values below.5 and summarize without fabricating a rate.

Zero accuracy would imply observed failures, while perfect accuracy would imply observed successes. An empty bin supports neither statement.

```python
mask=confidence<.5; summary={'count':int(mask.sum()),'accuracy':None if not mask.any() else float(correct[mask].mean())}
assert summary=={'count':0,'accuracy':None}
```

**Expected:** count0 and accuracyNone.

**Verify:** Compare the computed values or written argument with count0 and accuracyNone.

## Exercise 4: Check boundary membership

The question is: Use bins[.5,.8) and[.8,1] on the fixture.

A value exactly on a boundary must enter only one bin. Double inclusion or omission changes denominators and can distort calibration plots.

```python
low=(confidence>=.5)&(confidence<.8); high=(confidence>=.8)&(confidence<=1)
assert (int(low.sum()),int(high.sum()))==(1,3) and int((low|high).sum())==4
```

**Expected:** counts1 and3, total4.

**Verify:** Compare the computed values or written argument with counts1 and3, total4.

## Exercise 5: Align paired errors

The question is: Compare dictionariesA q1=0,q2=1 and B q2=0,q1=1 by IDs.

A zero mean can hide opposite per-question outcomes. Pairing preserves which system fails on which case.

```python
a={'q1':0,'q2':1}; b={'q2':0,'q1':1}; ids=sorted(a)
diff=np.array([a[i]-b[i] for i in ids]); np.testing.assert_array_equal(diff,[-1,1]); assert diff.mean()==0
```

**Expected:** differences[-1,1], mean0.

**Verify:** Compare the computed values or written argument with differences[-1,1], mean0.

## Exercise 6: Reject incompatible tokenizer scores

The question is: Compare evaluation metadata with tokenizer hashv1 versusv2.

The same text can be divided into different numbers and identities of tokens. A new common evaluation unit is needed before treating the scores as directly comparable.

```python
left={'tokenizer':'v1','unit':'token'}; right={'tokenizer':'v2','unit':'token'}
assert left!=right
```

**Expected:** direct token-loss comparison marked incompatible.

**Verify:** Compare the computed values or written argument with direct token-loss comparison marked incompatible.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
