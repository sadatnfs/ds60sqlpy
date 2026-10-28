# Actual acknowledged writes and distinct application calls

From the copied streaming workshop using its explicit binary route:

```bash
bash run.sh start
bash run.sh check-transactions
bash run.sh check-transactions
```

The fixed probe initializes only an empty fixture topic. It must preserve three
committed records, including two equal business-key/value records from two
separate send calls. Repeating the checker does not append the fixture again.

Read `TransactionProbe.java`: compare `enable.idempotence`, `acks`, delivery and
request deadlines, awaited futures, and transaction completion. These are actual
settings and observations. The probe does not inject network retries or claim
business-level deduplication. Use the earlier local transaction lesson to compare
that different boundary.
