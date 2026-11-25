# Checkpoint recovery and bounded guarantee claims

```bash
bash run.sh checkpoint
bash run.sh readback
```

The checkpoint route must observe completion before interruption, identify an
actual restoration and reconcile all final IDs and state. Read the qualification
ledger for the precise exercised topology.

Inside `checkpoint`, the launcher submits the job, waits until the REST API
reports at least one completed checkpoint, then stops and starts the single
`taskmanager` container. The finishing step fails unless the job's latest
checkpoint record says it was restored. `readback` only lists saved receipts and
requests; it submits nothing.

For the independent real Kafka transaction observation, use its separately copied
workshop after stopping this pack:

```bash
bash run.sh stop
```

The Kafka project's `check-transactions` result is not a Flink Kafka-sink receipt.
The compatible connector/sink preparation and recovery boundary are documented
separately; no package is fetched by opening this lesson.
