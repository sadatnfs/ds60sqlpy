# Hive apache-065 command notebook

Start and end this lifecycle with `metadata` from the copied Hive project. The probe reads table type, partition key and both storage locations through Thrift, so matching output before `stop` and after `resume` shows the Metastore database kept its state.

```bash
bash run.sh metadata
bash run.sh stop
bash run.sh resume
bash run.sh metadata
bash run.sh check
```

For replacement, use down/start then only check/metadata. Never initialize while testing retention. Compare database and warehouse ownership separately.

QUALIFICATION.md records that stop and resume kept the three service containers, and that replacement changed all three while the database, warehouse and typed metadata stayed the same. No schema initialization ran during that readback.