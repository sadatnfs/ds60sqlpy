# Hive apache-064 command notebook

`initialize.hql` is the DDL that maps `ds60.orders` onto `file:/warehouse/orders` with partition key `day`, and `fixture.py` writes the Parquet rows that DDL expects. Read both in the copied Hive project before the two checks.

```bash
cat initialize.hql
cat fixture.py
bash run.sh check
bash run.sh metadata
```

Use separately named copied-owned tables for wrong-type and wrong-location experiments. Record the actual reader response; an empty location and an incompatible schema are different conditions.

The accepted Hive gate covered one correct table. A wrong column type or a wrong location is your own experiment, and each needs its own table name, DDL and recorded diagnostic so nobody mistakes it for the reference result.