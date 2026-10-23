# llm-applied-011: Grounded claims, citations and evidence-based abstention

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-010`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Grounded answering requires a connection between each substantive claim and supporting evidence. The central investigation is concrete: Answer the conversion-definition question from the metric document and its first sentence. The finish condition is statusanswered; one claim; citation slices the exact sentence. rate.3 with input counts preserved. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Grounded answering requires a connection between each substantive claim and supporting evidence. A citation that points to a real document is not enough if the document does not establish the claim. Preserve document version and character offsets so the cited span can be inspected. Distinguish source quotation, paraphrase and computed result. A deterministic calculation should cite its input records and method, while a quoted policy should cite the exact policy version.

This chapter implements an extractive subject-assistant baseline. It selects an authored supported span and returns it with metadata, or abstains when no supported answer exists. It is deliberately not called a generative LLM. The baseline makes the evidence contract testable before adding a model that may paraphrase or invent claims. Exact substring checks establish span integrity, not general semantic entailment; the fixture includes hand-authored claim-to-span labels for that separate support judgment. Conflicting versions and missing evidence should remain visible rather than be resolved by fluent guesswork.

## Design decisions and when to use this method

Use extractive baselines when citation precision matters and the domain answers are directly present in text. They provide a useful lower-complexity comparison for a generative system. Add generation when synthesis or explanation materially helps, but keep the same claim and citation contract. A generated paraphrase should be evaluated for support, and a computed conclusion should identify its data and method.

Do not confuse an answer containing many citations with a well-supported answer. One citation can be irrelevant, stale or contradicted by another source. Report conflict explicitly and define a source-precedence policy before evaluation. Abstention should be measured through both correctness and coverage: refusing every question avoids unsupported claims but fails the task. Tune the policy on validation cases containing answerable, unanswerable and conflicting-evidence questions.

## Vocabulary and concepts

**Grounded claim:** A statement linked to evidence that supports its content.

**Citation integrity:** Agreement between a citation span and the referenced source bytes.

**Entailment:** The evidence actually establishes the meaning of a claim.

**Abstention policy:** A rule for returning unknown instead of unsupported content.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-011/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-011.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-011.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

An answer record containsstatus, claims andcitations. Each citation includesdocument_id, version, start, end. Validate that the stored source slice equals the cited quote and that the claim ID is supported by the authored evidence map. For missing evidence, returnstatusunknown with an empty claim list and a reason. Do not use a low retrieval score alone as a universal answerability threshold without calibration.

## Worked example / walkthrough

### Example A: Return a supported extractive answer

The answer is a controlled source extract. It demonstrates citation construction without claiming that a model inferred the definition independently.

```python

def extractive_answer(document,start,end,claim_id):
    if document is None: return {'status':'unknown','claims':[],'citations':[],'reason':'missing evidence'}
    if not 0<=start<end<=len(document['text']): raise ValueError('valid nonempty source span required')
    return {'status':'answered','claims':[{'id':claim_id,'quote':document['text'][start:end]}],
            'citations':[{'document_id':document['id'],'version':document['version'],'start':start,'end':end}]}
text='Conversion rate equals purchases divided by eligible visits. Exclude test accounts.'
document={'id':'metric-v1','version':1,'text':text}; end=text.index('.')+1
answer=extractive_answer(document,0,end,'conversion-definition')
assert answer['status']=='answered' and len(answer['claims'])==1
assert text[answer['citations'][0]['start']:answer['citations'][0]['end']]==answer['claims'][0]['quote']
```

**Expected:** statusanswered; one claim; citation slices the exact sentence.

### Example B: Reject a corrupted span

A document ID alone would still look valid. Comparing the exact source slice detects a citation that no longer matches its claimed quote.

```python
bad={'quote':'Conversion rate is always one.'}
assert text[0:end]!=bad['quote']
```

**Expected:** citation integrity check returnsFalse.

### Example C: Abstain on missing evidence

An empty evidence set should not be converted into a confident answer from unrelated top-ranked text. The unknown result is a successful execution of the declared policy.

```python
unknown=extractive_answer(None,0,0,'comet-period')
assert unknown=={'status':'unknown','claims':[],'citations':[],'reason':'missing evidence'}
```

**Expected:** statusunknown; claims empty; reasonmissing evidence.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: statusanswered; one claim; citation slices the exact sentence. rate.3 with input counts preserved. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Return a supported extractive answer.** Answer the conversion-definition question from the metric document and its first sentence.
   **Expected:** statusanswered; one claim; citation slices the exact sentence.
   **Verify:** Save the assertion results for exercise 1, including statusanswered; one claim; citation slices the exact sentence.

2. **Reject a corrupted span.** Change the stored quote while leaving citation offsets unchanged.
   **Expected:** citation integrity check returnsFalse.
   **Verify:** Save the assertion results for exercise 2, including citation integrity check returnsFalse.

3. **Abstain on missing evidence.** Request an unsupported comet-period answer with no admitted supporting document.
   **Expected:** statusunknown; claims empty; reasonmissing evidence.
   **Verify:** Save the assertion results for exercise 3, including statusunknown; claims empty; reasonmissing evidence.

4. **Separate a valid citation from support.** Cite the metric document for a claim about statistical significance and inspect the authored support map.
   **Expected:** document exists but significance claim unsupported.
   **Verify:** Save the assertion results for exercise 4, including document exists but significance claim unsupported.

5. **Bind the source version.** Compare a citation requiringversion1 with a suppliedversion2 document.
   **Expected:** version mismatch blocks citation reuse.
   **Verify:** Save the assertion results for exercise 5, including version mismatch blocks citation reuse.

6. **Keep arithmetic separate from prose.** Compute3 purchases over10 visits and attach the deterministic result to an explanation record.
   **Expected:** rate.3 with input counts preserved.
   **Verify:** Save the assertion results for exercise 6, including rate.3 with input counts preserved.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Grounded claim, Citation integrity, Entailment using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-010` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-011, Grounded claims, citations and evidence-based abstention.
Read courses/llm-applied/guides/llm-applied-011.md and courses/llm-applied/lessons/llm-applied-011.py. Direct prerequisites: `llm-applied-010`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
