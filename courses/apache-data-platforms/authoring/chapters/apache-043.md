## Logical deletion and physical deletion have different consequences

Deleting a row from a versioned table changes the current logical view. It does
not necessarily erase every older physical representation immediately. Retained
snapshots may still reference files containing the old row. Some writers rewrite
affected files, while table formats also support delete representations with
specific reader/writer compatibility requirements. A complete policy must name
which mechanism was used and which history remains accessible.

Snapshot expiration removes selected historical references under the table's
retention rules. Physical orphan cleanup is a separate operation and must avoid
files still referenced by retained snapshots or active writes. Deleting every
file whose modification time looks old is unsafe. A file can be old and still
be the only copy of data referenced by the current table.

The executable uses real PyIceberg delete and snapshot-expiration commits in a
temporary fixture. It never points maintenance at learner data or an external
warehouse. It records file bytes before and after metadata expiration so the
learner can see that removing a snapshot reference is not the same claim as
having physically erased all underlying objects.

## Worked case A: remove an order from the current view

After the initial three-order append, the program records the first snapshot.
It then deletes order 1. The current read returns only orders 2 and 3 with total
16, while reading the retained first snapshot still returns all three orders
with total 20. Exact order identities prevent a misleading count-only check.
The earlier state is deliberately still available at this point.

This is useful for rollback and audit, but can conflict with a requirement to
erase personal information. A logical deletion alone is not a complete privacy
erasure procedure. Such a procedure must consider retained snapshots, copies,
backups, downstream exports, legal retention and the storage system's behavior.
The synthetic order fixture contains no personal information and does not claim
to implement a regulatory compliance workflow.

Inspecting current planned files can reveal that the writer produced replacement
files, but it does not establish all implementation strategies for every engine.
Readers and writers can support different delete modes or table format versions.
Compatibility must be checked for the actual components rather than inferred from
both products supporting the word Iceberg.

## Worked case B: expire one unprotected historical snapshot

The second case expires the recorded first snapshot by its exact identifier.
The current snapshot remains protected and readable. The program verifies the
old identifier is absent from the table's snapshot list, while the current result
still contains orders 2 and 3. It also checks that the previously observed files
remain present on disk in this metadata-maintenance operation.

The distinction is deliberate. A learner should not conclude that expiration
already reclaimed all historical disk space. A physical cleanup procedure would
need its own reference analysis, minimum age, concurrency protection and exact
byte observations. The example does not run such deletion, because doing so would
broaden the destructive boundary and obscure the metadata lesson.

A tag or branch can protect a snapshot that a retention job would otherwise
select. Retention policies should account for named references and reproducible
training datasets. Keeping every snapshot forever, however, can retain old files
and inflate storage. The practical tradeoff is an explicit recovery window with
known downstream reproducibility requirements.

## Diagnosis and interview discussion

Before maintenance, record current snapshot, retained references, expected row
identities and the precise cleanup scope. After maintenance, verify the current
query and any promised retained reference. Keep physical-byte reclamation metrics
separate from snapshot-count changes. An error must not trigger a broad reset of
the warehouse, catalog database or Docker volume.

**Interview discussion: why can storage stay large after deleting most rows?**
Old snapshots can still reference previous files, the writer may have created
replacement data, and metadata expiration may not perform physical deletion.
These two cases make the logical view, retained history and actual file presence
independently observable, which is necessary before choosing a safe maintenance
and retention plan.
