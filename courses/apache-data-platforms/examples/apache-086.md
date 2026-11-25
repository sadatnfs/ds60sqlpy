# Integration apache-086 complete worked notebook

Select one already qualified owned workshop. Compare exact resume and retained-state replacement using read-only identity actions. Break one configuration only in a separate disposable copy and retain its typed failure.

## What this game day receipt must hold

- The selected workshop, its source hash and the image ID it ran.
- Container IDs before stop, after resume and after down/start replacement.
- The read-only check result at each boundary, run without any initialize step.
- The single configuration change made in the disposable copy, as a diff.
- The first typed diagnostic the broken copy produced.
- The restored check result and confirmation that the learner's volume was untouched.

Container IDs carry most of this oracle. After resume they must match the IDs
taken before stop. After down/start they must differ while the semantic check
still passes over the same volume. For Cassandra, that check compares host UUID,
replication settings and the exact order rows. For Kafka retention, it compares
end offsets and the latest value per key. Equal IDs after replacement mean down
never ran. The [shared receipt rules](../STUDY-GUIDE.md#evidence-receipts)
cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../cassandra/README.md
cat ../streaming/QUALIFICATION.md
```

The Cassandra README's lifecycle block runs `stop`, `resume`, `check`, then
`down`, `start` and `check`. Down removes owned containers and the network but
keeps the data volume. The Kafka qualification ledger records end offset 3 and
latest-key state preserved across repeat, resume and replacement, with physical
compaction not demonstrated. Use those recorded facts as the expected values.
