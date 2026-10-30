# llm-013: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A decoder can have perfect causal attention and still be evaluated on leaked data. Next-token training pairs each input position with the following token; copying the input as its own label creates an easier identity task. A split must also keep document families together and exclude duplicates across partitions. Tokenizer fitting, prompt selection and preprocessing can consume evaluation information before model training begins. The fixture separates these failure modes so a passing mask test is not mistaken for a complete experiment audit. Stable document identity and explicit shifted arrays provide stronger evidence than a plausible loss curve.

**Shifted target:** The next token paired with the current input position.

**Contamination:** Assessment information entering training or selection.

**Document family:** Related records treated as one split unit.

## Reading the implementation

For token sequence ids, use ids[:-1] as inputs and ids[1:] as targets. Hash raw or explicitly normalized text according to a declared policy. Compare both exact hashes and known family IDs across partitions; exact hashing cannot detect paraphrases on its own. Validate disjoint groups before fitting any vocabulary or count model.

## Exercise 1: Construct next-token pairs

The question is: Shift IDs[2,5,7,3] into input and label arrays.

There are three target events in a four-token sequence. The final token has no next token unless an explicit end marker is included in the original sequence.

```python
ids = np.array([2, 5, 7, 3])
inputs = ids[:-1]
labels = ids[1:]
np.testing.assert_array_equal(inputs, [2, 5, 7])
np.testing.assert_array_equal(labels, [5, 7, 3])
```

**Expected:** inputs[2,5,7],labels[5,7,3].

**Verify:** Compare the computed values or written argument with inputs[2,5,7],labels[5,7,3].

## Exercise 2: Expose identity labels

The question is: Compare copied-input labels with the proper shifted targets.

A model trained to reproduce its current token is not being tested on next-token prediction. A causal mask allows the current input, so it cannot detect this objective error.

```python
copied = inputs.copy()
assert np.count_nonzero(copied != labels) == 3
```

**Expected:** all three copied labels differ from the target fixture.

**Verify:** Compare the computed values or written argument with all three copied labels differ from the target fixture.

## Exercise 3: Detect exact duplicates

The question is: Hash texts alpha beta and an identical copy placed in another split.

File identity is not content identity. Exact hashing catches byte-identical duplicates but does not establish that differently worded texts are independent.

```python
import hashlib

train = {"a": "alpha beta"}
valid = {"copy": "alpha beta"}
hash_text = lambda text: hashlib.sha256(text.encode()).hexdigest()
assert {hash_text(t) for t in train.values()} & {hash_text(t) for t in valid.values()}
```

**Expected:** same SHA256 despite different filenames.

**Verify:** Compare the computed values or written argument with same SHA256 despite different filenames.

## Exercise 4: Detect family leakage

The question is: Assign documentsa andb to familyF across train and validation.

Known source families can catch related material that hashes differently. The grouping policy should be frozen before outcome inspection.

```python
families = {"a": "F", "b": "F", "c": "G"}
assert {families["a"]} & {families["b"]} == {"F"}
```

**Expected:** family intersection containsF.

**Verify:** Compare the computed values or written argument with family intersection containsF.

## Exercise 5: Freeze a vocabulary

The question is: Fit a vocabulary from training words alpha,beta and encode validation-only gamma without adding it.

A vocabulary update during validation changes the fitted representation. Unknown-token handling must be an explicit frozen policy.

```python
vocab = {"alpha": 0, "beta": 1}
before = dict(vocab)
unknown = vocab.get("gamma", -1)
assert unknown == -1 and vocab == before
```

**Expected:** vocabulary remains alpha,beta; gamma is unknown.

**Verify:** Compare the computed values or written argument with vocabulary remains alpha,beta; gamma is unknown.

## Exercise 6: Count active targets

The question is: Count targets across documents of lengths4 and2 without creating a transition between documents.

Concatenating documents without a boundary policy invents a transition from the end of one source to the start of another. Per-document pairing preserves the declared prediction unit.

```python
documents = [[2, 5, 7, 3], [8, 3]]
pairs = [(a, b) for doc in documents for a, b in zip(doc[:-1], doc[1:])]
assert len(pairs) == 4 and (3, 8) not in pairs
```

**Expected:** \(3+1=4\) targets, not5.

**Verify:** Compare the computed values or written argument with \(3+1=4\) targets, not5.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
