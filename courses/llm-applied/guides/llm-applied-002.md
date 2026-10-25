# llm-applied-002: Data-science task contracts and structured extraction

## Level and prerequisites

Beginner; approximately 180 minutes. Direct prerequisites: `llm-applied-001`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Structured extraction is the bridge between language and analysis. This chapter follows an analyst's source note through parsing, validation, provenance and aggregation, showing why a well-formed record can still be scientifically misleading.

## Purpose and mental model

Structured extraction turns text into typed records, but valid JSON is only the first boundary. A record can have all required keys and still contain a fabricated measurement, an impossible count or a unit mismatch. The task should distinguish unsupported fields from explicit missing values. This lesson extracts a small study record with visits, purchases and assignment_unit. The reference uses deterministic parsing of a tightly specified authored format so every accepted value can be traced to source text. It is an extraction baseline, not a language model. A future LLM proposal must pass the same validation before downstream analysis.

For data science, preserving units and uncertainty is essential. Purchases cannot exceed visits under the stated one-purchase-per-visit fixture. A missing outcome is not zero. A study randomized by account cannot be analyzed as though every repeated visit were independently assigned. The schema therefore carries semantic assumptions alongside numeric fields. Once accepted, deterministic code calculates conversion rate; generated prose must cite that computed value rather than invent a second calculation.

## From a source note to a defensible data row

The Methods Desk receives a study note containing counts, a description of eligibility and a statement about account-level randomization. A language model may be useful because the note is not always written in a fixed template. Before that flexibility can help, the application must decide what an accepted row means. Otherwise the model can produce neat JSON that downstream code interprets incorrectly.

Consider the sentence “Three purchases were observed in ten eligible visits; assignment was by account.” There are at least three distinct pieces of information: a numerator count, a denominator count and a study-design unit. The phrase eligible visits depends on an eligibility definition. The phrase assignment by account identifies where treatment was assigned, not necessarily how a reported descriptive ratio was weighted. Preserving those distinctions is part of extraction, even before any statistical model is fitted.

A useful interface separates the source observation from the proposed interpretation. The raw source and its version remain available. The proposal names fields and supporting spans. A validator checks the schema and domain constraints. A validated record can then be admitted to a particular calculation. The result is another artifact with its own inputs and method. If a reviewer later disputes the eligibility rule, the system can revisit that decision without pretending the original text contained a different fact.

## A schema expresses analytical commitments

The runnable example's counts assume at most one counted purchase per eligible visit. That is why purchases cannot exceed visits. In another application, a visit can contain multiple item purchases, so the same inequality would reject valid data. The correct repair would be to change the metric definition and schema deliberately, perhaps to items_per_visit, rather than loosening a validator while continuing to call the result a conversion probability.

Units need similar care. A value of 12 can mean 12 visits,12 accounts,12 dollars or 12 percentage points. A schema that stores only value=12 cannot recover the distinction from the number. Dates can identify event time, reporting time or an effective policy date. Identifiers can contain leading zeros that must survive serialization. The choice of primitive type is therefore a modeling decision, not merely a programming convenience.

Some ambiguity should remain explicit. If a source says “about ten visits,” converting it into an exact integer 10 may be inappropriate. If it says “no purchases were reported,” that can mean an observed zero or an absence of reporting. A production extraction schema may need separate value,status,unit and support fields. The narrow fixture intentionally rejects missing counts so the reader can see that unknown is not silently replaced by zero. Expanding the schema should preserve that distinction.

Validation cannot prove that a plausible value was stated in the source. An invented count of three still satisfies \(0\le 3\le 10\). Provenance is therefore a second contract: each accepted field needs a source span or another recorded evidence link. The span proves where the proposed value came from; interpreting that phrase correctly remains a semantic responsibility.

## When individually correct rows produce a wrong aggregate

Suppose account A has one eligible visit and one purchase, while account B has nine eligible visits and two purchases. The visit-weighted rate is \(\frac{3}{10}=0.3\). The equally weighted account mean is(1+2/9)/2=11/18, about 0.6111. Neither number is an arithmetic error. The first weights each visit equally; the second weights each account equally and averages its within-account ratio.

