# Day 57 — Security, Privacy, and Ethics

**Lesson ID:** `python-57` · **Level:** advanced · **Dependencies:** `data` · **Network:** offline

Security, privacy, and ethical analysis are requirements throughout a data
project, not a checklist applied after modeling. This lesson offers lightweight
technical practice; actual obligations require organizational policy, legal
review, domain expertise, and affected-stakeholder input.

## Learning objectives

By the end of the lesson, you can:

- inventory direct, quasi-, and sensitive identifiers;
- explain detection, redaction, pseudonymization, and anonymization differences;
- implement bounded PII scanning and state its failure modes;
- compare model metrics across relevant groups with sample sizes; and
- draft ownership, retention, access, incident, and model-card controls.

## Prerequisites

- Complete `python-56` (orchestration).
- Recall regex, hashing, pandas, and classification metrics.
- Use only the synthetic records in the notebook—never paste real sensitive
  information into an exercise or external assistant.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| PII | Information that identifies or can reasonably be linked to a person |
| Quasi-identifier | Attribute that can identify when combined with other data |
| Sensitive attribute | Protected or high-impact characteristic requiring special care |
| Data minimization | Collecting, retaining, and exposing only what is necessary |
| Redaction | Removing or masking a value |
| Pseudonymization | Replacing an identifier with a stable token while retaining linkability |
| Anonymization | Irreversibly reducing re-identification risk to an accepted standard |
| Fairness metric | Quantified comparison tied to a specific harm and decision context |
| Threat model | Explicit actors, assets, attack paths, likelihood, and impact |

Pseudonymized data are still personal data in many contexts because records can
remain linkable or reversible with auxiliary information.

## Worked example: detection is only one layer

```python
import re

EMAIL = re.compile(r"[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?"
    r"(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}"
)


def detected_kinds(text: str) -> set[str]:
    kinds: set[str] = set()
    if EMAIL.search(text):
        kinds.add("email")
    if PHONE.search(text):
        kinds.add("phone")
    return kinds
```

Regex has false positives and false negatives across languages and formats. A
scanner should route suspected content for controlled handling; it must not
certify that undetected text is safe.

The notebook uses a hard-coded salt only to make a deterministic demo. A real
pseudonymization key belongs in an approved secret manager, must be rotated
under policy, and should use a keyed construction such as HMAC—not a public,
reused repository constant.

## Learner exercises

1. Build a DataFrame PII scanner covering column names and free text.
2. Add a function that masks email addresses and phone numbers in text.
3. Simulate subgroup precision and recall for a classifier and compare groups.
4. Draft a one-page data-ethics checklist for your project.

### Progressive hints

1. Return finding type, row identifier, column, and a safe count—do not log the
   raw matched value. Test false-positive and missed-format cases.
2. Preserve only the minimum structure needed for debugging and ensure repeated
   substitutions do not reveal the original.
3. Include group support and positive-label counts beside metrics. Avoid a
   conclusion when groups are too small for a stable estimate.
4. Name intended use, excluded use, affected people, owners, data rights,
   retention, access, monitoring, appeals, and incident response.

## Self-check

- Why is hashing a small identifier space without a secret reversible by search?
- What information should a PII scanner avoid writing to logs?
- Can equal precision alone establish a fair decision system?
- Who can stop or roll back the system when harm is detected?
- What evidence would show that deleted data are gone from derivatives/backups
  under the applicable policy?

Expected behavior: the demo finds common sample emails/phones, but your
documentation explicitly lists formats it may miss and non-PII it may flag.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Regex called “PII protection” | Unknown sensitive data passes through | Layer inventory, classification, scanning, access, and review |
| Raw matches logged | Detection creates a new exposure | Log safe metadata/counts only |
| Unsalted/plain hashes | Dictionary attacks recover identifiers | Use managed keyed pseudonyms where justified |
| Protected attribute dropped blindly | Fairness cannot be audited | Separate controlled audit use from model inputs |
| Group metrics without denominators | Noise appears decisive | Report counts and uncertainty |
| Ethics checklist has no owner | No enforceable action | Assign approval, escalation, and appeal paths |

Privacy can conflict with observability and fairness auditing. Resolve the
minimum necessary controlled data, access, aggregation, and retention with the
appropriate experts rather than maximizing collection.

## Next step

- Work in the [Day 57 learner notebook](../notebooks/day57_security_privacy_ethics.ipynb).
- Then review the
  [Day 57 solution](../solutions/day57_security_privacy_ethics/day57_solutions.md).
- Continue to [Day 58 — Review and Refactoring](day58_code_review_refactor_tests.md).
