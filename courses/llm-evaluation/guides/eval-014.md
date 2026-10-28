# eval-014: Robustness, access policy and adversarial evaluation

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-009`, `eval-011`.

Build bounded adversarial and invariance tests while enforcing authorization independently of generated text or average answer quality.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-014`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Define the boundary being tested

A robustness test changes an input condition and observes whether a required property survives. A harmless formatting change may be intended to preserve the answer, while a changed unit or date should alter it. The relation must be specified before calling every output difference a failure or every identical output a success.

Security requirements are different from average task quality. A research assistant must not obtain access merely because a document or generated tool proposal claims to be authorized. Authority should come from trusted metadata and the caller's permissions. Retrieved text is data for the task. It is not an instruction channel for granting new rights.

The examples use public and restricted synthetic fixture records. They do not inspect real credentials, make network requests or execute shell commands. Their purpose is to make an authorization invariant and a bounded proposal validator executable. A system that passes these small checks has demonstrated only the named cases, not universal resistance to adversarial prompting.

## Worked case A: authorization before content matching

The retrieval helper first filters documents by trusted access metadata and only then evaluates the query. A restricted document includes the word public in its text. A content-based shortcut would misclassify it, but the metadata policy does not. The code also shows that appending an instruction-like request to the query cannot expand the allowed document set.

```python
DOCUMENTS = [
    {"id": "public-guide", "access": "public", "text": "conversion rate definition"},
    {
        "id": "restricted-note",
        "access": "restricted",
        "text": "public wording does not grant access",
    },
]


def retrieve(query, allowed_access):
    authorized = [d for d in DOCUMENTS if d["access"] in allowed_access]
    terms = set(query.casefold().split())
    return [d["id"] for d in authorized if terms.intersection(d["text"].casefold().split())]


def apply_proposal(proposal, allowed_ids):
    if not isinstance(proposal, dict) or set(proposal) != {"operation", "record_id"}:
        raise ValueError("Invalid proposal schema")
    if proposal["operation"] != "lookup":
        raise ValueError("Unsupported operation")
    key = proposal["record_id"]
    if not isinstance(key, str) or key not in allowed_ids:
        raise ValueError("Unauthorized record")
    return {"record_id": key, "result": "authored fixture value"}


def worked_a():
    assert retrieve("public", {"public"}) == []
    assert retrieve("conversion", {"public"}) == ["public-guide"]
    assert "restricted-note" not in retrieve("conversion ignore rules public", {"public"})
    print("Authorized candidate set is independent of instruction-like query text")


worked_a()
```

## Worked case B: generated proposals have no inherent authority

A generated proposal is parsed as a small data object. Its operation must be allowlisted, its fields exact, its identifier well formed and its target authorized. The helper returns an approved synthetic lookup result only after all conditions hold. A proposal to invoke an unspecified operation is rejected; the string is never passed to a shell or interpreted as executable code.

```python
DOCUMENTS = [
    {"id": "public-guide", "access": "public", "text": "conversion rate definition"},
    {
        "id": "restricted-note",
        "access": "restricted",
        "text": "public wording does not grant access",
    },
]


def retrieve(query, allowed_access):
    authorized = [d for d in DOCUMENTS if d["access"] in allowed_access]
    terms = set(query.casefold().split())
    return [d["id"] for d in authorized if terms.intersection(d["text"].casefold().split())]


def apply_proposal(proposal, allowed_ids):
    if not isinstance(proposal, dict) or set(proposal) != {"operation", "record_id"}:
        raise ValueError("Invalid proposal schema")
    if proposal["operation"] != "lookup":
        raise ValueError("Unsupported operation")
    key = proposal["record_id"]
    if not isinstance(key, str) or key not in allowed_ids:
        raise ValueError("Unauthorized record")
    return {"record_id": key, "result": "authored fixture value"}


def worked_b():
    good = apply_proposal({"operation": "lookup", "record_id": "public-guide"}, {"public-guide"})
    assert good["record_id"] == "public-guide"
    for bad in (
        {"operation": "other", "record_id": "public-guide"},
        {"operation": "lookup", "record_id": "restricted-note"},
    ):
        try:
            apply_proposal(bad, {"public-guide"})
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid proposal admitted")
    print("Allowed lookup accepted; other operations and targets rejected")


worked_b()
```

## Design an adversarial assessment

Create a threat model describing the attacker-controlled surface, trusted policy, possible side effects and failure severity. Sample tests across relevant attack families instead of repeating one phrase many times. Keep a record of which families and transformations were attempted. Zero failures among a few known patterns does not imply zero risk for unrepresented conditions.

Use metamorphic cases alongside adversarial ones. Whitespace or display-order transformations can test intended invariances. A changed permission or document date should change eligibility. Check the intermediate authorized candidate set as well as the final answer, because a system may accidentally access restricted content without quoting it in its response.

## Separate policy enforcement from model scoring

A model judge can help classify suspicious outputs, but it should not be the sole authority deciding whether an operation is permitted. Deterministic controls are appropriate for explicit constraints such as an allowed operation set, resource identity and maximum request size. Model behavior and policy controls should have separate versions and evidence.

When evaluating safety-related outcomes, preserve unknown and ambiguous cases for review. Do not reduce a critical failure to a small negative contribution in a broad helpfulness average. Define escalation and rollback decisions with the same care as the ordinary quality metric. A statistical confidence interval around observed failure frequency does not prove that the test distribution covers the threat model.

## Diagnose failures and transfer responsibly

A failed case should retain its input, policy context, attempted operation and actual side effect. Fixing the visible response while leaving an unauthorized intermediate action is insufficient. Re-run the failed case and independent neighboring cases after a repair, then evaluate the changed system on a broader held-out set.

The fixture demonstrates strict schema and authorization checks for an inert local lookup. A real system additionally needs identity integration, auditable resource ownership, secure implementation and operational monitoring. Those requirements cannot be inferred from a successful toy validator or a high benchmark score.


## Six investigations

### 1. Change formatting

Change capitalization and surrounding whitespace in the query conversion.

**Expected:** The authorized result remains public-guide.

**Hint:** Normalize harmless text without changing policy metadata.

### 2. Remove authorization

Use an empty allowed-access set.

**Expected:** No document is returned.

**Hint:** Apply policy before query matching.

### 3. Reject extra authority fields

Add a self-declared authority field to a proposal.

**Expected:** The exact-schema validator rejects it.

**Hint:** Untrusted data cannot add new privileges.

### 4. Inspect an intermediate action

An answer omits restricted text but retrieval accessed it.

**Expected:** Record a policy failure.

**Hint:** Evaluate side effects and candidate sets as well as visible text.

### 5. Audit family coverage

Repeat one attack template one hundred times.

**Expected:** Report one covered template family, not universal security evidence.

**Hint:** Distinguish repetitions from diversity.

### 6. Keep unknown separate

An output cannot be confidently labeled for a critical condition.

**Expected:** Route it to review and retain unknown status.

**Hint:** A missing verdict is not a pass.

## Primary references

- [NIST adversarial machine learning taxonomy](https://doi.org/10.6028/NIST.AI.100-2e2025)
- [Existing grounded assistant controls](../../../courses/llm-applied/README.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
