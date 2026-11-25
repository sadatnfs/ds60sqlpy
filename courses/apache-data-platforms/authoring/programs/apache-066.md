# Hive apache-066 command notebook

`explain.sql` is a plain SELECT over the fixture table, and `run.sh explain` sends it through the admin container of the copied Hive project. Save the full plan text, not a summary of it.

```bash
cat explain.sql
bash run.sh explain
```

Inspect actual partition and aggregate plan operators before claiming a specific engine optimization. Query result correctness and physical work are separate observations.

The accepted Hive gate checked query answers and did not grade plan operators. A claim about partition pruning or aggregation needs the saved plan beside the matching row result.