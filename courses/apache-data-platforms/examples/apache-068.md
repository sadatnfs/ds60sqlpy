# Hive apache-068 command notebook

`verify-schema` asks the Hive schema tool to compare the Metastore database with the Hive 4.2.1 schema, while `status` and `logs` only report container state and recent output. None of the three changes the database in the copied Hive project.

```bash
bash run.sh verify-schema
bash run.sh status
bash run.sh logs
```

Test upgrade/recovery only against a separate owned database copy with a retained consistent dump. Do not alter the live fixture version row or use automatic schema upgrades to suppress failure.

Metadata upgrades and remote backup are prepared extensions in QUALIFICATION.md. Record the dump identity, the schema version before and after, and the name of the separate database copy, so recovery never touches the live fixture.