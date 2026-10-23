# llm-applied-011: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Grounded answering requires a connection between each substantive claim and supporting evidence. A citation that points to a real document is not enough if the document does not establish the claim. Preserve document version and character offsets so the cited span can be inspected. Distinguish source quotation, paraphrase and computed result. A deterministic calculation should cite its input records and method, while a quoted policy should cite the exact policy version.

This chapter implements an extractive subject-assistant baseline. It selects an authored supported span and returns it with metadata, or abstains when no supported answer exists. It is deliberately not called a generative LLM. The baseline makes the evidence contract testable before adding a model that may paraphrase or invent claims. Exact substring checks establish span integrity, not general semantic entailment; the fixture includes hand-authored claim-to-span labels for that separate support judgment. Conflicting versions and missing evidence should remain visible rather than be resolved by fluent guesswork.

**Grounded claim:** A statement linked to evidence that supports its content.

**Citation integrity:** Agreement between a citation span and the referenced source bytes.

**Entailment:** The evidence actually establishes the meaning of a claim.

**Abstention policy:** A rule for returning unknown instead of unsupported content.

## Reading the implementation

An answer record containsstatus, claims andcitations. Each citation includesdocument_id, version, start, end. Validate that the stored source slice equals the cited quote and that the claim ID is supported by the authored evidence map. For missing evidence, returnstatusunknown with an empty claim list and a reason. Do not use a low retrieval score alone as a universal answerability threshold without calibration.

## Exercise 1: Return a supported extractive answer

The question is: Answer the conversion-definition question from the metric document and its first sentence.

The answer is a controlled source extract. It demonstrates citation construction without claiming that a model inferred the definition independently.

```python
text='Conversion rate equals purchases divided by eligible visits. Exclude test accounts.'
document={'id':'metric-v1','version':1,'text':text}; end=text.index('.')+1
answer=extractive_answer(document,0,end,'conversion-definition')
assert answer['status']=='answered' and len(answer['claims'])==1
assert text[answer['citations'][0]['start']:answer['citations'][0]['end']]==answer['claims'][0]['quote']
```

**Expected:** statusanswered; one claim; citation slices the exact sentence.

**Verify:** Compare the computed values or written argument with statusanswered; one claim; citation slices the exact sentence.

## Exercise 2: Reject a corrupted span

The question is: Change the stored quote while leaving citation offsets unchanged.

A document ID alone would still look valid. Comparing the exact source slice detects a citation that no longer matches its claimed quote.

```python
bad={'quote':'Conversion rate is always one.'}
assert text[0:end]!=bad['quote']
```

**Expected:** citation integrity check returnsFalse.

**Verify:** Compare the computed values or written argument with citation integrity check returnsFalse.

## Exercise 3: Abstain on missing evidence

The question is: Request an unsupported comet-period answer with no admitted supporting document.

An empty evidence set should not be converted into a confident answer from unrelated top-ranked text. The unknown result is a successful execution of the declared policy.

```python
unknown=extractive_answer(None,0,0,'comet-period')
assert unknown=={'status':'unknown','claims':[],'citations':[],'reason':'missing evidence'}
```

**Expected:** statusunknown; claims empty; reasonmissing evidence.

**Verify:** Compare the computed values or written argument with statusunknown; claims empty; reasonmissing evidence.

## Exercise 4: Separate a valid citation from support

The question is: Cite the metric document for a claim about statistical significance and inspect the authored support map.

Citation location and semantic support are different gates. A real support evaluator needs a task rubric, human labels or a validated model rather than a document-existence test.

```python
support={'conversion-definition':{'metric-v1'},'test-account-exclusion':{'metric-v1'}}
assert document['id']=='metric-v1' and document['id'] not in support.get('significance',set())
```

**Expected:** document exists but significance claim unsupported.

**Verify:** Compare the computed values or written argument with document exists but significance claim unsupported.

## Exercise 5: Bind the source version

The question is: Compare a citation requiringversion1 with a suppliedversion2 document.

A source update can change meaning or offsets. Reusing old citations against new text can produce apparently precise but incorrect evidence links.

```python
citation=answer['citations'][0]; newer={**document,'version':2}
assert citation['version']!=newer['version']
```

**Expected:** version mismatch blocks citation reuse.

**Verify:** Compare the computed values or written argument with version mismatch blocks citation reuse.

## Exercise 6: Keep arithmetic separate from prose

The question is: Compute3 purchases over10 visits and attach the deterministic result to an explanation record.

The generated explanation must use the computed artifact rather than independently inventing a numerical answer. The formula also depends on the domain definition of eligible visits.

```python
calculation={'purchases':3,'visits':10}; value=calculation['purchases']/calculation['visits']
record={'computed_rate':value,'inputs':calculation,'method':'purchases / eligible visits'}
assert record['computed_rate']==.3 and record['inputs']['visits']==10
```

**Expected:** rate.3 with input counts preserved.

**Verify:** Compare the computed values or written argument with rate.3 with input counts preserved.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
