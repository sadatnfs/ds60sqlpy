# apache-088: An auditable data-platform capstone

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-081`, `apache-082`, `apache-083`, `apache-084`, `apache-085`, `apache-086`, `apache-087`.

## Key terms

- **Evidence dossier:** The reviewable record of what was built, the bounded input, the expected result and which stages were only parsed, compiled or configured.
- **Acceptance criterion:** A stated, source-bound result that a capstone run must reproduce exactly before it counts as passing.
- **Qualified workshop:** A course workshop whose actual components have run and been recorded in its qualification ledger, unlike one that is only prepared.
- **Owned lifecycle:** Starting, retaining and destroying only the capstone's own labeled resources, with destruction requiring explicit confirmation.

## A capstone is a reviewable evidence dossier

An auditable data-platform capstone selects a coherent path and demonstrates its
actual contracts. It does not need to start every product in the course at once.
A narrow supported implementation with exact source, result and recovery evidence
is more informative than a large diagram whose services or guarantees were never
exercised together.

Choose an embedded batch path, a qualified Arrow Flight/Kafka/Cassandra workshop,
or a separately prepared native integration whose required components are
available. State prerequisites and omitted features before running. The Atlas
and Delta Sharing native-server alternatives remain prepared until real server,
backing storage and client exchanges qualify them. Source presence alone does
not change that status.

The dossier should let another contributor understand what was built, reproduce
the bounded input, recognize the expected result and distinguish a failed stage
from a different experiment. It should also identify which parts were only parsed,
compiled or configured. A final success flag without those boundaries is difficult
to review and easy to overinterpret.

## Worked case A: deliver one source-bound implementation

Select one path and record its maintained source revision/hashes, dependency or
image identities, actual native platform and owned resource names. Run its exact
positive and negative checks with the deterministic order fixture. Save logical
source IDs/values, relevant schema/state positions and an independent business
result oracle.

For the Flight path, actual RPC/schema/null/value checks and compiled Rust/Python
IPC are different observations. For Kafka, noncompacted source positions,
transaction visibility and compacted latest-key state have different stable
projections. For Cassandra, RF1 API behavior and the actual RF3 outage are separate
topologies. Use the product's real contract rather than reducing all evidence to
one row count.

Write a concise architecture explanation naming ownership of storage, transport,
execution, catalog and governance. Include the concrete trigger for each operation
and the boundary at which it becomes visible. Link primary product references,
prepared versions and project commands so another native environment can follow
the same supported route without hidden host SDKs.

## Worked case B: independently verify failure and recovery

Have the checker read accepted state without initialization, then perform exact
stop/resume and retained-state replacement where the chosen route supports them.
Compare process identity, software identity and semantic state independently.
Inject one bounded typed failure on a separate owned experiment and verify that
its diagnostic matches the intended contract.

Keep the failed receipt, corrective source change and fresh qualified result
separate. A historical successful run cannot qualify changed behavior, and a
format-only source parity record does not represent new service execution.
Native ARM64 results also do not establish native AMD64 behavior; that architecture
needs its own actual native runner acceptance.

Export needed evidence before confirmed owned-data destruction. The cleanup
report should show only the experiment's verified containers/networks/volumes
removed, with original learner state retained. If cleanup or evidence storage
fails, report it explicitly rather than pretending the computation rolled back
or silently rerunning a completed action.

## Diagnosis and interview discussion

Review the dossier for unexplained assumptions, untested connectors, credential
leaks, unsupported feature claims and ambiguous identities. A result can be useful
while retaining limitations. State those practical boundaries so future work can
extend the right acceptance gate rather than repeating an unrelated successful
check.

**Interview discussion: what makes a data-platform project auditable?** A clear
contract, actual source/runtime identity, independent semantic and failure oracles,
retained-state readback and a reproducible owned lifecycle. These cases deliver
one concrete path and then independently challenge its recovery claims, producing
evidence another engineer can assess without trusting the author's summary alone.

## Worked examples

### Hash the sources a dossier depends on

```bash
cd work/integration
shasum -a 256 batch_snapshot.py run.sh
```

Each line pairs a SHA-256 digest with a file name. The receipt from batch_snapshot.py already embeds its own source hash; comparing that value with this command shows the reviewed code is the code that ran. A reviewer who gets a different digest should treat every result in the dossier as unverified until the mismatch is explained.

### Check that the dossier states its boundaries

```python
receipt = {
    "passed": True,
    "fresh_catalog_readback": True,
    "wrong_catalog_rejected": True,
    "direct_spark_or_iceberg_datafusion_connector_qualified": False,
}
required = ["passed", "fresh_catalog_readback", "wrong_catalog_rejected"]
missing = [key for key in required if receipt.get(key) is not True]
print("missing:", missing, "declared unsupported:", [k for k, v in receipt.items() if v is False])
```

```text
missing: [] declared unsupported: ['direct_spark_or_iceberg_datafusion_connector_qualified']
```

The fields come from the integration receipt. A good dossier states both what passed and what was not qualified; here the Spark connector route is declared false rather than omitted. A reviewer can then see at once that the capstone proves the Iceberg, Arrow and DataFusion path and makes no claim about Spark.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Integration apache-088 complete worked notebook

Assemble source/config hashes, actual image/platform identities, positive/negative results, exact resume/replacement, cleanup and explicit unsupported/prepared boundaries into one reviewable dossier. Select a coherent path rather than launching every product.

## What this dossier must hold

- One named path and the reason it was chosen over the others.
- The maintained source revision and hashes for every file the path runs.
- The image ID and native platform that produced each observation.
- The positive check, the typed negative check and their exact outputs.
- Resume and replacement results, using the same read-only checker.
- The cleanup list, naming only the experiment's containers, networks and volumes.

A reviewer should be able to rebuild every verdict in the dossier from its own
fields. Check that every observation cites the image and platform it ran on, so
an ARM64 run is never presented as AMD64 evidence. Check that each negative
result names the expected failure before the observed one. Keep any feature that
was only prepared, such as a combined streaming topology, in a separate list. The
[shared receipt rules](../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat README.md
cat batch_snapshot.py
```

The integration README separates three routes: the actual bounded batch dossier,
a real service dossier through a qualified workshop, and prepared combined
routes. Choose one before writing anything. `batch_snapshot.py` shows the receipt
shape the batch route already writes, including the explicit false for direct
connector acceptance, which is a good model for every unsupported claim.

## Primary references

- [Arrow Flight RPC protocol](https://arrow.apache.org/docs/format/Flight.html)
- [Kafka transactions and log compaction](https://kafka.apache.org/44/design/design/)
- [Cassandra replication guarantees](https://cassandra.apache.org/doc/5.0/cassandra/architecture/guarantees.html)
- [Iceberg snapshot reliability](https://iceberg.apache.org/docs/latest/reliability/)
