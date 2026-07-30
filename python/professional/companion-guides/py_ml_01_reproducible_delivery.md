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

## Exercises

### 1. Complete snapshot hashing

Require a nonempty unique `record_id`, sort by it, serialize with sorted keys,
reject NaN, and hash UTF-8 bytes. Verify reversed rows retain the hash while one
changed value does not.

Explain what the hash does *not* prove: source ownership, legality, labeling
quality, representativeness, or absence of leakage.

### 2. Fit and serialize the local model

Fit `y = intercept + coefficient*x` on three deterministic points. Store only
format identifier, feature name, and numeric parameters in JSON. Do not use
pickle: loading an untrusted pickle can execute code.

### 3. Version the feature schema

Declare feature name, ordered position, dtype, required status, and schema
version. Test exact compatibility, reordered input, a renamed feature, and a
version change. Decide which future changes could be safely additive for a
different consumer contract.

### 4. Define runtime compatibility

Declare Python 3.11 through below 3.13 and required package major versions.
Inject the observed versions into the check rather than dumping a
machine-specific environment. Report every incompatibility, not only the first.

### 5. Build and tamper with a bundle

Write model, schema, and manifest into a temporary directory. Verify all
hashes. Replace `model.json` with `{}` and confirm loading fails before parsing
or prediction.

### 6. Promote with evidence

Register a candidate with:

- tests passed,
- compatibility passed,
- named metric and threshold,
- metric value, and
- 64-character manifest hash.

Move it to staging and production. Reject a version with missing tests even if
its metric is high.

### 7. Rehearse rollback

Promote version 1, then version 2. Record a simulated latency regression and
roll back to archived version 1. Confirm one production version remains and the
event trail preserves action, target, and reason.

### 8. Relate the lab to MLflow

Map snapshot, manifest, metrics, and stages to local MLflow concepts from Day
53. MLflow can store evidence; it does not define your compatibility or
approval policy automatically.

### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 9 — rebuild a bundle deterministically

Build the JSON model bundle twice from canonical records and the same configuration. Compare manifest/artifact hashes and diagnose any nondeterministic field such as timestamps, path order, or float serialization.

**Progressive hint:** Keep build time and machine paths outside content-addressed payloads. Canonical JSON requires sorted keys, stable ordering, and finite values.

### Exercise 10 — write a claim-bounded model card

Create a model card from the manifest and evaluation evidence: intended and excluded use, population, metric/threshold, slices/support, data provenance, limitations, monitoring, owners, and stop conditions.

**Progressive hint:** Generate measured fields from the same result object and keep policy prose versioned. Do not claim causality or production readiness from offline metrics.

### Exercise 11 — design shadow and canary evidence

Specify a no-side-effect shadow comparison followed by a bounded canary. Define routing, success/guardrail metrics, sample/time minimums, stop rules, rollback, and how delayed labels are handled.

**Progressive hint:** Shadow predictions do not affect decisions; canary output does. Both need versioned request/prediction identity and privacy-safe telemetry.

### Exercise 12 — separate drift from compatibility

Create examples of schema incompatibility, valid schema with shifted distribution, and stable inputs with performance degradation. Route each to reject, monitor/investigate, or rollback/retrain policy.

**Progressive hint:** Compatibility is a hard interface check; drift and quality are statistical evidence with support, reference, and action thresholds.

### Exercise 13 — test forward and backward compatibility

Build a matrix of producer/consumer schema and model versions. Test an additive optional field, required rename, reordered feature, and changed numeric meaning across old/new readers.

**Progressive hint:** Define compatibility from each consumer's contract; semantic changes may be breaking even when JSON types match.

### Exercise 14 — capture dependency and supply-chain evidence

Create a local release manifest containing reviewed lock hash, direct runtime requirements, Python range, package major versions, artifact hashes, source revision/dirty flag, and a generated component inventory.

**Progressive hint:** Keep portable names/versions/hashes; omit credentials and developer paths. An inventory is evidence, not a vulnerability verdict.

### Exercise 15 — verify artifact trust before parsing

Model a trusted local manifest root and verify every bundle file's relative path, size, and SHA-256 before JSON parsing. Reject path traversal, symlink escape, extra required files, and pickle.

**Progressive hint:** Resolve paths under the bundle root without following an escape. Hash bytes first and accept only an allowlisted safe format.

### Exercise 16 — rehearse rollback dependency failure

Archive version 1, promote version 2, then discover that version 1's runtime dependency is unavailable. Define rollback-target readiness, fallback decision, event trail, and prevention.

**Progressive hint:** A registry stage is not enough; periodically load and smoke-test retained rollback bundles in their compatible runtime.

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
