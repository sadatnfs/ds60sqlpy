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

## Audit the complete local path without inventing missing integration

At construction, the Assistant copies only documents whose scope appears in the supplied set. A public instance therefore lacks private-v1 in its internal document dictionary. answer then maps a fixed question key to a document ID, retrieves that admitted document and returns its first sentence with versioned character offsets. An unsupported or excluded target returns unknown with no restricted document identity in the response.

This is an explicit lookup-and-extraction baseline. It does not embed a natural-language question, execute BM25, learn a retrieval policy or generate a new paraphrase. The controlled map makes identity and disclosure behavior transparent. A broader natural-language interface would need its own intent mapping and retrieval evaluation rather than inheriting success from these exact keys.

| Capability | Local capstone evidence | Separate evidence still needed for a larger assistant |
| --- | --- | --- |
| Scope filtering | Restricted target absent from public instance | Authenticated dynamic policy integration |
| Source extraction | Exact first-sentence slice and version | General claim support and conflict handling |
| Numerical calculation | Validated3/10=0.3 and invalid-count rejection | Real input provenance and analysis design |
| Task statuses | Three fixed expected statuses match | Independent question families and utility |
| Model generation | Not invoked by this baseline | Actual candidate outputs and grounding evaluation |

The three status cases include one answered definition and two correct unknowns: missing comet evidence and a restricted threshold under public scope. Status accuracy is3/3, but answer coverage is1/3. That is appropriate for these authored cases; it is not evidence that every future question is answered correctly. A high status score can coexist with low usefulness if the evaluation contains too many easy refusals.

Citation integrity is checked separately by slicing the original document. This catches a corrupted span even if status remains answered. It does not prove that the first sentence contains every caveat needed by a future question. The metric document's second sentence excludes test accounts, while the returned first sentence gives the formula. A question requiring eligibility details would need the additional span; the current fixed key is not a general policy-synthesis test.

The conversion helper accepts integer purchases and visits with 0<=purchases<=visits and a positive denominator. Its0.3 output is descriptive arithmetic under the stated counting rule. Source evidence defines eligible visits, but actual eligible counts still need validated observations. Neither this ratio nor the assistant's explanation establishes sampling uncertainty or a causal effect.

The instance captures its permitted documents at construction. It does not dynamically reevaluate revocations, implement the previous chapter's freshness gate or connect to a real identity provider. Those earlier components illustrate contracts that a larger service should integrate and test. Their separate existence in the course does not mean this small class already exercises them end to end.

The optional pretrained recipe supplies another real but separate result: training, reload and generation executed, while the formula in its generated answer was incorrect despite supplied evidence. The capstone's local receipt correctly says pretrained_generation_executed=False for this particular run. It must not be read as a global denial that the separate recipe ran, or as a reason to discard its quality failure. A release report should reference both artifacts and retain their distinct scopes.

### Interview reasoning with explanatory answers

**Why can a successful capstone still conclude no-go?** Its local contracts pass while required operational and domain-quality evidence remains absent or has failed. A bounded success is useful without satisfying every release criterion.

**What would justify replacing the extractive stage with generation?** Measured utility on cases requiring synthesis or explanation, with access, supported claims, citations, deterministic calculations and appropriate abstention preserved. Fluency alone does not establish that improvement.

**How do you know whether all previous components are integrated?** Trace the actual call path and execution artifacts. A list of available modules or completed lessons is not an end-to-end runtime receipt.

## Exercise 1: Answer a supported domain definition

The question is: Ask the public assistant forconversion_definition.

The baseline uses an explicit authored mapping so its evidence contract is transparent. A generative proposal stage would need separate support validation before returning the same answer shape.

```python
assistant=Assistant(DOCUMENTS,{'public'},'corpus-v1')
answer=assistant.answer('conversion_definition')
assert answer['status']=='answered' and answer['citation']['document_id']=='metric-v1'
assert 'eligible visits' in answer['text']
```

**Expected:** answered with metric-v1 citation and source text.

**Verify:** Compare the computed values or written argument with answered with metric-v1 citation and source text.

## Exercise 2: Abstain on missing evidence

The question is: Ask forcomet_period, which has no supporting corpus entry.

Returning an unrelated top-ranked document would not make the question answerable. The abstention is the correct result under the task contract.

```python
missing=assistant.answer('comet_period')
assert missing['status']=='unknown' and missing['reason']=='missing evidence'
```

**Expected:** unknown with missing evidence reason.

**Verify:** Compare the computed values or written argument with unknown with missing evidence reason.

## Exercise 3: Enforce access before answering

The question is: Ask a public-only assistant forrestricted_threshold, then ask a separately authorized assistant.

The public trace does not reveal the restricted document ID. Access is enforced by trusted metadata filtering before evidence selection.

```python
public=assistant.answer('restricted_threshold'); privileged=Assistant(DOCUMENTS,{'public','restricted'},'corpus-v1').answer('restricted_threshold')
assert public['status']=='unknown' and privileged['citation']['document_id']=='private-v1'
```

**Expected:** public unknown; authorizedanswercitesprivate-v1.

**Verify:** Compare the computed values or written argument with public unknown; authorizedanswercitesprivate-v1.

## Exercise 4: Compute a data-science result deterministically

The question is: Calculate3 purchases over10 eligible visits and reject11 purchases over10 visits.

The assistant can explain the metric using the retrieved definition, but the value comes from validated arithmetic. This does not establish a causal effect or sampling uncertainty.

```python
assert conversion(3,10)==.3
try: conversion(11,10)
except ValueError: pass
else: raise AssertionError('invalid conversion counts')
```

**Expected:** rate.3; invalid counts raise ValueError.

**Verify:** Compare the computed values or written argument with rate.3; invalid counts raise ValueError.

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

The question is: Record local fixture acceptance while leaving pretrained generation, real identity integration and production readiness unverified.

A successful local baseline is meaningful progress without being a deployment claim. The next evidence is explicit:actual local model outputs, held-out domain questions and real integration boundary tests.

```python
receipt={'local_fixture_pass':all(results),'pretrained_generation_executed':False,'real_identity_integration_verified':False,'production_go':'no-go','scope':'offline extractive subject-assistant baseline'}
assert receipt['local_fixture_pass'] and receipt['production_go']=='no-go' and not receipt['pretrained_generation_executed']
```

**Expected:** local_fixture_pass True; production_go no-go.

**Verify:** Compare the computed values or written argument with local_fixture_pass True; production_go no-go.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
