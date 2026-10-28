# Hive apache-065 command notebook

Run from the copied owned Hive project, following its README. Native service
acceptance is separately recorded in QUALIFICATION.md.

```bash
bash run.sh metadata
bash run.sh stop
bash run.sh resume
bash run.sh metadata
bash run.sh check
```

For replacement, use down/start then only check/metadata. Never initialize while testing retention. Compare database and warehouse ownership separately.

The classroom does not execute these Docker commands. Retain source, schema,
file identities, actual responses and failure scope in an independent receipt.
