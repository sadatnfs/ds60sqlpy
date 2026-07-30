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

