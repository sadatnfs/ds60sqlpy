# llm-014: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A count-based model is a useful baseline because its entire fitted state can be inspected. Each row of a transition table counts observed next tokens for a current token. Add-one smoothing gives every vocabulary token positive mass, including transitions never seen during training. Fit counts only on training documents, preserving document boundaries. Evaluate negative log probability over the active held-out transitions and report the denominator. Combine the baseline score with causal-prefix and contamination checks, since none substitutes for the others. This capstone produces an evidence notebook for a tiny vocabulary, not a claim of broad language-model capability.

**Bigram model:** A next-token distribution conditioned only on the preceding token.

**Smoothing:** A declared rule assigning mass to unobserved events.

**Token-weighted loss:** Total negative log likelihood divided by active target count.

## Reading the implementation

Initialize a square count matrix with zeros. For each document, update only adjacent pairs inside it. Add one to every cell and divide each row by its row sum plus vocabulary size. Index the probability table with held-out current/next token IDs, sum negative logs and divide by the number of transitions. Save counts before evaluation to demonstrate that assessment did not refit the model.

## Exercise 1: Fit a tiny baseline

The question is: Use vocabularyA,B,C and documentsABAB,AC; count transitions within documents.

The end of ABAB is not linked to the start of AC. Counts describe the specified training corpus, not all concatenations of its files.

```python
docs = [[0, 1, 0, 1], [0, 2]]
counts = np.zeros((3, 3), dtype=int)
for doc in docs:
    for a, b in zip(doc[:-1], doc[1:]):
        counts[a, b] += 1
assert counts[0, 1] == 2 and counts[1, 0] == 1 and counts[0, 2] == 1 and counts.sum() == 4
```

**Expected:** AtoB2,BtoA1,AtoC1; total4.

**Verify:** Compare the computed values or written argument with AtoB2,BtoA1,AtoC1; total4.

## Exercise 2: Normalize smoothed rows

The question is: Apply add-one smoothing to the count matrix.

Smoothing adds three pseudocounts to each denominator because there are three possible next tokens. Adding one only to the numerator would create excess probability mass.

```python
prob = (counts + 1) / (counts.sum(1, keepdims=True) + 3)
np.testing.assert_allclose(prob.sum(1), 1, atol=1e-12, rtol=0)
np.testing.assert_allclose(prob[2], [1 / 3] * 3, atol=1e-12, rtol=0)
```

**Expected:** row sums1; unseen C context is uniform.

**Verify:** Compare the computed values or written argument with row sums1; unseen C context is uniform.

## Exercise 3: Score held-out transitions

The question is: Evaluate held-out sequenceA,C,B using the frozen table.

The two transition probabilities are \(p(C\mid A)=2/6=1/3\) and \(p(B\mid C)=1/3\). Their negative log probabilities sum to \(-\log(1/3)-\log(1/3)=2\log 3\). Dividing this total negative log likelihood by two active targets gives mean loss \(\log 3\).

```python
saved = counts.copy()
held = [0, 2, 1]
nll = -sum(np.log(prob[a, b]) for a, b in zip(held[:-1], held[1:]))
np.testing.assert_allclose(nll, 2 * np.log(3), atol=1e-12, rtol=0)
assert len(held) - 1 == 2
```

**Expected:** 2 targets; NLL log3+log3.

**Verify:** Compare the computed values or written argument with 2 targets; NLL log3+log3.

## Exercise 4: Prove no assessment update

The question is: Compare the count matrix before and after scoring.

An evaluation helper should read fitted state without updating it. This identity check catches a stateful scorer that accidentally treats every observed transition as training data.

```python
np.testing.assert_array_equal(counts, saved)
```

**Expected:** counts unchanged exactly.

**Verify:** Compare the computed values or written argument with counts unchanged exactly.

## Exercise 5: Verify a causal prefix oracle

The question is: For zero-score attention values2,4,8 calculate prefix means and independently recompute each prefix.

This arithmetic verifies the simple information boundary independently of the baseline. A count model and an attention mechanism answer different architectural questions.

```python
values = np.array([2.0, 4.0, 8.0])
out = np.array([values[: i + 1].mean() for i in range(3)])
np.testing.assert_allclose(out, [2, 3, 14 / 3], atol=1e-12, rtol=0)
for cut in range(1, 4):
    np.testing.assert_allclose(
        out[:cut], [values[: i + 1].mean() for i in range(cut)], atol=1e-12, rtol=0
    )
```

**Expected:** outputs2,3,14/3.

**Verify:** Compare the computed values or written argument with outputs2,3,14/3.

## Exercise 6: Write the bounded comparison

The question is: Create a report with vocabulary size3,2 held-out targets and a limitation about unseen tasks.

A complete report can be modest. Counts, denominator and limitations let a reviewer understand exactly what the model was asked to do and what the result cannot establish.

```python
report = {
    "vocabulary": 3,
    "targets": 2,
    "mean_nll": float(nll / 2),
    "limitation": "Tiny authored corpus; unseen tasks remain untested.",
}
assert (
    np.isfinite(report["mean_nll"])
    and report["targets"] == 2
    and "untested" in report["limitation"]
)
```

**Expected:** report includes finite meanNLL and no broad competence claim.

**Verify:** Compare the computed values or written argument with report includes finite meanNLL and no broad competence claim.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