An assistant asked for “average account conversion” must resolve which quantity is intended. It cannot infer the estimand solely from the existence of an assignment_unit field. If randomization is by account, a treatment-effect analysis also needs the assignment and account identities, not just a pooled count ratio. Repeated visits from the same account can share behavior and treatment. Treating every visit as an independently randomized unit would create an unjustified uncertainty calculation.

The distinction becomes especially important after extraction. A source may report one row per account, one row per visit or one summary row per study. Joining those rows to another table can duplicate observations. A correct extractor does not protect a later analysis from grain changes. Carry identifiers, counts and aggregation rules through the pipeline so the final statistic can be reconstructed from its actual observational units.

## Rejection changes the analyzed population

Imagine 100 source notes. The extractor accepts 80 and rejects 20 because their outcome language is ambiguous. Among accepted notes, field accuracy is excellent. That result does not establish that the accepted 80 represent all 100. Perhaps unsuccessful studies describe outcomes less consistently, or older reports use a different format. Excluding them can change the estimated result even when every retained value is correct.

The evaluation should therefore keep separate counts for all eligible sources, accepted records, rejected records and unsupported accepted fields. If 72 of 80 accepted records are entirely correct, accepted-record accuracy is 0.9 and acceptance coverage is 0.8. The count of fully correct accepted records per all eligible sources is 72/100=0.72. These describe different properties of the system. The intended workflow determines whether a rejected record goes to human review, a second parser, an explicit unknown state or a separately reported exclusion.

Repeated correction can create its own leakage. If every final assessment error is turned into another prompt example, the assessment is now influencing system selection. Keep document families and annotation revisions traceable so a new model version is not evaluated only on patterns that motivated its development. Agreement with a schema is easy to score; trustworthy extraction requires representative sources and a support rubric.

## Connect the record back to the analyst's question

The practical result is a chain of named quantities. The source supplies a count claim. The extractor proposes a typed value and span. The validator admits it under declared units and rules. The calculation produces a ratio. The explanation can then say what the ratio describes and which stronger conclusions remain unsupported. This chain lets a data scientist localize a disagreement to extraction, eligibility, weighting or interpretation.

The reference parser is deliberately narrower than an LLM. Its exact grammar supplies a reliable arithmetic and provenance baseline before a more flexible proposal stage is introduced. A language model earns value when it correctly handles useful variation while preserving the same acceptance contract. Flexibility that merely hides unsupported fields is not an improvement in the analytical system.

## Design decisions and when to use this method

Use a strict extraction boundary when downstream code depends on typed fields, especially counts, money, dates or identifiers. An LLM can propose fields from varied prose, but the acceptance policy should be independent of that model. Keep raw source, proposed record, validation result and corrected record as separate artifacts. A rejected record may require human review or a documented fallback; it should not disappear silently from the denominator.

Do not ask an extraction model to invent a p-value or causal conclusion from a short narrative. Those outputs require actual data and a valid analysis design. If the source says “significant” without a test definition, preserve that as a quoted source claim rather than converting it into a verified statistical result. Measure exact-match accuracy, missing-field behavior and unsupported-field rates on held-out document families. Schema validity alone rewards well-formed hallucinations.

Define the accepted record schema before asking a model to populate it. Keep source parsing, record validation and eligibility for a particular calculation as separate stages. This fixture permits a zero-visit/zero-purchase record structurally, but rate() rejects its zero denominator. That distinction lets a system preserve a real zero-activity observation without inventing a rate.

When extraction is used before statistical analysis, retain rejected records and their reasons. An acceptance filter can change the analyzed population. A high accuracy among accepted records should therefore be accompanied by acceptance coverage and a review of which document families were excluded.

## Vocabulary and concepts

**Schema validity:** Structural and type conformance of a proposed record.

**Semantic validity:** Consistency with domain rules such as units and count bounds.

**Provenance span:** The source character interval supporting an extracted field.

**Abstention:** Returning an explicit unknown result when evidence is absent.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-002/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-002.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Validate an already decoded dictionary, require exactly the allowed keys, and reject booleans where an integer count is required because Python bool is a subclass of int. Validate 0<=purchases<=visits and require a positive denominator before computing a rate. Use None only where the schema explicitly permits missingness. The extract helper recognizes the authored grammar and returns source spans so a field can be traced to the exact characters that supplied it.

