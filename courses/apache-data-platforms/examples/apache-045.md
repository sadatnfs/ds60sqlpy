# Real Flink stream and SQL entry points

From the repository root, copy the complete project into a fresh owned directory.
Prepare the native Java17 base and selected pinned runtime as documented there.

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/flink work/flink
cd work/flink
bash run.sh prepare --binary
bash run.sh start
bash run.sh check
bash run.sh check-sql
bash run.sh readback
```

The code is compiled inside the prepared container; no host Java, Maven or SDK is
required. The check distinguishes compilation, actual submitted job completion,
exact source identity and output rows. See the qualification ledger before
interpreting a prepared extension as an exercised runtime path.
