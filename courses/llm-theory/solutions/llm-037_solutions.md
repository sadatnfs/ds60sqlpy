# llm-037: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A retrieval-and-answer pipeline has several failure opportunities. The retriever may miss a relevant document; the answerer may ignore available evidence; a claim may cite a document that does not support it; or the system may answer a question that should be declined. Evaluate these separately using stable question IDs, authored relevance labels and explicit claim spans. An oracle-context control supplies the relevant document directly, isolating answer behavior from retrieval quality. A correct final answer without support can still violate an evidence-grounded task. Conversely, an abstention can be correct when the corpus lacks the needed information.

**Retrieval miss:** Relevant evidence exists but is absent from retrieved context.

**Unsupported claim:** A statement not established by the cited evidence.

**Oracle context:** Known relevant context supplied to isolate answer behavior.

## Reading the implementation

Represent each question with relevant document IDs, retrieved IDs, answer correctness, claim support and abstention status. Compute named integer counters rather than a single opaque score. A support link needs both a document ID and the span that entails the claim. Oracle context changes only retrieval input, leaving the answer task and scoring rubric fixed.

## Exercise 1: Classify four cases

The question is: Useq1 retrieval miss,q2 unsupported answer,q3 correct abstention,q4 supported correct answer.

The categories locate different mechanisms. A shared final error rate would not reveal whether to improve retrieval, answer grounding or abstention policy.

```python
rows=[{'id':'q1','miss':True,'unsupported':False,'abstain':False,'correct':False},{'id':'q2','miss':False,'unsupported':True,'abstain':False,'correct':False},{'id':'q3','miss':False,'unsupported':False,'abstain':True,'correct':True},{'id':'q4','miss':False,'unsupported':False,'abstain':False,'correct':True}]
assert sum(r['miss'] for r in rows)==1 and sum(r['unsupported'] for r in rows)==1
```

**Expected:** one case in each named category.

**Verify:** Compare the computed values or written argument with one case in each named category.

## Exercise 2: Compute appropriate abstention

The question is: Count correct abstentions separately from answered correctness.

A system should not be punished for declining an unanswerable question when that is the declared policy. Report coverage alongside correctness.

```python
assert sum(r['abstain'] and r['correct'] for r in rows)==1
assert sum(not r['abstain'] and r['correct'] for r in rows)==1
```

**Expected:** 1 correct abstention;1 correct answered case.

**Verify:** Compare the computed values or written argument with 1 correct abstention;1 correct answered case.

## Exercise 3: Attach a claim span

The question is: Use documentd1 text red square has four sides and cite span square has four sides for that claim.

Substring presence checks citation location, while semantic support still requires reasoning. The fixture makes that reasoning straightforward; arbitrary text overlap would not be enough.

```python
text='red square has four sides'; claim={'document':'d1','span':'square has four sides','text':'The square has four sides.'}
assert claim['span'] in text
```

**Expected:** span appears verbatim and supports the stated claim.

**Verify:** Compare the computed values or written argument with span appears verbatim and supports the stated claim.

## Exercise 4: Reject a misleading citation

The question is: Cite the same document for claim the square weighs10kg.

Document existence is weaker than claim entailment. A valid-looking source link can accompany an unsupported statement.

```python
claim={'document':'d1','text':'The square weighs 10kg.'}; evidence={'d1':text}
assert claim['document'] in evidence and '10kg' not in evidence['d1']
```

**Expected:** citation exists but claim unsupported.

**Verify:** Compare the computed values or written argument with citation exists but claim unsupported.

## Exercise 5: Use an oracle-context control

The question is: Forq1 supply the authored relevant document and record whether the answer becomes correct.

If the answer still failed with oracle evidence, retrieval would not be the only problem. The control isolates a pipeline stage without changing the question.

```python
control={'id':'q1','oracle_context':True,'retrieval_miss':False,'answer_correct':True}
assert control['oracle_context'] and not control['retrieval_miss']
```

**Expected:** retrieval miss removed;answer outcome measured separately.

**Verify:** Compare the computed values or written argument with retrieval miss removed;answer outcome measured separately.

## Exercise 6: Preserve question identity

The question is: Join observed and oracle results byq1 and reject duplicate IDs in a score table.

Pairing by stable IDs preserves which intervention affected which question. Duplicate rows can inflate denominators or overstate improvement.

```python
ids=[r['id'] for r in rows]; assert len(ids)==len(set(ids))
bad=ids+['q1']; assert len(bad)!=len(set(bad))
```

**Expected:** one row per question;duplicateq1 detected.

**Verify:** Compare the computed values or written argument with one row per question;duplicateq1 detected.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