## Follow one value from text to an analysis unit

The helper extract recognizes a deliberately narrow source grammar. It uses a full-string regular expression and returns digit spans from the original string. The helper validate accepts an already decoded Python dictionary; it is not a JSON parser. A JSON response from a future language model would first need parsing and then the same independent acceptance checks. These interfaces should not be collapsed into the claim “the model returned valid data.”

For the literal text `Visits: 10; Purchases: 3; Unit: account`, the visit digits occupy the half-open character interval[8, 10), the purchase digit[23, 24), and the unit[32, 39). Slicing the original string at those boundaries recovers 10, 3 and account. The integer conversion changes representation, while the stored span keeps its provenance. If preprocessing removes spaces before extracting offsets, those new offsets cannot be applied directly to the original string without a mapping.

The record check accepts exactly three keys and requires type(value) to be int for both counts. Python's Boolean subtype relationship makes this stricter than a plain isinstance(value, int) test. A True visit count would otherwise become one in arithmetic even though the source proposed a logical value. Extra fields are also rejected, so a model cannot quietly insert an unsupported p_value alongside otherwise valid counts.

The domain constraint 0<=purchases<=visits assumes at most one counted purchase per eligible visit. It is not a universal business rule. If the real outcome counts multiple items purchased in a visit, the ratio may legitimately exceed one and needs a different name and contract. A validator should make that modeling choice explicit instead of treating every ratio as a probability.

For the valid fixture, \(\frac{3}{10}=0.3\) describes purchases per eligible visit. The assignment_unit field says the experimental assignment is by account. It does not transform the arithmetic denominator into accounts, nor does it make 10 visits independently randomized. Repeated observations within accounts require account identities and a suitable analysis design for uncertainty. The three extracted fields alone cannot recover that information.

Aggregation adds another distinction. Suppose one account has 1 purchase in 1 visit and another has 1 purchase in 9 visits. The pooled visit rate is \(\frac{2}{10}=0.2\). The equally weighted mean of account-specific rates is(1+1/9)/2=5/9, about 0.556. Both calculations are valid for their declared estimands; they answer different questions. Calling both “average conversion” hides the weighting rule. The extraction schema should preserve enough units and identities to support the intended calculation.

Missingness and invalidity need explicit statuses. purchases=None is rejected by this strict count schema; purchases=0 is a real observed zero. A broader system could carry a separate unknown record with a source reason. It should not coerce unknown to zero, nor remove every hard-to-parse study and then report the remaining sample as representative.

### Interview reasoning with explanatory answers

**Why is schema validity insufficient?** It establishes structure and primitive types. A fabricated purchase count can still be an integer within the allowed range. Source support and semantic interpretation need separate checks.

**Can the parser prove a statistical result?** It can recover the declared source fields under its grammar. A causal effect, standard error or p-value additionally needs actual analysis inputs and justified design assumptions. Preserve a source's claim as a claim until that separate computation is validated.

**How should an extraction comparison be scored?** Align records and fields to held-out source families, count unsupported values and missing-field behavior, and report acceptance coverage beside accuracy. Otherwise a system can appear accurate by rejecting difficult documents or inventing easy defaults.

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

**Expected:** values 10 and 3; each span slices the original digits.

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
   **Expected:** values 10 and 3; each span slices the original digits.
   **Verify:** Save the assertion results for exercise 3, including values 10 and 3; each span slices the original digits.

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

If a rate is wrong, inspect the exact source spans, parsed values, eligibility rule and denominator in that order. If zero-activity records vanish, distinguish a valid zero-count observation from an undefined zero-denominator rate. If a Boolean slips into counts, inspect exact types before coercion.

If accepted records have excellent accuracy but aggregate findings change, inspect the rejected population and grouping units. If a causal conclusion appears despite having only counts and a unit label, locate the missing assignment and outcome data. If citations move after text cleanup, preserve the original version and an explicit coordinate mapping rather than widening a substring match.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Schema validity, Semantic validity, Provenance span using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-001` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Python json documentation](https://docs.python.org/3.12/library/json.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-002, Data-science task contracts and structured extraction.
Read courses/llm-applied/guides/llm-applied-002.md and courses/llm-applied/lessons/llm-applied-002.py. Direct prerequisites: `llm-applied-001`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
