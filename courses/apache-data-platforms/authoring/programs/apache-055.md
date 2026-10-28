# Conditional state and actual SAI

```bash
bash run.sh check
```

The CQL client performs a known compare-and-set, checks `[applied]`, rejects a
stale comparison and conditionally restores only the known probe value. It
creates a real Storage Attached Index, waits for its queryability and compares
exact selective-query order identities against the independent fixture.

A conditional mutation protects the stated partition transition, not an external
payment, email or second table. A successful three-row index query establishes
API and result correctness; production selection requires cardinality, update,
latency, disk and memory measurements.
