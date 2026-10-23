# llm-applied-008: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Hybrid retrieval combines complementary candidate generators. Lexical ranking can preserve exact terms, while embedding ranking can recover paraphrases. Their raw scores are usually on different scales, so adding them without calibration can let one dominate for arbitrary numerical reasons. Reciprocal-rank fusion uses rank positions instead: each list contributes1/(constant+rank) to a candidate. A document appearing near the top of both lists accumulates evidence from both methods. This is a ranking heuristic, not a probability model.

Reranking evaluates a smaller candidate set with a more expensive scoring function, often a cross-encoder that jointly reads query and document. This lesson uses a transparent deterministic relevance feature as a reranker so the candidate-stage limitation is visible. If a relevant document never enters the candidate set, no reranker can recover it. Measure candidate recall before judging reranker quality, and keep the query, candidate IDs, scores and final order in the evaluation trace.

**Hybrid retrieval:** Combining candidate rankings from different retrieval mechanisms.

**RRF:** Reciprocal-rank fusion, combining inverse rank contributions.

**Reranker:** A second-stage scorer applied to a bounded candidate set.

**Candidate recall:** Relevant evidence coverage before reranking.

## Reading the implementation

Use one-based ranks and a positive fusion constant. Deduplicate each input ranking before assigning contributions so repeated IDs do not gain extra votes. Sum contributions by document ID and sort with an explicit ID tie-breaker. The reranker receives only admitted candidates and returns a new ordering; it must not expand access scope or silently fetch new documents.

## Exercise 1: Fuse two rankings

The question is: Fuse lexical[a, b, c] and dense[b, d, a] with constant60.

Documentb receives ranks2 and1, whilea receives1 and3. The difference comes from rank evidence rather than incompatible raw score scales.

```python
ranked=rrf([['a','b','c'],['b','d','a']],60)
assert [key for key,score in ranked][:2]==['b','a']
```

**Expected:** b ranks first, a second.

**Verify:** Compare the computed values or written argument with b ranks first, a second.

## Exercise 2: Inspect one exact contribution

The question is: Calculate the fused score ofb as1/62+1/61.

Writing the formula independently makes off-by-one rank errors visible. Zero-based rank would change every denominator.

```python
scores=dict(ranked)
assert abs(scores['b']-(1/62+1/61))<1e-12
```

**Expected:** computed b score equals that sum within1e-12.

**Verify:** Compare the computed values or written argument with computed b score equals that sum within1e-12.

## Exercise 3: Prevent duplicate votes

The question is: Repeatb inside one ranking and compare with its deduplicated form.

One retrieval list should contribute one rank per document. Otherwise a buggy candidate generator can inflate a result by emitting duplicates.

```python
assert rrf([['a','b','b','c']],60)==rrf([['a','b','c']],60)
```

**Expected:** fusion result unchanged.

**Verify:** Compare the computed values or written argument with fusion result unchanged.

## Exercise 4: Rerank a bounded candidate set

The question is: Use candidatesa, b, c with authored relevance features0, 2, 1 and sort descending feature then ID.

This deterministic feature is an inspectable stand-in for a learned reranker score. It is not described as a cross-encoder or a language model.

```python
features={'a':0,'b':2,'c':1}; candidates=['a','b','c']
reranked=sorted(candidates,key=lambda key:(-features[key],key))
assert reranked==['b','c','a']
```

**Expected:** orderb, c, a.

**Verify:** Compare the computed values or written argument with orderb, c, a.

## Exercise 5: Expose a candidate-recall ceiling

The question is: Declare relevant documentd but supply only candidatesa, b, c.

A reranker can rearrange available evidence but cannot repair an upstream omission without another retrieval step. This distinction guides where to invest debugging effort.

```python
relevant={'d'}; assert not set(candidates)&relevant
assert 'd' not in reranked
```

**Expected:** candidate recall0 and reranker cannot return d.

**Verify:** Compare the computed values or written argument with candidate recall0 and reranker cannot return d.

## Exercise 6: Reject invalid fusion policy

The question is: Use constant0 or a repeated non-string identifier and apply the declared validation.

Validation keeps the rank formula and identity space explicit. A production implementation also needs bounds on list length and candidate count.

```python
for rankings,k,kind in [([['a']],0,ValueError),([[1]],60,TypeError)]:
    try: rrf(rankings,k)
    except kind: pass
    else: raise AssertionError('invalid fusion input')
```

**Expected:** ValueError for nonpositive constant; TypeError for non-string ID.

**Verify:** Compare the computed values or written argument with ValueError for nonpositive constant; TypeError for non-string ID.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
