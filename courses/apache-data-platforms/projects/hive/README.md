# Owned Hive 4.2.1 and Metastore project

This is a prepared actual-product Docker route for PostgreSQL-backed Metastore,
HiveServer2/Beeline, independent Java Thrift metadata and a Parquet warehouse.
Native Linux ARM64 SQL/Thrift and retained-state acceptance passed; no simulated catalog counts as Hive. The
pinned release runs on Java 21. Its official image supplies a JRE; the separately prepared java21 worker supplies the JDK for compilation. Source/schema
checks, platform descriptors and live execution are separate evidence.

Prepare the ordinary data-platforms-python and java21 images, then copy this directory to
`work/apache-hive`, then use the copied directory:

```bash
bash run.sh prepare
bash run.sh start-db
bash run.sh initialize-schema
bash run.sh start
bash run.sh initialize
bash run.sh check
bash run.sh metadata
bash run.sh explain
```

Prepare explicitly pulls pinned native official Hive/PostgreSQL inputs and
prepares the PostgreSQL 42.7.5 JDBC JAR with a checked digest. It never requests
emulation or disables TLS. The Hive image is large, approximately 1.5 GB compressed;
allow additional storage for extraction, named metadata/warehouse state and
engine overhead. The aggregate steady-state service limits total 3.5 GiB; allow
at least 5 GiB available memory including one-shot clients. No host ports or Docker
socket are exposed. Fixture credentials are private to this isolated synthetic
network and are not a production authentication design.

Schema initialization is explicit and never an automatic upgrade during resume.
`verify-schema` reads version information. Startup verifies schema before serving.
The stock upstream image's automatic initOrUpgradeSchema entrypoint is overridden.
Initialize writes only the known Parquet fixture and idempotent owned DDL. Check
is read-only and requires exact rows 1/east/4, 2/west/9 and 3/east/7 plus a real invalid
column failure. Metadata runs the separately prepared Java HiveMetaStoreClient and
checks the actual external-table schema, location and partition without reading
the Parquet bytes. Explain shows a selective aggregate's actual plan.

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check
bash run.sh metadata
bash run.sh down
bash run.sh start
bash run.sh check
bash run.sh metadata
```

Readback must not call initialize. Resume reuses exact containers; replacement
retains PostgreSQL and warehouse volumes. Keep `.env` with the copied project.
The launcher verifies resource ownership before mutation. Native AMD64 execution
belongs on a native AMD64 runner, separately from native ARM64 acceptance.

`iceberg.hql` is a separately prepared extension using Hive 4.2's bundled Iceberg
support. It requires its own snapshot/schema/delete-compatibility observations.
The default Parquet route does not prove ACID or Iceberg commit semantics.

Export an owned PostgreSQL dump and schema/file identity before testing an
upgrade or restore. A wrong schema version must fail verification, never trigger
automatic migration. Binaries rolling back do not roll back database schemas.
Only verified disposable copies may be used for a restore game day.

```bash
bash run.sh destroy --confirm-owned-data-loss
```

This optional final command deletes only verified owned synthetic state.

## Native JDK preparation without a duplicate client image

The official Hive image contains JRE21, not javac. Explicit prepare therefore
copies the actual pinned Hive/Hadoop classpath temporarily into this owned
`.workshop/` directory and invokes the already prepared native java21 JDK worker
to compile MetadataProbe.java with `--release 21`. It retains the class plus
source/class/Hive-image/JDK-image hashes in one canonical identity.tsv record, then removes only its temporary public
classpath copy and verified stopped preparation container. No host SDK or new
client image layer is required. Repeated prepare verifies the accepted class;
changed source/images require a fresh owned copy. Runtime metadata reads verify
source/class/image identity and use the Hive JRE's actual release libraries.
An interrupted preparation retains an ownership record for reconciliation rather
than silently replaying or overwriting derived state.


## Preparation failures and identity checks

Prepare acquires the same PID-marked lock used by normal lifecycle actions, and
metadata compilation has a separate atomic lock. It cannot run concurrently with
another action in the same copied directory. No image is rebuilt or downloaded by
resume, check or metadata.

The metadata helper creates exact labeled containers for the stopped classpath
source and the compiler or verifier. It invokes the JDK with the host user's UID
and GID so a read-only container with dropped capabilities can write only its
owned preparation directory. Both roles use inspected immutable image IDs.
Cleanup checks owner, role, image and state, stops/reaps a known running compiler,
and confirms that the owned container set is empty before removing temporary
classpath files. It never stops unrelated containers.

An uncertain state retains `.workshop/preparation.owner`, the preparation lock and
the associated stage for inspection. An accepted class does not hide a failed
cleanup. Do not remove these markers and rerun blindly: inspect the recorded
owner and matching `org.ds60.workshop.owner` / `org.ds60.workshop.kind` container
labels, establish that no compiler can still write the stage, and reconcile only
those exact owned resources. No automatic workload replay is attempted.

The accepted client contains only `classes/MetadataProbe.class` and `identity.tsv`.
Preparation and the JRE-side verifier check the same bounded canonical record;
there are no independent editable hash sidecars. Before execution, the runtime
also matches the actual selected Hive image identity and current source/class
bytes. Changed or incomplete preparation fails without replacing an accepted
class. Do not hand-edit this derived identity to make a failed check pass.

The Thrift oracle checks the exact table name, external-table type, column names
and types, partition key/type, partition value and both locations. Three fields
or one partition alone do not establish that contract. The additional
`typed_schema_checked` and `partition_identity_checked` observation fields report
those checks; they do not replace SQL row and negative-query acceptance.

## Explicit digest-identical mirror

If the official registry blob endpoint fails verified TLS, a fresh owned copy can
select `bash run.sh prepare --mirror`. This uses mirror.gcr.io for exactly the
same reviewed native Hive and PostgreSQL manifests from the pinned indexes, not a different release or a
moving tag. The fixed architecture map selects only the actual native engine. Docker verifies content by those digests and still selects the native
engine platform. Certificate checks remain enabled. This is an explicit download
source choice; normal start/resume never fetches software.

The isolated fixture explicitly disables Metastore notification-API authorization
so its local HiveServer2 process can perform the startup event poll. The first
actual run retained the real denied-call diagnostic. This setting belongs to the
synthetic private-network lab; this project does not demonstrate a production
Metastore authorization policy or an authenticated multi-user warehouse.
