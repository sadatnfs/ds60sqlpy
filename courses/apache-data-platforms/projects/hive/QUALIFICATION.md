# Native Hive and Metastore qualification

Apache Hive 4.2.1 with PostgreSQL 17.6 passed actual Linux ARM64 acceptance on
October 28, 2026. The explicit mirror selected the exact reviewed native manifests
from the pinned upstream indexes, after the official registry blob TLS failure
and missing mirror index-attestation failure were retained. TLS verification
remained enabled, and no local AMD64 emulation was used.

The actual gate initialized and verified a fresh owned Metastore schema, started
Metastore/HiveServer2, registered the three-row Parquet fixture, and required exact
SQL IDs/regions/amounts. A wrong column produced its actual Hive 10004 diagnostic.
A separately compiled Java HiveMetaStoreClient called real Thrift metadata APIs
and verified column names/types, table type, day key/type, partition value and
both storage locations. The missing-table API produced its intended exception.
The metadata client did not read the Parquet data files.

Repeated observations and lifecycle readback were read-only. Exact stop/resume
retained the three service container identities. Replacement changed all three
container identities while preserving prepared image identities and the database,
warehouse, SQL and typed metadata observations. The qualifier did not call schema
initialization, fixture writing or DDL during readback. Owned container/network/
volume absence and retention of every pre-existing volume were confirmed.

The two Hive-specific scripts are initialize.hql and iceberg.hql. Their rename
from .sql retained identical bytes, recorded independently before a fresh native
path/source requalification. PostgreSQL's parser is not claimed to validate Hive
syntax. The ordinary explain.sql query uses compatible basic SELECT grammar.

Native preparation used the existing java21 JDK worker to compile against exact
release SDK jars with annotation processing disabled. The accepted artifact binds
source/class/Hive-image/JDK-image identity. Runtime verifies the canonical record,
copies the small class to container-local temporary storage and uses actual Hive/
Hadoop release libraries. This avoids repeated Java classpath checks against a
Mac host bind mount. Beeline's pinned JLine client uses explicit Java 21 preview/
native-access and pseudo-terminal settings for its batch execution.

The isolated synthetic lab disables notification-API authorization so its local
HiveServer2 process can perform the startup event poll. Actual denied-call and
client-preparation diagnostics remain separate from corrected-source acceptance.
This is not a production multi-user authorization or authenticated warehouse test.

Native AMD64 remains a separate hosted-runner gate. Hive ACID, Iceberg integration,
metadata upgrades/remote backup, distributed Tez/YARN operation, arbitrary external
clients and cross-host disaster recovery remain prepared extensions with their
own required evidence. The default Parquet/Thrift path does not qualify them.
