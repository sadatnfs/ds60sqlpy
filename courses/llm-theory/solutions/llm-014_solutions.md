# llm-014: explanatory solutions

Read these capstone: a small language-model evidence notebook answers after attempting *Count transitions in new documents* through *Write the bounded comparison*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Score held-out transitions* points to one step. `llm-014_solution.py` holds the assertions; this page explains how they test bigram model. Then try *Write the bounded comparison* on a fresh input you chose before looking.

## Mechanism review

A count-based model is a useful baseline because its entire fitted state can be inspected. Each row of a transition table counts observed next tokens for a current token. Add-one smoothing gives every vocabulary token positive mass, including transitions never seen during training. Fit counts only on training documents, preserving document boundaries. Evaluate negative log probability over the active held-out transitions and report the denominator. Combine the baseline score with causal-prefix and contamination checks, since none substitutes for the others. This capstone produces an evidence notebook for a tiny vocabulary, not a claim of broad language-model capability.

**Bigram model:** A next-token distribution conditioned only on the preceding token.

**Smoothing:** A declared rule assigning mass to unobserved events.

**Token-weighted loss:** Total negative log likelihood divided by active target count.

## Reading the implementation

Initialize a square count matrix with zeros. For each document, update only adjacent pairs inside it. Add one to every cell and divide each row by its row sum plus vocabulary size. Index the probability table with held-out current/next token IDs, sum negative logs and divide by the number of transitions. Save counts before evaluation to demonstrate that assessment did not refit the model.

## Exercise 1: Count transitions in new documents

The question is: Use vocabulary A=0, B=1, C=2 and the documents CAAB and BCA; count transitions within each document.

The first document ends in B and the second starts with B. Concatenating them would invent a B to B transition, so the zero in that cell checks the document boundary.

```python
docs2 = [[2, 0, 0, 1], [1, 2, 0]]
counts2 = np.zeros((3, 3), dtype=int)
for doc in docs2:
    for a, b in zip(doc[:-1], doc[1:]):
        counts2[a, b] += 1
assert counts2[2, 0] == 2 and counts2[0, 0] == 1 and counts2[0, 1] == 1 and counts2[1, 2] == 1
assert counts2.sum() == 5 and counts2[1, 1] == 0
```

**Expected:** C to A: 2, A to A: 1, A to B: 1, B to C: 1; total 5; no B to B transition across the document boundary.

**Verify:** For *Count transitions in new documents*, a fresh-process check confirms `counts2[2, 0] == 2`; `counts2[0, 0] == 1`; `counts2[0, 1] == 1`; `counts2[1, 2] == 1` and 2 further checks.

## Exercise 2: Predict two smoothed rows

The question is: Apply add-one smoothing to the new counts and predict the rows for contexts A and C.

Each row adds one pseudo-count per vocabulary item, so its denominator is the row count plus 3. Context A has two observed transitions and context C has two, but their distributions differ because the counts fall in different cells.

```python
prob2 = (counts2 + 1) / (counts2.sum(1, keepdims=True) + 3)
np.testing.assert_allclose(prob2[0], [2 / 5, 2 / 5, 1 / 5], atol=1e-12, rtol=0)
np.testing.assert_allclose(prob2[2], [3 / 5, 1 / 5, 1 / 5], atol=1e-12, rtol=0)
```

**Expected:** row A [2/5, 2/5, 1/5]; row C [3/5, 1/5, 1/5].

**Verify:** For *Predict two smoothed rows*, a fresh-process check confirms `prob2[0]` matches `[2 / 5, 2 / 5, 1 / 5]` within 1e-12 and `prob2[2]` matches `[3 / 5, 1 / 5, 1 / 5]` within 1e-12.

## Exercise 3: Score held-out transitions

The question is: Evaluate held-out sequence A, C, B using the frozen table.

The two transition probabilities are \(p(C\mid A)=2/6=1/3\) and \(p(B\mid C)=1/3\). Their negative log probabilities sum to \(-\log(1/3)-\log(1/3)=2\log 3\). Dividing this total negative log likelihood by two active targets gives mean loss \(\log 3\).

```python
saved = counts.copy()
held = [0, 2, 1]
nll = -sum(np.log(prob[a, b]) for a, b in zip(held[:-1], held[1:]))
np.testing.assert_allclose(nll, 2 * np.log(3), atol=1e-12, rtol=0)
assert len(held) - 1 == 2
```

**Expected:** 2 targets; NLL log 3+log 3.

**Verify:** For *Score held-out transitions*, a fresh-process check confirms `nll` matches `2 * np.log(3)` within 1e-12 and `len(held) - 1 == 2`.

## Exercise 4: Prove no assessment update

The question is: Compare the count matrix before and after scoring.

An evaluation helper should read fitted state without updating it. This identity check catches a stateful scorer that accidentally treats every observed transition as training data.

```python
np.testing.assert_array_equal(counts, saved)
```

**Expected:** counts unchanged exactly.

**Verify:** For *Prove no assessment update*, a fresh-process check confirms `counts` equals `saved`.

## Exercise 5: Verify a causal prefix oracle

The question is: For zero-score attention values 2, 4, 8 calculate prefix means and independently recompute each prefix.

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

**Expected:** outputs 2, 3, 14/3.

**Verify:** For *Verify a causal prefix oracle*, a fresh-process check confirms `out` matches `[2, 3, 14 / 3]` within 1e-12 and for every `cut` in `range(1, 4)`, `out[:cut]` matches `[values[:i + 1].mean() for i in range(cut)]` within 1e-12.

## Exercise 6: Write the bounded comparison

The question is: Create a report with vocabulary size 3, 2 held-out targets and a limitation about unseen tasks.

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

**Expected:** report includes finite mean NLL and no broad competence claim.

**Verify:** For *Write the bounded comparison*, a fresh-process check confirms `np.isfinite(report['mean_nll'])`, `report['targets'] == 2` and `'untested' in report['limitation']`.

## Review after comparison

Change one input to *Prove no assessment update* and predict the result first; keep *Verify a causal prefix oracle* failing beside the repair. Log a missing NumPy separately from a wrong bigram model value in `llm-014`.
