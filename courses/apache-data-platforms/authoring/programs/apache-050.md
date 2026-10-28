# Explicit state points and a negative mapping case

```bash
bash run.sh savepoint
bash run.sh readback
```

The route records an actual completed state point, checks the deliberately changed
UID failure without allowing dropped state, and restores the compatible program.
Only a verified owned savepoint path can be selected. Prior outputs and source
identities are retained during diagnosis.

```bash
bash run.sh stop
bash run.sh resume
bash run.sh readback
```

Container resume and savepoint restore are different operations. Readback never
silently starts a job. See the complete project ledger for what was actually
qualified and which external transactional-sink or HA routes remain separate.
