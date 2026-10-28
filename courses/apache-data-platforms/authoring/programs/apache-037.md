# Actual broker policy; separately labeled local payload validation

```bash
bash run.sh check-retention
bash run.sh check-retention
bash run.sh check-schema
```

The retained log fixture contains three ordered updates and reconstructs two keys.
The effective topic policy is checked against the real broker. The result must
explicitly say physical compaction was not demonstrated.

`schema_fixture.py` runs a local application reader: additive field accepted,
missing/string/Boolean amount rejected. It requires the binary route's prepared
Python interpreter and does not deploy a schema registry or change broker policy.

Use status/logs to inspect the owned project. Never delete a topic or volume to
conceal an unexpected pre-existing fixture state.
