# Hive apache-064 command notebook

Run from the copied owned Hive project, following its README. Native service
acceptance is separately recorded in QUALIFICATION.md.

```bash
cat initialize.hql
cat fixture.py
bash run.sh check
bash run.sh metadata
```

Use separately named copied-owned tables for wrong-type and wrong-location experiments. Record the actual reader response; an empty location and an incompatible schema are different conditions.

The classroom does not execute these Docker commands. Retain source, schema,
file identities, actual responses and failure scope in an independent receipt.
