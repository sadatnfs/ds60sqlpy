# Reproducible data and model delivery

**Stable ID:** `python-ml-01`

**Level:** advanced

**Estimated time:** 210–270 minutes

## Level and prerequisites

- **Catalog prerequisite:** `python-45`
- Python Days 34–45; Days 53–55 are useful follow-ons
- Basic model fitting, evaluation, files, JSON, and hashing
- `python-pro-01` package metadata concepts are helpful, not required

The lab uses a deterministic linear model and temporary JSON files. It needs no
cloud registry, MLflow server, container registry, or network access.

## Learning objectives

You will be able to:

1. Create an order-stable data snapshot identity.
2. Hash model, feature schema, and manifest independently.
3. Record a bounded runtime compatibility contract.
4. Verify artifact bytes before loading model data.
5. Reject incompatible feature order, type, Python, or package versions.
6. Distinguish candidate, staging, production, and archived registry stages.
7. Require tests, compatibility, metrics, and manifest identity for promotion.
8. Perform a recorded rollback during a local incident drill.

## Vocabulary and concepts

- **Lineage:** evidence connecting source data, code/runtime, evaluation, and
  artifact.
- **Snapshot identifier:** stable identity for exact dataset content.
- **Canonical serialization:** one deterministic byte representation.
- **Content hash:** digest that changes when bytes change.
- **Feature schema:** ordered feature names, types, requirements, and version.
- **Manifest:** artifact metadata and referenced hashes.
- **Compatibility:** whether a consumer satisfies declared schema/runtime
  assumptions.
- **Registry stage:** reviewed lifecycle state, not merely a folder name.
- **Promotion evidence:** checks required before a version changes stage.
- **Rollback:** deliberate restoration of a previously accepted version with a
  recorded reason.
- **Trusted loading:** verifying identity and parsing a constrained format
  rather than executing arbitrary serialized code.

## Worked example / walkthrough

Run the learner hash example.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_ml_01_reproducible_delivery.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_ml_01_reproducible_delivery.py
```

Ordinary JSON object key order changes raw bytes. Canonical JSON sorts keys and
uses stable separators. Dataset rows are sorted by unique `record_id` so an
incidental read order does not create a new snapshot identity.

The reference delivery flow is:

```text
rows -> snapshot hash
model -> model.json -> artifact hash
schema -> schema.json -> schema hash
all hashes + runtime -> manifest.json
                         |
                         +-> verify -> compatibility -> promotion evidence
                                                   -> registry stage
```

Every generated file stays in a temporary directory.

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

Work from the repository root. First run the answer-free learner
module named in this guide's original walkthrough. Read each TODO as a
contract: record the input, returned value, raised exception, and side
effect before implementing it. Then run the focused test command in
**Self-check**. Keep exploratory changes in a copy or a new test; the
checked-in solution remains a comparison artifact.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_ml_01_reproducible_delivery.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_ml_01_reproducible_delivery.py
```

The focused test command is shown in **Self-check** below. The learner
module is intentionally answer-free, so `TODO` output is the expected
starting state rather than a setup failure.

## Mechanism lab — two small examples before the full system

### Boundary and mental model

Reproducible model delivery links exact data records, feature schema,
training configuration, environment, metrics, and artifact bytes. A
canonical hash is stable only after row identity/order, field order,
numeric special values, encoding, and serialization are defined.

A delivery bundle contains a safe model representation, schema, and
manifest of hashes/versions/evidence. Loading verifies bytes and
compatibility before parsing or prediction. Promotion is a policy
decision based on tests, thresholds, limitations, ownership, and
rollback—not the existence of a model file.

- **canonical data hash:** normalizes only declared non-semantic ordering and rejects duplicate/missing identity or unsupported values.
- **feature/runtime compatibility:** checks ordered names, types, required fields, schema version, Python and direct package ranges.
- **manifest verification before load:** checks every relative path, byte hash, format, and expected metadata before trusting content.

### Micro-example A — make record order irrelevant but value changes visible

```python
import hashlib
import json

def snapshot(records):
    ordered = sorted(records, key=lambda row: row["record_id"])
    payload = json.dumps(
        ordered, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

records = [{"record_id": "b", "x": 2}, {"record_id": "a", "x": 1}]
assert snapshot(records) == snapshot(list(reversed(records)))
changed = [{"record_id": "b", "x": 3}, {"record_id": "a", "x": 1}]
assert snapshot(records) != snapshot(changed)
```

