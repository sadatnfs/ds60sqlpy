# llm-applied-002: Data-science task contracts and structured extraction

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 180 minutes. Direct prerequisites: `llm-applied-001`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Structured extraction turns text into typed records, but valid JSON is only the first boundary. The central investigation is concrete: Validate visits 10, purchases 3 and assignment_unit account. The finish condition is conversion rate 0.3. invalid unit rejected; account remains explicit. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Structured extraction turns text into typed records, but valid JSON is only the first boundary. A record can have all required keys and still contain a fabricated measurement, an impossible count or a unit mismatch. The task should distinguish unsupported fields from explicit missing values. This lesson extracts a small study record with visits, purchases andassignment_unit. The reference uses deterministic parsing of a tightly specified authored format so every accepted value can be traced to source text. It is an extraction baseline, not a language model. A future LLM proposal must pass the same validation before downstream analysis.

For data science, preserving units and uncertainty is essential. Purchases cannot exceed visits under the stated one-purchase-per-visit fixture. A missing outcome is not zero. A study randomized by account cannot be analyzed as though every repeated visit were independently assigned. The schema therefore carries semantic assumptions alongside numeric fields. Once accepted, deterministic code calculates conversion rate; generated prose must cite that computed value rather than invent a second calculation.

## Design decisions and when to use this method

Use a strict extraction boundary when downstream code depends on typed fields, especially counts, money, dates or identifiers. An LLM can propose fields from varied prose, but the acceptance policy should be independent of that model. Keep raw source, proposed record, validation result and corrected record as separate artifacts. A rejected record may require human review or a documented fallback; it should not disappear silently from the denominator.

Do not ask an extraction model to invent a p-value or causal conclusion from a short narrative. Those outputs require actual data and a valid analysis design. If the source says “significant” without a test definition, preserve that as a quoted source claim rather than converting it into a verified statistical result. Measure exact-match accuracy, missing-field behavior and unsupported-field rates on held-out document families. Schema validity alone rewards well-formed hallucinations.

## Vocabulary and concepts

**Schema validity:** Structural and type conformance of a proposed record.

**Semantic validity:** Consistency with domain rules such as units and count bounds.

**Provenance span:** The source character interval supporting an extracted field.

**Abstention:** Returning an explicit unknown result when evidence is absent.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-002/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-002.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-002.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Parse JSON into a dictionary, require exactly the allowed keys, and reject booleans where an integer count is required because Python bool is a subclass ofint. Validate0<=purchases<=visits and require a positive denominator before computing a rate. UseNone only where the schema explicitly permits missingness. The extract helper recognizes the authored grammar and returns source spans so a field can be traced to the exact characters that supplied it.

## Worked example / walkthrough

### Example A: Validate a correct proposal

The denominator and unit are known before division. This calculation is deterministic and does not depend on the wording of an explanation.

```python
import re
def validate(value):
    if not isinstance(value,dict): raise TypeError('object required')
    if set(value)!={'visits','purchases','assignment_unit'}: raise ValueError('exact fields required')
    if any(type(value[k]) is not int for k in ('visits','purchases')): raise TypeError('integer counts required')
    if not 0<=value['purchases']<=value['visits']: raise ValueError('inconsistent counts')
    if value['assignment_unit']!='account': raise ValueError('account assignment required')
    return dict(value)
def rate(record):
    if record['visits']==0: raise ValueError('positive denominator required')
    return record['purchases']/record['visits']
def extract(text):
    match=re.fullmatch(r'Visits: (\d+); Purchases: (\d+); Unit: (account)',text)
    if match is None: raise ValueError('unsupported source grammar')
    result=validate({'visits':int(match[1]),'purchases':int(match[2]),'assignment_unit':match[3]})
    return result,{name:match.span(i) for i,name in enumerate(['visits','purchases','assignment_unit'],1)}
record=validate({'visits':10,'purchases':3,'assignment_unit':'account'})
assert rate(record)==.3
```

**Expected:** conversion rate 0.3.

### Example B: Reject a plausible but impossible record

A JSON parser cannot detect this domain contradiction. The validation rule catches a semantically invalid proposal even though its keys and primitive types are correct.

```python
try: validate({'visits':2,'purchases':3,'assignment_unit':'account'})
except ValueError: pass
else: raise AssertionError('impossible counts accepted')
```

**Expected:** ValueError for inconsistent counts.

### Example C: Trace extracted values to text

Offsets refer to the original source string. Normalizing text before saving offsets without a mapping would make citations point at the wrong characters.

```python
text='Visits: 10; Purchases: 3; Unit: account'
parsed,spans=extract(text)
assert parsed==record
assert text[slice(*spans['visits'])]=='10' and text[slice(*spans['purchases'])]=='3'
```

**Expected:** values10 and3; each span slices the original digits.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: conversion rate 0.3. invalid unit rejected; account remains explicit. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Validate a correct proposal.** Validate visits 10, purchases 3 and assignment_unit account.
   **Expected:** conversion rate 0.3.
   **Verify:** Save the assertion results for exercise 1, including conversion rate 0.3.

2. **Reject a plausible but impossible record.** Validate visits 2 and purchases 3 under the declared one-purchase-per-visit policy.
   **Expected:** ValueError for inconsistent counts.
   **Verify:** Save the assertion results for exercise 2, including ValueError for inconsistent counts.

3. **Trace extracted values to text.** Parse the source text Visits: 10; Purchases: 3; Unit: account and retain source spans.
   **Expected:** values10 and3; each span slices the original digits.
   **Verify:** Save the assertion results for exercise 3, including values10 and3; each span slices the original digits.

4. **Distinguish missing from zero.** Submit a record with purchases=None and compare it with a real zero-purchase record.
   **Expected:** None is rejected by this strict schema; zero is accepted with rate 0.
   **Verify:** Save the assertion results for exercise 4, including None is rejected by this strict schema; zero is accepted with rate 0.

5. **Reject boolean and extra fields.** Submit visits=True, then add an undeclared p_value field to a valid proposal.
   **Expected:** TypeError for a boolean count; ValueError for an extra field.
   **Verify:** Save the assertion results for exercise 5, including TypeError for a boolean count; ValueError for an extra field.

6. **Preserve the assignment unit.** Attempt to replace account with visit and explain why the independence assumption cannot be inferred from the count fields.
   **Expected:** invalid unit rejected; account remains explicit.
   **Verify:** Save the assertion results for exercise 6, including invalid unit rejected; account remains explicit.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Schema validity, Semantic validity, Provenance span using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-001` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Python json documentation](https://docs.python.org/3.12/library/json.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-002, Data-science task contracts and structured extraction.
Read courses/llm-applied/guides/llm-applied-002.md and courses/llm-applied/lessons/llm-applied-002.py. Direct prerequisites: `llm-applied-001`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
