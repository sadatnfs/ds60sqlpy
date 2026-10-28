# Data visibility and delayed failure

From the copied, prepared Ballista workshop:

```bash
bash run.sh start
bash run.sh paths
```

The positive read must match the canonical fixture. The negative case registers a
separate disposable Parquet copy, removes only that copy, and detects the actual empty result with an independent row-identity oracle while preserving the canonical source checksum.

```bash
bash run.sh check
bash run.sh evidence
```

A single-host shared mount is not a multi-host filesystem qualification. Inspect
the complete client source before adapting the paths to another storage system.
