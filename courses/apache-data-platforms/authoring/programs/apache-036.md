# Real transactional visibility

The prepared Java compile path uses the explicit binary workshop route.

```bash
bash run.sh check-transactions
```

Expected actual result: `committed_records:3`, `uncommitted_records:4`,
`aborted_hidden:true`, and two retained distinct duplicate business send calls.
The implementation checks exact payloads in addition to these counts.

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check-transactions
```

The checker validates retained transaction evidence and does not append again.
Read the complete `TransactionProbe.java` source before modifying transaction
identity, isolation mode or offset handling. A different workload requires a
separately identified fixture, not deletion of unexpected retained data.
