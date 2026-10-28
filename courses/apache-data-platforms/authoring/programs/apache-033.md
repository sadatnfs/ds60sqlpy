# Real topic, keyed records and independent readers

Copy `projects/streaming` to a fresh owned directory and follow its README to
prepare either the pinned upstream image or explicit verified-binary route.

```bash
bash run.sh start --binary
bash run.sh check
bash run.sh check
bash run.sh check-consumers
```

The first two checks must retain exactly three keyed records across two partitions.
The Java probe must report uncommitted replay, zero records after group A's
committed resume, and three records for an independent group. It uses manual
assignment and makes no rebalance claim.

```bash
bash run.sh status
bash run.sh logs
```

`--binary` is only needed to select that route initially. A saved upstream route
cannot silently switch provenance. Consumer compilation needs the binary route's
prepared JDK; the ordinary CLI check also supports the official-image route.
