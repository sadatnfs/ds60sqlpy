# llm-applied-002: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Structured extraction turns text into typed records, but valid JSON is only the first boundary. A record can have all required keys and still contain a fabricated measurement, an impossible count or a unit mismatch. The task should distinguish unsupported fields from explicit missing values. This lesson extracts a small study record with visits, purchases andassignment_unit. The reference uses deterministic parsing of a tightly specified authored format so every accepted value can be traced to source text. It is an extraction baseline, not a language model. A future LLM proposal must pass the same validation before downstream analysis.

For data science, preserving units and uncertainty is essential. Purchases cannot exceed visits under the stated one-purchase-per-visit fixture. A missing outcome is not zero. A study randomized by account cannot be analyzed as though every repeated visit were independently assigned. The schema therefore carries semantic assumptions alongside numeric fields. Once accepted, deterministic code calculates conversion rate; generated prose must cite that computed value rather than invent a second calculation.

**Schema validity:** Structural and type conformance of a proposed record.

**Semantic validity:** Consistency with domain rules such as units and count bounds.

**Provenance span:** The source character interval supporting an extracted field.

**Abstention:** Returning an explicit unknown result when evidence is absent.

## Reading the implementation

Validate an already decoded dictionary, require exactly the allowed keys, and reject booleans where an integer count is required because Python bool is a subclass ofint. Validate0<=purchases<=visits and require a positive denominator before computing a rate. UseNone only where the schema explicitly permits missingness. The extract helper recognizes the authored grammar and returns source spans so a field can be traced to the exact characters that supplied it.

## Follow one value from text to an analysis unit

The helper extract recognizes a deliberately narrow source grammar. It uses a full-string regular expression and returns digit spans from the original string. The helper validate accepts an already decoded Python dictionary; it is not a JSON parser. A JSON response from a future language model would first need parsing and then the same independent acceptance checks. These interfaces should not be collapsed into the claim “the model returned valid data.”

For the literal text `Visits: 10; Purchases: 3; Unit: account`, the visit digits occupy the half-open character interval[8, 10), the purchase digit[23, 24), and the unit[32, 39). Slicing the original string at those boundaries recovers10, 3 and account. The integer conversion changes representation, while the stored span keeps its provenance. If preprocessing removes spaces before extracting offsets, those new offsets cannot be applied directly to the original string without a mapping.

The record check accepts exactly three keys and requires type(value) to be int for both counts. Python's Boolean subtype relationship makes this stricter than a plain isinstance(value, int) test. A True visit count would otherwise become one in arithmetic even though the source proposed a logical value. Extra fields are also rejected, so a model cannot quietly insert an unsupported p_value alongside otherwise valid counts.

The domain constraint0<=purchases<=visits assumes at most one counted purchase per eligible visit. It is not a universal business rule. If the real outcome counts multiple items purchased in a visit, the ratio may legitimately exceed one and needs a different name and contract. A validator should make that modeling choice explicit instead of treating every ratio as a probability.

For the valid fixture, \(\frac{3}{10}=0.3\) describes purchases per eligible visit. The assignment_unit field says the experimental assignment is by account. It does not transform the arithmetic denominator into accounts, nor does it make10 visits independently randomized. Repeated observations within accounts require account identities and a suitable analysis design for uncertainty. The three extracted fields alone cannot recover that information.

Aggregation adds another distinction. Suppose one account has1 purchase in1 visit and another has1 purchase in9 visits. The pooled visit rate is2/10=0.2. The equally weighted mean of account-specific rates is(1+1/9)/2=5/9, about0.556. Both calculations are valid for their declared estimands; they answer different questions. Calling both “average conversion” hides the weighting rule. The extraction schema should preserve enough units and identities to support the intended calculation.

Missingness and invalidity need explicit statuses. purchases=None is rejected by this strict count schema; purchases=0 is a real observed zero. A broader system could carry a separate unknown record with a source reason. It should not coerce unknown to zero, nor remove every hard-to-parse study and then report the remaining sample as representative.

### Interview reasoning with explanatory answers

**Why is schema validity insufficient?** It establishes structure and primitive types. A fabricated purchase count can still be an integer within the allowed range. Source support and semantic interpretation need separate checks.

