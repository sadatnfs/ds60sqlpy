# llm-applied-024: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A subject-assistant capstone should demonstrate an entire evidence path: task admission, authorized retrieval, versioned source selection, grounded output, deterministic data-science computation and independent evaluation. The final system must also say when it does not know. A polished response alone cannot show whether the answer came from permitted, current evidence or whether a numerical claim was actually calculated.

The default capstone assembles an offline extractive RAG baseline over authored data-science method snippets. It is explicitly an assistant architecture and test fixture, not a production LLM. The pretrained-model recipe can supply a local generative proposal stage after separate preparation, but every proposal must still pass the same evidence and tool boundaries. Actual tiny-model SFT and adapters were trained in earlier chapters; their held-out receipts belong beside this pipeline evaluation rather than being replaced by invented answer records. This chapter tests supported definitions, unknown questions, restricted knowledge and exact conversion-rate arithmetic, then makes a bounded go/no-go decision.

**End-to-end evidence path:** The trace from admitted input through sources and tools to a checked answer.

**Extractive baseline:** An answerer returning controlled source text rather than generated prose.

**Acceptance gate:** A required condition for a bounded release decision.

**Subject-assistant artifact:** The corpus,policies,code,evaluation and model identities needed for review.

## Reading the implementation

The Assistant class stores versioned documents and an allowed-scope set. It filters before matching an authored question-to-evidence map, returns a cited source span for supported definitions, and abstains otherwise. A separate conversion tool validates integer counts and a positive denominator. Each answer trace names the corpus version and admitted document ID. Evaluation uses fixed question IDs and expected statuses, not a self-reported confidence score. The final decision requires all boundary checks and reports unexecuted production surfaces explicitly.

## Exercise 1: Answer a supported domain definition

The question is: Ask the public assistant forconversion_definition.

The baseline uses an explicit authored mapping so its evidence contract is transparent. A generative proposal stage would need separate support validation before returning the same answer shape.

```python
assistant=Assistant(DOCUMENTS,{'public'},'corpus-v1')
answer=assistant.answer('conversion_definition')
assert answer['status']=='answered' and answer['citation']['document_id']=='metric-v1'
assert 'eligible visits' in answer['text']
```

**Expected:** answered withmetric-v1 citation and source text.

**Verify:** Compare the computed values or written argument with answered withmetric-v1 citation and source text.

## Exercise 2: Abstain on missing evidence

The question is: Ask forcomet_period, which has no supporting corpus entry.

Returning an unrelated top-ranked document would not make the question answerable. The abstention is the correct result under the task contract.

```python
missing=assistant.answer('comet_period')
assert missing['status']=='unknown' and missing['reason']=='missing evidence'
```

**Expected:** unknown withmissing evidence reason.

**Verify:** Compare the computed values or written argument with unknown withmissing evidence reason.

## Exercise 3: Enforce access before answering

The question is: Ask a public-only assistant forrestricted_threshold, then ask a separately authorized assistant.

The public trace does not reveal the restricted document ID. Access is enforced by trusted metadata filtering before evidence selection.

```python
public=assistant.answer('restricted_threshold'); privileged=Assistant(DOCUMENTS,{'public','restricted'},'corpus-v1').answer('restricted_threshold')
assert public['status']=='unknown' and privileged['citation']['document_id']=='private-v1'
```

**Expected:** publicunknown; authorizedanswercitesprivate-v1.

**Verify:** Compare the computed values or written argument with publicunknown; authorizedanswercitesprivate-v1.

## Exercise 4: Compute a data-science result deterministically

The question is: Calculate3 purchases over10 eligible visits and reject11 purchases over10 visits.

The assistant can explain the metric using the retrieved definition, but the value comes from validated arithmetic. This does not establish a causal effect or sampling uncertainty.

```python
assert conversion(3,10)==.3
try: conversion(11,10)
except ValueError: pass
else: raise AssertionError('invalid conversion counts')
```

**Expected:** rate.3; invalid counts raiseValueError.

**Verify:** Compare the computed values or written argument with rate.3; invalid counts raiseValueError.

## Exercise 5: Evaluate fixed task and boundary cases

The question is: Score supported, missing andrestricted-public questions against their expected statuses.

Status accuracy alone would miss a corrupted citation. The independent source-slice check verifies a second part of the contract.

```python
cases=[('conversion_definition','answered'),('comet_period','unknown'),('restricted_threshold','unknown')]
results=[assistant.answer(question)['status']==expected for question,expected in cases]
assert results==[True,True,True]
citation=answer['citation']; source=next(d for d in DOCUMENTS if d['id']==citation['document_id'])
assert source['text'][citation['start']:citation['end']]==answer['text']
```

**Expected:** 3 of 3 status contracts pass; citation integrity checked separately.

**Verify:** Compare the computed values or written argument with 3 of 3 status contracts pass; citation integrity checked separately.

## Exercise 6: Issue a bounded capstone decision

The question is: Record local fixture acceptance while leaving pretrained generation, realidentity integration andproduction readiness unverified.

A successful local baseline is meaningful progress without being a deployment claim. The next evidence is explicit:actual local model outputs, held-out domain questions and real integration boundary tests.

```python
receipt={'local_fixture_pass':all(results),'pretrained_generation_executed':False,'real_identity_integration_verified':False,'production_go':'no-go','scope':'offline extractive subject-assistant baseline'}
assert receipt['local_fixture_pass'] and receipt['production_go']=='no-go' and not receipt['pretrained_generation_executed']
```

**Expected:** local_fixture_passTrue; production_gono-go.

**Verify:** Compare the computed values or written argument with local_fixture_passTrue; production_gono-go.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
