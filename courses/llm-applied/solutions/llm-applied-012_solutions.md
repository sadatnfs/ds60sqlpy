# llm-applied-012: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A RAG evaluation should identify where the pipeline failed. Retrieval recall asks whether relevant evidence entered the candidate or context set. Ranking metrics ask how early it appeared. Answer correctness asks whether the response satisfies the question. Support asks whether its claims are established by supplied evidence. Appropriate abstention asks whether the system declined cases lacking evidence. These measurements can disagree, and combining them into one number too early hides actionable information.

An oracle-context control supplies the authored relevant evidence directly while leaving the question and answer rubric unchanged. If the answer improves, retrieval was a bottleneck. If it still fails, the answer stage or task definition needs attention. The local fixture uses saved deterministic answer labels, not fabricated model execution. Every result is keyed by question ID and linked to an authored relevance set. Questions with no relevant documents need a separate answerability category because recall has an empty denominator.

**Retrieval recall:** Coverage of authored relevant evidence in retrieved results.

**Reciprocal rank:** Inverse position of the first relevant result.

**Oracle-context control:** Known relevant evidence supplied to isolate answer behavior.

**Failure taxonomy:** Separate named categories locating pipeline problems.

## Reading the implementation

Recall@k is the number of relevant IDs retrieved divided by total relevant IDs. Reciprocal rank is1 divided by the first relevant rank, or0 when none appears. For unanswerable questions, returnNone for recall and score abstention separately. Keep retrieval misses, unsupported claims, incorrect answers and appropriate abstentions as distinct counters. Compare observed and oracle results by the same question ID.

## Exercise 1: Calculate recall and reciprocal rank

The question is: Use relevant IDs a, c and retrieved b, c, a.

Both relevant documents are retrieved, but the first appears second. Recall alone would not reveal that ordering.

```python
recall,rr=retrieval_metrics(['b','c','a'],{'a','c'})
assert recall==1 and rr==.5
```

**Expected:** recall1; reciprocal rank.5.

**Verify:** Compare the computed values or written argument with recall1; reciprocal rank.5.

## Exercise 2: Measure a retrieval miss

The question is: Use relevant a and retrieved b, c.

The answer stage cannot use evidence absent from its context. This is a retrieval failure even if a language model guesses the answer from prior training.

```python
assert retrieval_metrics(['b','c'],{'a'})==(0.,0.)
```

**Expected:** recall0; reciprocal rank 0.

**Verify:** Compare the computed values or written argument with recall0; reciprocal rank 0.

## Exercise 3: Handle an unanswerable question

The question is: Use an empty relevant set and a saved abstention result.

A denominator of zero does not mean perfect recall. The correct task behavior is evaluated through an explicit answerability and abstention policy.

```python
assert retrieval_metrics(['b'],set())==(None,0.)
result={'question':'q-missing','answerable':False,'abstained':True}; assert not result['answerable'] and result['abstained']
```

**Expected:** recallNone; appropriate abstentionTrue.

**Verify:** Compare the computed values or written argument with recallNone; appropriate abstentionTrue.

## Exercise 4: Separate support from correctness

The question is: Record a correct-looking answer whose cited context does not support it.

A system can answer from memorized knowledge or chance while failing an evidence-grounded contract. Both outcomes should remain visible.

```python
saved={'question':'q1','correct':True,'supported':False,'retrieval_miss':True}
assert saved['correct'] and not saved['supported']
```

**Expected:** correctTrue but supportedFalse.

**Verify:** Compare the computed values or written argument with correctTrue but supportedFalse.

## Exercise 5: Apply an oracle-context control

The question is: Compare q1 observed incorrect with oracle-context correct under the same rubric.

The unchanged failure onq2 shows that retrieval is not always the sole bottleneck. The control should not silently change the question or answer criteria.

```python
observed={'q1':0,'q2':0}; oracle={'q1':1,'q2':0}
assert oracle['q1']-observed['q1']==1 and oracle['q2']-observed['q2']==0
```

**Expected:** paired improvement1 for q1.

**Verify:** Compare the computed values or written argument with paired improvement1 for q1.

## Exercise 6: Reject duplicate result identities

The question is: Validate one score row per question and inject a duplicateq1.

Duplicated question rows can inflate counts and distort paired comparisons. Identity checks belong before calculating aggregate metrics.

```python
ids=['q1','q2','q3']; assert len(ids)==len(set(ids))
bad=ids+['q1']; assert len(bad)!=len(set(bad))
```

**Expected:** duplicate ID detected.

**Verify:** Compare the computed values or written argument with duplicate ID detected.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