**Can the parser prove a statistical result?** It can recover the declared source fields under its grammar. A causal effect, standard error or p-value additionally needs actual analysis inputs and justified design assumptions. Preserve a source's claim as a claim until that separate computation is validated.

**How should an extraction comparison be scored?** Align records and fields to held-out source families, count unsupported values and missing-field behavior, and report acceptance coverage beside accuracy. Otherwise a system can appear accurate by rejecting difficult documents or inventing easy defaults.

## Exercise 1: Validate a correct proposal

The question is: Validate visits 10, purchases 3 and assignment_unit account.

The denominator and unit are known before division. This calculation is deterministic and does not depend on the wording of an explanation.

```python
record = validate({"visits": 10, "purchases": 3, "assignment_unit": "account"})
assert rate(record) == 0.3
```

**Expected:** conversion rate 0.3.

**Verify:** Compare the computed values or written argument with conversion rate 0.3.

## Exercise 2: Reject a plausible but impossible record

The question is: Validate visits 2 and purchases 3 under the declared one-purchase-per-visit policy.

A JSON parser cannot detect this domain contradiction. The validation rule catches a semantically invalid proposal even though its keys and primitive types are correct.

```python
try:
    validate({"visits": 2, "purchases": 3, "assignment_unit": "account"})
except ValueError:
    pass
else:
    raise AssertionError("impossible counts accepted")
```

**Expected:** ValueError for inconsistent counts.

**Verify:** Compare the computed values or written argument with ValueError for inconsistent counts.

## Exercise 3: Trace extracted values to text

The question is: Parse the source text Visits: 10; Purchases: 3; Unit: account and retain source spans.

Offsets refer to the original source string. Normalizing text before saving offsets without a mapping would make citations point at the wrong characters.

```python
text = "Visits: 10; Purchases: 3; Unit: account"
parsed, spans = extract(text)
assert parsed == record
assert text[slice(*spans["visits"])] == "10" and text[slice(*spans["purchases"])] == "3"
```

**Expected:** values10 and3; each span slices the original digits.

**Verify:** Compare the computed values or written argument with values10 and3; each span slices the original digits.

## Exercise 4: Distinguish missing from zero

The question is: Submit a record with purchases=None and compare it with a real zero-purchase record.

A missing value requires a separate unknown-status schema or a repair workflow. Coercing it to zero changes the statistical meaning of the data.

```python
try:
    validate({"visits": 10, "purchases": None, "assignment_unit": "account"})
except TypeError:
    pass
else:
    raise AssertionError("missing treated as count")
assert rate(validate({"visits": 10, "purchases": 0, "assignment_unit": "account"})) == 0
```

**Expected:** None is rejected by this strict schema; zero is accepted with rate 0.

**Verify:** Compare the computed values or written argument with None is rejected by this strict schema; zero is accepted with rate 0.

## Exercise 5: Reject boolean and extra fields

The question is: Submit visits=True, then add an undeclared p_value field to a valid proposal.

A model can produce syntactically convenient but semantically wrong values. Exact-key and exact-type checks prevent a downstream analysis from silently consuming unsupported claims.

```python
for candidate, kind in [
    ({"visits": True, "purchases": 0, "assignment_unit": "account"}, TypeError),
    ({**record, "p_value": 0.01}, ValueError),
]:
    try:
        validate(candidate)
    except kind:
        pass
    else:
        raise AssertionError("schema bypass accepted")
```

**Expected:** TypeError for a boolean count; ValueError for an extra field.

**Verify:** Compare the computed values or written argument with TypeError for a boolean count; ValueError for an extra field.

## Exercise 6: Preserve the assignment unit

The question is: Attempt to replace account with visit and explain why the independence assumption cannot be inferred from the count fields.

The fixture deliberately supports one study design. Expanding it to visit-level randomization requires an explicit new contract and evaluation, not a casual string substitution.

```python
try:
    validate({**record, "assignment_unit": "visit"})
except ValueError:
    pass
else:
    raise AssertionError("unsupported assignment unit")
assert record["assignment_unit"] == "account"
```

**Expected:** invalid unit rejected; account remains explicit.

**Verify:** Compare the computed values or written argument with invalid unit rejected; account remains explicit.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
