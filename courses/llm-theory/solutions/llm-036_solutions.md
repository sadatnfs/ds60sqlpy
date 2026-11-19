# llm-036: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Retrieval-augmented generation supplies external evidence to a language system, but retrieval itself does not guarantee correct answers. A retriever ranks documents; an answerer must still identify supported claims, handle missing evidence and avoid treating document text as instructions. This local lesson uses lexical overlap over six authored snippets, which is intentionally simple enough to audit. Authored relevance labels let retrieval recall be calculated separately from answer quality. A question with no relevant document should remain unanswered under the declared policy. A document containing command-like text is still data and must never trigger an action.

**Retrieval:** Ranking candidate evidence documents for a query.

**Recall at k:** Fraction of relevant documents present in the top-k results.

**Abstention:** Declining to answer when required evidence is missing.

## Reading the implementation

Tokenize the local query and documents into lowercase word sets. Score by set intersection size, sort descending score with document ID as a deterministic tie-breaker, and retain k. Recall@k is retrieved relevant IDs divided by all authored relevant IDs. It is undefined for a question with no relevant documents, so represent that case separately rather than claiming perfect recall.

## Exercise 1: Rank a different query

The question is: Query has sides against the same six documents with token overlap and ID tie-breaks; return the top 3.

Documents d1 and d4 share both query words, so the ID rule orders them. Document d5 shares only has, which ranks it above every document with no overlap.

```python
assert rank("has sides", docs, 3) == ["d1", "d4", "d5"]
```

**Expected:** top 3 IDs d1, d4, d5: two tied overlaps ordered by ID, then the single overlap.

**Verify:** In a fresh process, the exercise checks confirm `rank('has sides', docs, 3) == ['d1', 'd4', 'd5']`.

## Exercise 2: Measure recall with a tie-filled slot

The question is: Use relevant IDs d3 and d4 for the query round circle and compute recall at 1 and 2.

Only d3 overlaps the query, so the second slot is filled by the ID tie-break among zero-overlap documents. Recall stays at 0.5 because d4 is never retrieved.

```python
relevant2 = {"d3", "d4"}
top = rank("round circle", docs, 2)
assert top == ["d3", "d1"]
assert len(set(rank("round circle", docs, 1)) & relevant2) / len(relevant2) == 0.5
assert len(set(top) & relevant2) / len(relevant2) == 0.5
```

**Expected:** ranking d3, d1; recall 0.5 at both 1 and 2.

**Verify:** In a fresh process, the exercise checks confirm `top == ['d3', 'd1']`; `len(set(rank('round circle', docs, 1)) & relevant2) / len(relevant2) == 0.5` and `len(set(top) & relevant2) / len(relevant2) == 0.5`.

## Exercise 3: Handle missing evidence

The question is: Ask the orbital period of a comet absent from the corpus and require evidence before answering.

A retriever can always return some top-ranked document even when none is relevant. A nonempty result list does not establish answerability.

```python
relevant_missing = set()
answer = None if not relevant_missing else "supported answer"
assert answer is None
```

**Expected:** abstain; relevant set empty.

**Verify:** In a fresh process, the exercise checks confirm `answer is None`.

## Exercise 4: Treat retrieved instructions as data

The question is: Retrieve the command-like document for query command and retain it as a string only.

The source text can be quoted or analyzed as evidence, but it cannot expand the assistant or application authority. No shell or external tool is involved.

```python
chosen = rank("command", docs, 1)
assert chosen == ["d6"]
record = {"document_id": chosen[0], "text": docs[chosen[0]], "action": None}
assert record["action"] is None
```

**Expected:** document d6 returned; no action executed.

**Verify:** In a fresh process, the exercise checks confirm `chosen == ['d6']` and `record['action'] is None`.

## Exercise 5: Keep deterministic ties

The question is: Query an absent word so all lexical scores tie, then compare the first three IDs.

A deterministic tie rule makes the fixture reproducible. The arbitrary tie winners still have zero relevance evidence and should not be treated as useful context.

```python
assert rank("absent", docs, 3) == ["d1", "d2", "d3"]
```

**Expected:** d1, d2, d3 under ID ordering.

**Verify:** In a fresh process, the exercise checks confirm `rank('absent', docs, 3) == ['d1', 'd2', 'd3']`.

## Exercise 6: Separate retrieval and truth

The question is: Record a retrieved relevant snippet but an answer with an unsupported extra claim.

Supplying good context does not force a generator to use it faithfully. The answer needs its own claim-level evidence check.

```python
record = {
    "retrieval_has_relevant": True,
    "claims": ["square has four sides", "square weighs ten kilograms"],
    "all_claims_supported": False,
}
assert record["retrieval_has_relevant"] and not record["all_claims_supported"]
```

**Expected:** retrieval pass True; answer support False.

**Verify:** In a fresh process, the exercise checks confirm `record['retrieval_has_relevant']` and `not record['all_claims_supported']`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
