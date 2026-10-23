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

An answer record containsstatus, claims andcitations. Each citation includesdocument_id, version, start, end. The examples check source-slice equality and inspect an authored support map separately. The helper constructs the span record; a complete caller must enforce semantic claim support before accepting it. For missing evidence, returnstatusunknown with an empty claim list and a reason. Do not use a low retrieval score alone as a universal answerability threshold without calibration.

## Separate the four questions behind a citation

A citation can answer four different questions: does the referenced document exist, does the stored span reproduce the quoted text, does that text support the stated claim, and is the source itself reliable/applicable? Passing an earlier question does not imply a later one. An exact quote from an obsolete policy has perfect span integrity and can still be the wrong answer to a current-policy question.

The helper extractive_answer constructs a record from a supplied document, span and claim ID. It validates a nonempty in-range span or returns unknown when no document is supplied. It does not look up the claim ID in a semantic support map. The separate exercise inspects an authored support map to show why that gate is necessary. A real caller must establish support before treating the constructed record as a validated grounded answer.

For the metric fixture, the first sentence ends at the first period. The returned quote includes that period and the citation stores document_id, version, start, end. Changing the quote to “Conversion rate is always one” while retaining the span fails the slice-equality test. Changing the claim to statistical significance while retaining the correct metric quote passes slice integrity but fails semantic support. These counterexamples localize two different failures.

An answer can also preserve the words while changing the scope. Suppose a source says “Exclude test accounts from this experiment's eligible population.” A generated claim that all company metrics exclude test accounts adds a universal scope not established by that sentence. Citation existence and overlapping vocabulary are weak proxies for entailment. Human rubrics or a separately validated support evaluator must assess the actual proposition.

Computed claims need a different lineage. The result0.3 comes from purchases 3 divided by eligible visits 10. A useful record preserves those inputs, the formula, relevant definition version and calculation output. The source definition supports the formula; it does not itself supply the measured count values. A generated explanation should consume the computed artifact rather than recomputing an approximate number from memory. Neither the ratio nor the definition establishes a causal treatment effect.

Abstention is a decision under uncertainty about support. In a simple illustrative utility model, a correct supported answer earns benefit B, an incorrect or unsupported answer incurs cost C, and abstention has utility zero. If p were a calibrated probability of meeting the complete answer contract, answering is favored when pB-(1-p)C>0, or p>C/(B+C). This is a derivation under explicit assumptions, not permission to interpret a retrieval score as p. Additional answer costs or asymmetric abstention costs change the threshold.

Coverage and conditional quality must be reported together. If a system answers six of ten questions and five answers satisfy the full contract, coverage is0.6 and accepted-answer accuracy is5/6. Reporting only5/6 hides the four refusals; reporting only five successes hides whether the failures were unsupported answers or appropriate unknowns. The final task population and cost policy determine which tradeoff is useful.

Conflicting sources need a policy too. A newer version may supersede an older one for current questions, but historical questions can require the older rule. Two simultaneously applicable sources may disagree. Preserve the conflict and source-precedence rule rather than using fluent synthesis to erase it. A supported quote from each side can establish that a conflict exists without establishing which side is correct.

### Interview reasoning with explanatory answers

**Does an exact substring prove an answer is grounded?** It proves a quote matches a declared source span. The question's proposition, source applicability and support relation require additional checks.

**Why can a correct answer still fail this task?** It may be guessed from prior knowledge or use unauthorized/stale evidence. An evidence-grounded task includes the support and access contract, not only the final words.

**How can abstention improve a system without hiding failure?** Declare its policy and report coverage, supported accuracy and failure categories. Keep refusals on answerable questions visible beside successful refusals on unanswerable ones.

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
