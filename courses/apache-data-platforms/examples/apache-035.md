# Replay and committed next offsets

```bash
bash run.sh check
bash run.sh check-consumers
```

Inspect `ConsumerProbe.java`: automatic commit is disabled; the first two consumer
instances read without committing; a later instance commits each partition's next
position; the following instance reads zero rows. A different group reads all
three rows. The code closes consumers before deleting only its unique probe group
IDs. The source topic and records remain.

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check
bash run.sh check-consumers
```

This is real Kafka offset behavior with manual assignment. It does not claim an
actual rebalance, broker replication, process-kill injection or external database
atomicity. Keep those evidence boundaries when writing a recovery report.
