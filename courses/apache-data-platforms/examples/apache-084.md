# Integration apache-084 complete worked notebook

Read real catalog metadata, register explicitly sourced Atlas identities/lineage, then test the actual protected data operation separately. Metadata classification alone is not enforcement.

## What this governance receipt must hold

- The catalog, database and table names exactly as the Metastore client returned them.
- The table location, schema and selected snapshot or external table properties.
- The Atlas qualified names built from those fields, and the GUIDs Atlas assigned.
- The lineage edges read back from Atlas, with direction, input and output.
- The classification name, who attached it and when it was read back.
- Two engine requests under two fixture principals, with the enforcement point named.

The governance oracle has two halves that must not be merged. The metadata half
passes when the qualified name read back from Atlas matches the observed catalog
identity and the lineage edge points from source to result. The access half
passes only when the allowed principal reads the three orders and the denied
principal receives a typed refusal from the data engine itself. The
[shared receipt rules](../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../hive/MetadataProbe.java
cat ../atlas/README.md
cat ../atlas/client.py
```

`MetadataProbe.java` checks `ds60.orders` as an `EXTERNAL_TABLE` at
`file:/warehouse/orders` with partition key `day`. Those observed fields, not a
display name, are the source for the Atlas qualified name. In `client.py`, the
`plan` action prints prepared payloads without contacting a server. A printed payload is
the request you intend to send, not an entity that Atlas accepted, so record it
separately from any server response.