**Expected observation:** Declared row ordering does not change the identity, while one semantic value change does.

**Why it matters:** Record IDs are unique/nonempty and sorting them is semantically irrelevant for this dataset.

### Micro-example B — fail a bundle when one artifact byte changes

```python
import hashlib

files = {"model.json": b'{"coefficient":2.0}', "schema.json": b'{"x":"float"}'}
manifest = {name: hashlib.sha256(data).hexdigest()
            for name, data in files.items()}
files["model.json"] = b"{}"  # tampering/corruption
mismatches = [
    name for name, data in files.items()
    if hashlib.sha256(data).hexdigest() != manifest[name]
]
print(mismatches)
assert mismatches == ["model.json"]
```

**Expected observation:** Verification catches the changed artifact before code attempts to interpret it.

**Why it matters:** The expected manifest came from a trusted release channel and itself is authenticated/governed.

### Debugging and transfer

**Common mistake:** Hashing noncanonical JSON, loading untrusted pickle first, or calling an environment dump a compatibility policy.

**Diagnostic:** Rebuild the canonical bytes, print schema/version differences, verify every manifest path/hash before parse, and reload/predict in a clean process.

**Transfer question:** What compatibility rule allows an additive nullable feature without silently changing an older model's ordered input?

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercises

### 1. Complete snapshot hashing

Require a nonempty unique `record_id`, sort by it, serialize with sorted keys,
reject NaN, and hash UTF-8 bytes. Verify reversed rows retain the hash while one
changed value does not.

Explain what the hash does *not* prove: source ownership, legality, labeling
quality, representativeness, or absence of leakage.

**Verify:** For task `Complete snapshot hashing`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### 2. Fit and serialize the local model

Fit `y = intercept + coefficient*x` on three deterministic points. Store only
format identifier, feature name, and numeric parameters in JSON. Do not use
pickle: loading an untrusted pickle can execute code.

**Verify:** For task `Fit and serialize the local model`, report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







### 3. Version the feature schema

Declare feature name, ordered position, dtype, required status, and schema
version. Test exact compatibility, reordered input, a renamed feature, and a
version change. Decide which future changes could be safely additive for a
different consumer contract.

**Verify:** For task `Version the feature schema`, assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced.







### 4. Define runtime compatibility

Declare Python 3.11 through below 3.13 and required package major versions.
Inject the observed versions into the check rather than dumping a
machine-specific environment. Report every incompatibility, not only the first.

**Verify:** For task `Define runtime compatibility`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







### 5. Build and tamper with a bundle

Write model, schema, and manifest into a temporary directory. Verify all
hashes. Replace `model.json` with `{}` and confirm loading fails before parsing
or prediction.

**Verify:** For task `Build and tamper with a bundle`, report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







### 6. Promote with evidence

Register a candidate with:

- tests passed,
- compatibility passed,
- named metric and threshold,
- metric value, and
- 64-character manifest hash.

Move it to staging and production. Reject a version with missing tests even if
its metric is high.

**Verify:** For task `Promote with evidence`, assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced; then report class support and confusion counts at the chosen threshold and prove the declared operating constraint is satisfied.







### 7. Rehearse rollback

Promote version 1, then version 2. Record a simulated latency regression and
roll back to archived version 1. Confirm one production version remains and the
event trail preserves action, target, and reason.

**Verify:** For task `Rehearse rollback`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### 8. Relate the lab to MLflow

Map snapshot, manifest, metrics, and stages to local MLflow concepts from Day
53. MLflow can store evidence; it does not define your compatibility or
approval policy automatically.

**Verify:** For task `MLflow can store evidence; it does not define your compatibility or`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced.







### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 9 — rebuild a bundle deterministically

Build the JSON model bundle twice from canonical records and the same configuration. Compare manifest/artifact hashes and diagnose any nondeterministic field such as timestamps, path order, or float serialization.

**Progressive hint:** Keep build time and machine paths outside content-addressed payloads. Canonical JSON requires sorted keys, stable ordering, and finite values.

**Verify:** For task `rebuild a bundle deterministically`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.







### Exercise 10 — write a claim-bounded model card

Create a model card from the manifest and evaluation evidence: intended and excluded use, population, metric/threshold, slices/support, data provenance, limitations, monitoring, owners, and stop conditions.

**Progressive hint:** Generate measured fields from the same result object and keep policy prose versioned. Do not claim causality or production readiness from offline metrics.

