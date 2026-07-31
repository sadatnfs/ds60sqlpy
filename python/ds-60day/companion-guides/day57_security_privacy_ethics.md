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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 57 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — data minimization, privacy boundaries, fairness evidence, and accountable controls

### The mental model

Security asks how systems resist misuse; privacy asks whether collection,
use, access, retention, and disclosure of data are justified; ethics
asks who benefits or is harmed and how decisions remain accountable.
These overlap but are not interchangeable.

Direct identifiers can name a person; quasi-identifiers can re-identify
in combination. Redaction removes visibility, while pseudonymization
retains linkability and is therefore still personal data. Fairness
metrics require a relevant decision, group definitions, denominators,
uncertainty, and harm analysis—not a single parity number.

### Worked examples and syntax anatomy

- **allowlist output fields:** starts from data that is necessary rather than trying to detect every sensitive field after collection.
- **detection → review → action:** treats regex/PII scanners as bounded signals with false positives and false negatives.
- **group metric + support:** reports numerator/denominator and uncertainty so tiny groups do not create confident-looking claims.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — minimize a record through an allowlist

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
raw_record = {
    "record_id": "row-17",
    "email": "learner@example.invalid",
    "age_band": "35-44",
    "prediction": 0.72,
    "free_text": "not required for this report",
}
allowed_fields = {"record_id", "age_band", "prediction"}
minimized = {key: raw_record[key] for key in allowed_fields}
print(minimized)
assert "email" not in minimized and "free_text" not in minimized
```

**Expected observation:** Only fields required for the stated report cross the boundary; unnecessary raw text and contact data do not.

**Assumption to name:** The purpose and access model justify each allowed field, including the opaque record ID.

### Focused example B — attach sample support to group error rates

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
groups = {
    "group_a": {"false_negatives": 8, "actual_positives": 80},
    "group_b": {"false_negatives": 1, "actual_positives": 5},
}
report = {
    name: {
        "false_negative_rate": values["false_negatives"] / values["actual_positives"],
        "support": values["actual_positives"],
    }
    for name, values in groups.items()
}
print(report)
assert report["group_b"]["support"] == 5
```

**Expected observation:** Group B's 20% rate rests on only five positive cases, so uncertainty and collection context are central.

**Assumption to name:** The group definitions are lawful, meaningful for the decision, and measured consistently.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define data minimization, privacy boundaries, fairness evidence, and accountable controls in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Calling hashed identifiers anonymous, treating a regex scan as complete protection, or optimizing parity without decision context.

**Debug it deliberately:** Build a data-flow inventory: source, purpose, lawful/ethical basis, fields, access, retention, logs/artifacts, deletion, owners, and incident route.

**Stop condition:** Do not expose real sensitive data in a lesson, log, screenshot, model artifact, prompt, or group report without explicit authorization and minimization.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Build a DataFrame PII scanner covering column names and free text.

**Verify:** For task `Build a DataFrame PII scanner covering column names and free text`, record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.






2. Add a function that masks email addresses and phone numbers in text.

**Verify:** For task `Add a function that masks email addresses and phone numbers in text`, demonstrate the concrete requirement “2. Add a function that masks email addresses and phone numbers in text” with explicit inputs, observable output, and one counterexample.






3. Simulate subgroup precision and recall for a classifier and compare groups.

**Verify:** For task `Simulate subgroup precision and recall for a classifier and compare groups`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior.






4. Draft a one-page data-ethics checklist for your project.

**Verify:** For task `Draft a one-page data-ethics checklist for your project`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Progressive hints

1. Return finding type, row identifier, column, and a safe count—do not log the
   raw matched value. Test false-positive and missed-format cases.
2. Preserve only the minimum structure needed for debugging and ensure repeated
   substitutions do not reveal the original.
3. Include group support and positive-label counts beside metrics. Avoid a
   conclusion when groups are too small for a stable estimate.
4. Name intended use, excluded use, affected people, owners, data rights,
   retention, access, monitoring, appeals, and incident response.

### Additional mastery practice

Combine data minimization, access control, threat modeling, privacy limits, fairness uncertainty, and incident response. Detection or masking alone is not protection.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

5. **Threat modeling:** Create a data-flow diagram for collection, notebook, artifacts, API, logs, and backups. For each boundary, identify asset, actor, threat, control, residual risk, and owner.
   **Progressive hint:** Include accidental exposure and insider misuse, not only external attackers. Trace data copies and retention through every stage.

**Verify:** For task `Threat modeling: Create a data-flow diagram for collection, notebook, artifacts, API, logs, a...`, report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels; then verify identity/hash and metadata, then reload or inspect the artifact outside the creating state and test one tampered mismatch.







6. **Re-identification reasoning:** Generalize a small dataset to satisfy a chosen k-anonymity target, then demonstrate why k-anonymity does not prevent attribute disclosure or attacks using outside information.
   **Progressive hint:** Group quasi-identifiers, inspect equivalence-class sizes and sensitive value diversity, and measure utility loss.

**Verify:** For task `Re-identification reasoning: Generalize a small dataset to satisfy a chosen k-anonymity targe...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







7. **Fairness uncertainty:** Bootstrap subgroup precision and recall, show confidence intervals and support, and compare a gap with a ratio. Explain what to do when one group's denominator is nearly zero.
   **Progressive hint:** Resample at the independent entity level when rows repeat. Undefined metrics should remain undefined rather than being forced to zero.

**Verify:** For task `Fairness uncertainty: Bootstrap subgroup precision and recall, show confidence intervals and...`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







8. **Incident response:** Simulate discovering raw emails in a committed notebook output. Write the containment, notification, credential review, history cleanup decision, verification, and prevention steps.
   **Progressive hint:** Preserve a restricted incident record, stop further sharing, and assume copied history may exist. Redaction from the latest commit alone is insufficient.

**Verify:** For task `Incident response: Simulate discovering raw emails in a committed notebook output. Write the...`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-57` — Day 57 — Security, Privacy, and Ethics.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize data minimization, privacy boundaries, fairness evidence, and accountable controls. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day57_security_privacy_ethics.md`
- learner artifact: `python/ds-60day/notebooks/day57_security_privacy_ethics.ipynb`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
