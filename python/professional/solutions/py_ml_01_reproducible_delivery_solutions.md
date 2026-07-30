# Reproducible model-delivery solution reasoning

Attempt `python-ml-01` before opening
[`py_ml_01_reproducible_delivery_solution.py`](py_ml_01_reproducible_delivery_solution.py).

Canonical JSON and SHA-256 make the exact data snapshot, feature schema, model
artifact, and manifest independently identifiable. Sorting by a unique record
ID makes the snapshot insensitive to incidental row order while duplicate IDs
fail fast. A content hash proves byte identity, not data quality or provenance;
those need source and review evidence alongside the digest.

The local linear model is stored as validated JSON rather than pickle. Pickle
can execute code while loading and is not a trustworthy exchange format.
`verify_bundle` checks model, schema, and manifest before use. Compatibility
then checks exact feature order/types, supported Python versions, and declared
package major versions.

Registry stages are decisions, not directories. A candidate needs tests,
compatibility, a thresholded metric, and a manifest identity before staging or
production. Promotion archives the previous production version. Rollback
requires an explicit target and reason and leaves an event trail.

In a larger system MLflow may record runs and artifacts, but the same lineage
and compatibility evidence is still necessary. Hosted accounts are not
required for this local contract.

Edge cases include duplicated record identities, floating NaN (rejected by
canonical JSON), schema reorder, a package major-version change, artifact
tampering, promotion without tests, and rollback to a version whose external
dependencies no longer exist.


---

## Exercise-by-exercise reference

Use this map after an honest attempt. The executable implementation remains
[`py_ml_01_reproducible_delivery_solution.py`](py_ml_01_reproducible_delivery_solution.py); this section explains the
contract, evidence, alternatives, and edge cases behind every numbered task.

### Exercise 1 — Complete snapshot hashing

**Prompt recap:** Require a nonempty unique `record_id`, sort by it, serialize with sorted keys, reject NaN, and hash UTF-8 bytes. Verify reversed rows retain the hash while one changed value does not. Explain what the hash does *not* prove: source ownership, legality, labeling quality, representativeness, or absence of leakage.

**Reference reasoning:** Model delivery packages data identity, feature schema, model format, runtime compatibility, metrics, promotion evidence, and rollback history into one verifiable contract. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 2 — Fit and serialize the local model

**Prompt recap:** Fit `y = intercept + coefficient*x` on three deterministic points. Store only format identifier, feature name, and numeric parameters in JSON. Do not use pickle: loading an untrusted pickle can execute code.

**Reference reasoning:** Model delivery packages data identity, feature schema, model format, runtime compatibility, metrics, promotion evidence, and rollback history into one verifiable contract. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 3 — Version the feature schema

**Prompt recap:** Declare feature name, ordered position, dtype, required status, and schema version. Test exact compatibility, reordered input, a renamed feature, and a version change. Decide which future changes could be safely additive for a different consumer contract.

**Reference reasoning:** Model delivery packages data identity, feature schema, model format, runtime compatibility, metrics, promotion evidence, and rollback history into one verifiable contract. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 4 — Define runtime compatibility

**Prompt recap:** Declare Python 3.11 through below 3.13 and required package major versions. Inject the observed versions into the check rather than dumping a machine-specific environment. Report every incompatibility, not only the first.

**Reference reasoning:** Model delivery packages data identity, feature schema, model format, runtime compatibility, metrics, promotion evidence, and rollback history into one verifiable contract. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 5 — Build and tamper with a bundle

**Prompt recap:** Write model, schema, and manifest into a temporary directory. Verify all hashes. Replace `model.json` with `{}` and confirm loading fails before parsing or prediction.

**Reference reasoning:** Model delivery packages data identity, feature schema, model format, runtime compatibility, metrics, promotion evidence, and rollback history into one verifiable contract. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 6 — Promote with evidence

**Prompt recap:** Register a candidate with: - tests passed, - compatibility passed, - named metric and threshold, - metric value, and - 64-character manifest hash. Move it to staging and production. Reject a version with missing tests even if its metric is high.

**Reference reasoning:** Model delivery packages data identity, feature schema, model format, runtime compatibility, metrics, promotion evidence, and rollback history into one verifiable contract. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 7 — Rehearse rollback

**Prompt recap:** Promote version 1, then version 2. Record a simulated latency regression and roll back to archived version 1. Confirm one production version remains and the event trail preserves action, target, and reason.

**Reference reasoning:** Model delivery packages data identity, feature schema, model format, runtime compatibility, metrics, promotion evidence, and rollback history into one verifiable contract. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 8 — Relate the lab to MLflow

**Prompt recap:** Map snapshot, manifest, metrics, and stages to local MLflow concepts from Day 53. MLflow can store evidence; it does not define your compatibility or approval policy automatically.

**Reference reasoning:** Model delivery packages data identity, feature schema, model format, runtime compatibility, metrics, promotion evidence, and rollback history into one verifiable contract. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 9 — rebuild a bundle deterministically

**Prompt recap:** Build the JSON model bundle twice from canonical records and the same configuration. Compare manifest/artifact hashes and diagnose any nondeterministic field such as timestamps, path order, or float serialization.

**Reasoning path:** Keep build time and machine paths outside content-addressed payloads. Canonical JSON requires sorted keys, stable ordering, and finite values.

