# Storage and timestamp observations

```bash
bash run.sh check
bash run.sh identity
bash run.sh logs
```

The checker writes known competing cell versions with explicit microsecond
timestamps and independently requires the greatest-timestamp value. Its clustering
range selects order 3, while a full selected partition returns orders 3 and 1.
`identity` performs read-only retained-order inspection without initializing data.

To extend this observation, record actual nodetool metrics and SSTable metadata
around a controlled flush. A successful row read alone does not identify the
physical file that supplied it. Do not delete individual files to change a result.
