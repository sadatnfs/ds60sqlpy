# Hive apache-063 command notebook

Run the seven Hive actions in this order from the copied project. PostgreSQL starts first because `initialize-schema` writes the Metastore tables into it, and only `initialize` registers the three-row Parquet fixture.

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

QUALIFICATION.md records this full path as accepted with Hive 4.2.1 and PostgreSQL 17.6 on Linux ARM64. Keep the Thrift metadata answer and the Beeline rows as two receipt entries, because the probe never reads the data files.