Generate immutable payloads from canonical data/schema/model/config and write
them in deterministic order. The content manifest should match across builds;
operational metadata such as build time can live in a separate non-hashed
attestation if needed.

On mismatch, compare canonical payloads field by field rather than accepting
new hashes. Reproducibility does not prove model quality, but it makes lineage
and review significantly stronger.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 10 — write a claim-bounded model card

**Prompt recap:** Create a model card from the manifest and evaluation evidence: intended and excluded use, population, metric/threshold, slices/support, data provenance, limitations, monitoring, owners, and stop conditions.

**Reasoning path:** Generate measured fields from the same result object and keep policy prose versioned. Do not claim causality or production readiness from offline metrics.

Every headline value includes dataset/split identity, unit, denominator, and
uncertainty where appropriate. The card names populations not represented,
known failure modes, human oversight, and what evidence would require rollback
or retraining.

Treat the card as release evidence reviewed with the artifact, not static
marketing text. A missing or stale card blocks promotion under the local policy.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 11 — design shadow and canary evidence

**Prompt recap:** Specify a no-side-effect shadow comparison followed by a bounded canary. Define routing, success/guardrail metrics, sample/time minimums, stop rules, rollback, and how delayed labels are handled.

**Reasoning path:** Shadow predictions do not affect decisions; canary output does. Both need versioned request/prediction identity and privacy-safe telemetry.

Shadow mode compares compatibility, latency, score distribution, and matured
outcomes without exposing users to candidate decisions. A canary receives a
small controlled share only after shadow gates pass. Predeclared safety,
quality, capacity, and error thresholds trigger automatic pause/rollback.

Do not repeatedly inspect and expand based on ordinary noisy metrics. Preserve
assignment and label-maturity windows for valid comparisons.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 12 — separate drift from compatibility

**Prompt recap:** Create examples of schema incompatibility, valid schema with shifted distribution, and stable inputs with performance degradation. Route each to reject, monitor/investigate, or rollback/retrain policy.

**Reasoning path:** Compatibility is a hard interface check; drift and quality are statistical evidence with support, reference, and action thresholds.

Missing/reordered/wrong-type required features fail before prediction.
Distribution shift with a valid schema can continue only under the reviewed
monitoring policy; report support and reference period. Performance degradation
requires matured labels and may trigger rollback even when input drift metrics
look stable.

Do not coerce an incompatible input merely to keep serving, and do not treat a
PSI threshold as proof of model failure.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 13 — test forward and backward compatibility

**Prompt recap:** Build a matrix of producer/consumer schema and model versions. Test an additive optional field, required rename, reordered feature, and changed numeric meaning across old/new readers.

**Reasoning path:** Define compatibility from each consumer's contract; semantic changes may be breaking even when JSON types match.

Old readers may ignore an additive optional field only when they select known
fields. New readers can supply a documented default for old payloads. Required
renames, position changes in ordered models, and unit/meaning changes require a
new version or explicit migration.

Store migrations as tested code and preserve the original payload identity.
Never relabel a semantic change as additive because parsing still succeeds.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 14 — capture dependency and supply-chain evidence

**Prompt recap:** Create a local release manifest containing reviewed lock hash, direct runtime requirements, Python range, package major versions, artifact hashes, source revision/dirty flag, and a generated component inventory.

**Reasoning path:** Keep portable names/versions/hashes; omit credentials and developer paths. An inventory is evidence, not a vulnerability verdict.

Compatibility checks consume only declared runtime requirements, while the
lock/inventory supports reconstruction and security review. Record the exact
tool/version that produced each file and fail promotion when required evidence
is absent or inconsistent.

Scanning/signing systems are optional authorized extensions. Do not invent an
SBOM standard claim unless output validates against that standard.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 15 — verify artifact trust before parsing

**Prompt recap:** Model a trusted local manifest root and verify every bundle file's relative path, size, and SHA-256 before JSON parsing. Reject path traversal, symlink escape, extra required files, and pickle.

**Reasoning path:** Resolve paths under the bundle root without following an escape. Hash bytes first and accept only an allowlisted safe format.

Validate the manifest structure, normalize relative paths, and ensure resolved
files remain beneath the expected root. Reject symlinks or special files under
the strict lesson policy. Compare size and digest, then parse flat/canonical
JSON and validate schema.

A hash from an untrusted manifest does not establish trust; the manifest root
must arrive through an approved distribution boundary. Pickle/joblib remains
unsafe for untrusted content.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 16 — rehearse rollback dependency failure

**Prompt recap:** Archive version 1, promote version 2, then discover that version 1's runtime dependency is unavailable. Define rollback-target readiness, fallback decision, event trail, and prevention.

**Reasoning path:** A registry stage is not enough; periodically load and smoke-test retained rollback bundles in their compatible runtime.

Before promotion, verify at least one rollback candidate has artifact,
manifest, runtime, schema, and representative fixture evidence. If v1 cannot
load during incident response, do not mark rollback successful; pause/route to
the last verified candidate or safe degraded behavior and record the failure.

Add scheduled restoration drills and retain required runtime artifacts/locks.
The event trail preserves original incident, attempted target, rejection
reason, final action, and owner.

**Common trap:** A high metric or artifact hash cannot compensate for leakage, incompatible schema/runtime, untrusted serialization, missing tests, or a rollback target that no longer works.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.
