# Hive apache-063 command notebook

Run from the copied owned Hive project, following its README. Native service
acceptance is separately recorded in QUALIFICATION.md.

```bash
bash run.sh prepare
bash run.sh start-db
bash run.sh initialize-schema
bash run.sh start
bash run.sh initialize
bash run.sh check
bash run.sh metadata
```

The metadata probe reads actual Thrift table/partition metadata independently from Beeline and data files.

The classroom does not execute these Docker commands. Retain source, schema,
file identities, actual responses and failure scope in an independent receipt.
