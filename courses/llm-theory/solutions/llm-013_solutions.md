# llm-013: explanatory solutions

Read these a leakage audit before a model score answers after attempting *Shift a batch of two sequences* through *Count active targets*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Detect exact duplicates* points to one step. `llm-013_solution.py` holds the assertions; this page explains how they test shifted target. Then try *Count active targets* on a fresh input you chose before looking.

## Mechanism review

A decoder can have perfect causal attention and still be evaluated on leaked data. Next-token training pairs each input position with the following token; copying the input as its own label creates an easier identity task. A split must also keep document families together and exclude duplicates across partitions. Tokenizer fitting, prompt selection and preprocessing can consume evaluation information before model training begins. The fixture separates these failure modes so a passing mask test is not mistaken for a complete experiment audit. Stable document identity and explicit shifted arrays provide stronger evidence than a plausible loss curve.

**Shifted target:** The next token paired with the current input position.

**Contamination:** Assessment information entering training or selection.

**Document family:** Related records treated as one split unit.

## Reading the implementation

For token sequence ids, use ids[:-1] as inputs and ids [1:] as targets. Hash raw or explicitly normalized text according to a declared policy. Compare both exact hashes and known family IDs across partitions; exact hashing cannot detect paraphrases on its own. Validate disjoint groups before fitting any vocabulary or count model.

## Exercise 1: Shift a batch of two sequences

The question is: Shift IDs [[4, 1, 6, 2, 9], [3, 3, 8, 0, 5]] along the time axis into inputs and labels.

The shift is applied to the time axis of every sequence; the batch axis is untouched. Each sequence loses one prediction target because its final token has no successor.

```python
batch = np.array([[4, 1, 6, 2, 9], [3, 3, 8, 0, 5]])
x_in = batch[:, :-1]
y_out = batch[:, 1:]
assert x_in.shape == y_out.shape == (2, 4)
np.testing.assert_array_equal(y_out, [[1, 6, 2, 9], [3, 8, 0, 5]])
```

**Expected:** inputs and labels both shape (2, 4); labels [[1, 6, 2, 9], [3, 8, 0, 5]].

**Verify:** For *Shift a batch of two sequences*, a fresh-process check confirms `x_in.shape == y_out.shape == (2, 4)` and `y_out` equals `[[1, 6, 2, 9], [3, 8, 0, 5]]`.

## Exercise 2: Predict a partly hidden label bug

The question is: For the second sequence, compare copied-input labels with the shifted targets and predict how many positions agree.

A repeated token makes the identity-label bug agree with the true target at one position. A check that only looked for any agreement would pass; counting all disagreements still exposes the bug.

```python
row = batch[1]
copied_row = row[:-1]
target_row = row[1:]
assert int(np.count_nonzero(copied_row == target_row)) == 1
assert int(np.count_nonzero(copied_row != target_row)) == 3
```

**Expected:** copied labels agree once (the repeated 3) and differ at the other 3 positions.

**Verify:** For *Predict a partly hidden label bug*, a fresh-process check confirms `int(np.count_nonzero(copied_row == target_row)) == 1` and `int(np.count_nonzero(copied_row != target_row)) == 3`.

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

**Verify:** For *Detect exact duplicates*, a fresh-process check confirms `{hash_text(t) for t in train.values()} & {hash_text(t) for t in valid.values()}`.

## Exercise 4: Detect family leakage

The question is: Assign documents a and b to family F across train and validation.

Known source families can catch related material that hashes differently. The grouping policy should be frozen before outcome inspection.

```python
families = {"a": "F", "b": "F", "c": "G"}
assert {families["a"]} & {families["b"]} == {"F"}
```

**Expected:** family intersection contains F.

**Verify:** For *Detect family leakage*, a fresh-process check confirms `{families['a']} & {families['b']} == {'F'}`.

## Exercise 5: Freeze a vocabulary

The question is: Fit a vocabulary from training words alpha, beta and encode validation-only gamma without adding it.

A vocabulary update during validation changes the fitted representation. Unknown-token handling must be an explicit frozen policy.

```python
vocab = {"alpha": 0, "beta": 1}
before = dict(vocab)
unknown = vocab.get("gamma", -1)
assert unknown == -1 and vocab == before
```

**Expected:** vocabulary remains alpha, beta; gamma is unknown.

**Verify:** For *Freeze a vocabulary*, a fresh-process check confirms `unknown == -1` and `vocab == before`.

## Exercise 6: Count active targets

The question is: Count targets across documents of lengths 4 and 2 without creating a transition between documents.

Concatenating documents without a boundary policy invents a transition from the end of one source to the start of another. Per-document pairing preserves the declared prediction unit.

```python
documents = [[2, 5, 7, 3], [8, 3]]
pairs = [(a, b) for doc in documents for a, b in zip(doc[:-1], doc[1:])]
assert len(pairs) == 4 and (3, 8) not in pairs
```

**Expected:** \(3+1=4\) targets, not 5.

**Verify:** For *Count active targets*, a fresh-process check confirms `len(pairs) == 4` and `(3, 8) not in pairs`.

## Review after comparison

Change one input to *Detect family leakage* and predict the result first; keep *Freeze a vocabulary* failing beside the repair. Log a missing NumPy separately from a wrong shifted target value in `llm-013`.
