# Hive apache-068 command notebook

Run from the copied owned Hive project, following its README. Native service
acceptance is separately recorded in QUALIFICATION.md.

```bash
bash run.sh verify-schema
bash run.sh status
bash run.sh logs
```

Test upgrade/recovery only against a separate owned database copy with a retained consistent dump. Do not alter the live fixture version row or use automatic schema upgrades to suppress failure.

The classroom does not execute these Docker commands. Retain source, schema,
file identities, actual responses and failure scope in an independent receipt.
