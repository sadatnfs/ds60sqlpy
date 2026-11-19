# llm-037: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A retrieval-and-answer pipeline has several failure opportunities. The retriever may miss a relevant document; the answerer may ignore available evidence; a claim may cite a document that does not support it; or the system may answer a question that should be declined. Evaluate these separately using stable question IDs, authored relevance labels and explicit claim spans. An oracle-context control supplies the relevant document directly, isolating answer behavior from retrieval quality. A correct final answer without support can still violate an evidence-grounded task. Conversely, an abstention can be correct when the corpus lacks the needed information.

**Retrieval miss:** Relevant evidence exists but is absent from retrieved context.

**Unsupported claim:** A statement not established by the cited evidence.

**Oracle context:** Known relevant context supplied to isolate answer behavior.

## Reading the implementation

Represent each question with relevant document IDs, retrieved IDs, answer correctness, claim support and abstention status. Compute named integer counters rather than a single opaque score. A support link needs both a document ID and the span that entails the claim. Oracle context changes only retrieval input, leaving the answer task and scoring rubric fixed.

## Exercise 1: Classify five new cases

The question is: Use r1 and r2 retrieval misses, r3 an unsupported answer, r4 a correct supported answer and r5 an abstention on an answerable question.

An abstention is only correct when the question cannot be answered from the evidence. Recording r5 as an incorrect abstention keeps caution from being counted as success.

```python
rows2 = [
    {"id": "r1", "miss": True, "unsupported": False, "abstain": False, "correct": False},
    {"id": "r2", "miss": True, "unsupported": False, "abstain": False, "correct": False},
    {"id": "r3", "miss": False, "unsupported": True, "abstain": False, "correct": False},
    {"id": "r4", "miss": False, "unsupported": False, "abstain": False, "correct": True},
    {"id": "r5", "miss": False, "unsupported": False, "abstain": True, "correct": False},
]
assert sum(r["miss"] for r in rows2) == 2 and sum(r["unsupported"] for r in rows2) == 1
assert (
    sum(r["abstain"] for r in rows2) == 1 and sum(r["abstain"] and r["correct"] for r in rows2) == 0
)
```

**Expected:** 2 retrieval misses, 1 unsupported answer, 1 abstention that was not appropriate and 1 correct answer.

**Verify:** In a fresh process, the exercise checks confirm `sum((r['miss'] for r in rows2)) == 2`, `sum((r['unsupported'] for r in rows2)) == 1`, `sum((r['abstain'] for r in rows2)) == 1` and `sum((r['abstain'] and r['correct'] for r in rows2)) == 0`.

## Exercise 2: Predict coverage and answered accuracy

The question is: From the five new cases, compute the share of questions answered and the accuracy among answered questions.

Four of five questions were answered and only r4 was correct. Reporting coverage beside answered accuracy prevents abstentions from silently raising or lowering the headline score.

```python
answered = [r for r in rows2 if not r["abstain"]]
assert len(answered) / len(rows2) == 0.8
assert sum(r["correct"] for r in answered) / len(answered) == 0.25
```

**Expected:** coverage 0.8; answered accuracy 0.25.

**Verify:** In a fresh process, the exercise checks confirm `len(answered) / len(rows2) == 0.8` and `sum((r['correct'] for r in answered)) / len(answered) == 0.25`.

## Exercise 3: Attach a claim span

The question is: Use document d1 text red square has four sides and cite span square has four sides for that claim.

Substring presence checks citation location, while semantic support still requires reasoning. The fixture makes that reasoning straightforward; arbitrary text overlap would not be enough.

```python
text = "red square has four sides"
claim = {"document": "d1", "span": "square has four sides", "text": "The square has four sides."}
assert claim["span"] in text
```

**Expected:** span appears verbatim and supports the stated claim.

**Verify:** In a fresh process, the exercise checks confirm `claim['span'] in text`.

## Exercise 4: Reject a misleading citation

The question is: Cite the same document for claim the square weighs 10 kg.

Document existence is weaker than claim entailment. A valid-looking source link can accompany an unsupported statement.

```python
claim = {"document": "d1", "text": "The square weighs 10kg."}
evidence = {"d1": text}
assert claim["document"] in evidence and "10kg" not in evidence["d1"]
```

**Expected:** citation exists but claim unsupported.

**Verify:** In a fresh process, the exercise checks confirm `claim['document'] in evidence` and `'10kg' not in evidence['d1']`.

## Exercise 5: Use an oracle-context control

The question is: For q1 supply the authored relevant document and record whether the answer becomes correct.

If the answer still failed with oracle evidence, retrieval would not be the only problem. The control isolates a pipeline stage without changing the question.

```python
control = {"id": "q1", "oracle_context": True, "retrieval_miss": False, "answer_correct": True}
assert control["oracle_context"] and not control["retrieval_miss"]
```

**Expected:** retrieval miss removed; answer outcome measured separately.

**Verify:** In a fresh process, the exercise checks confirm `control['oracle_context']` and `not control['retrieval_miss']`.

## Exercise 6: Preserve question identity

The question is: Join observed and oracle results by q1 and reject duplicate IDs in a score table.

Pairing by stable IDs preserves which intervention affected which question. Duplicate rows can inflate denominators or overstate improvement.

```python
ids = [r["id"] for r in rows]
assert len(ids) == len(set(ids))
bad = ids + ["q1"]
assert len(bad) != len(set(bad))
```

**Expected:** one row per question; duplicate q1 detected.

**Verify:** In a fresh process, the exercise checks confirm `len(ids) == len(set(ids))` and `len(bad) != len(set(bad))`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
