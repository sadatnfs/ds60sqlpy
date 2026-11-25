# Integration apache-082 complete worked notebook

Prepare a separately owned combined Kafka/Flink/Pinot route. Capture actual connector versions, private DNS, source offsets, checkpoint/sink state and exact serving IDs. Exercise duplicate and late-correction rules; component receipts alone do not qualify the whole path.

## What this streaming receipt must hold

- The integration topic name, partition count and end offsets after the single produce.
- The Flink job ID, parallelism, watermark policy and the last completed checkpoint ID.
- The sink connector name and version, and whether it joins the checkpoint commit.
- The Pinot table name, decoder class, offset reset policy and consuming segment names.
- The broker query result as stable event IDs with amounts, not only a row count.
- The duplicate ID, the correction version and what serving returned for each.

Reconcile three ledgers before writing any verdict: Kafka offsets, Flink
checkpoint state and Pinot query rows. Producing the three orders once should
leave three offsets, three logical events and a total of 20. After the duplicate, Kafka
holds four records while a deduplicating route still serves three IDs. A served
total of 29 means the duplicate of order 2 was counted. The
[shared receipt rules](../../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../pinot/realtime-table.json
cat ../flink/README.md
cat ../streaming/README.md
```

In `realtime-table.json`, the topic `ds60-orders`, the broker list `kafka:9092`
and `auto.offset.reset` set to `smallest` decide where Pinot starts reading. A
combined route needs its own topic name so that the Pinot table never consumes
the streaming workshop's retained records. None of these files proves a combined
topology ran; they show which settings must agree across the three projects.