**Verify:** For task `write a claim-bounded model card`, report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels; then report class support and confusion counts at the chosen threshold and prove the declared operating constraint is satisfied.







### Exercise 11 — design shadow and canary evidence

Specify a no-side-effect shadow comparison followed by a bounded canary. Define routing, success/guardrail metrics, sample/time minimums, stop rules, rollback, and how delayed labels are handled.

**Progressive hint:** Shadow predictions do not affect decisions; canary output does. Both need versioned request/prediction identity and privacy-safe telemetry.

**Verify:** For task `design shadow and canary evidence`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then test representative forbidden values and prove they are absent from returned data, repr, logs, metrics, and generated artifacts.







### Exercise 12 — separate drift from compatibility

Create examples of schema incompatibility, valid schema with shifted distribution, and stable inputs with performance degradation. Route each to reject, monitor/investigate, or rollback/retrain policy.

**Progressive hint:** Compatibility is a hard interface check; drift and quality are statistical evidence with support, reference, and action thresholds.

**Verify:** For task `separate drift from compatibility`, report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels; then assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced.







### Exercise 13 — test forward and backward compatibility

Build a matrix of producer/consumer schema and model versions. Test an additive optional field, required rename, reordered feature, and changed numeric meaning across old/new readers.

**Progressive hint:** Define compatibility from each consumer's contract; semantic changes may be breaking even when JSON types match.

**Verify:** For task `test forward and backward compatibility`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.







### Exercise 14 — capture dependency and supply-chain evidence

Create a local release manifest containing reviewed lock hash, direct runtime requirements, Python range, package major versions, artifact hashes, source revision/dirty flag, and a generated component inventory.

**Progressive hint:** Keep portable names/versions/hashes; omit credentials and developer paths. An inventory is evidence, not a vulnerability verdict.

**Verify:** For task `capture dependency and supply-chain evidence`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







### Exercise 15 — verify artifact trust before parsing

Model a trusted local manifest root and verify every bundle file's relative path, size, and SHA-256 before JSON parsing. Reject path traversal, symlink escape, extra required files, and pickle.

**Progressive hint:** Resolve paths under the bundle root without following an escape. Hash bytes first and accept only an allowlisted safe format.

**Verify:** For task `verify artifact trust before parsing`, report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels; then verify identity/hash and metadata, then reload or inspect the artifact outside the creating state and test one tampered mismatch.







### Exercise 16 — rehearse rollback dependency failure

Archive version 1, promote version 2, then discover that version 1's runtime dependency is unavailable. Define rollback-target readiness, fallback decision, event trail, and prevention.

**Progressive hint:** A registry stage is not enough; periodically load and smoke-test retained rollback bundles in their compatible runtime.

**Verify:** For task `rehearse rollback dependency failure`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







## Self-check

- Snapshot hashes ignore row order but detect content changes.
- Duplicate record IDs fail.
- Canonical JSON rejects NaN.
- Model prediction for x=3 is 7.
- Artifact tampering fails hash verification.
- Schema, Python, and package incompatibilities are all reported.
- A failed test blocks promotion despite a passing metric.
- Promotion archives the prior production entry.
- Rollback records a nonempty incident reason.
- No pickle, hosted account, or network access is used.

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest python.professional.tests.test_py_ml_01_reproducible_delivery -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest python.professional.tests.test_py_ml_01_reproducible_delivery -v
```

## Common pitfalls

- **A filename is called lineage:** names are mutable and do not identify
  content.
- **Row order changes every snapshot:** canonical identity did not define row
  ordering.
- **A hash is called trustworthy:** identity is not provenance or review.
- **The feature set matches but order differs:** the model contract was not
  checked exactly.
- **The whole developer environment is required:** compatibility was not
  bounded to direct runtime assumptions.
- **Pickle is loaded before verification:** arbitrary code may execute.
- **A metric alone promotes:** tests, schema/runtime compatibility, and review
  evidence are missing.
- **Rollback is an unrecorded file copy:** operators cannot reconstruct what
  changed or why.

## Next step

Use this verified bundle in `python-svc-02`. Day 53 can record the same evidence
in local MLflow, while Day 54 supplies monitoring and governance decisions.

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-ml-01` — Reproducible data and model delivery.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize data/model identity, schema compatibility, safe bundles, and promotion evidence. Use exactly these maintained learner materials:
- guide: `python/professional/companion-guides/py_ml_01_reproducible_delivery.md`
- learner artifact: `python/professional/lessons/py_ml_01_reproducible_delivery.py`

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
