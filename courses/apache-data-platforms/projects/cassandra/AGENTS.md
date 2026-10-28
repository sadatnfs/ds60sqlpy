# Cassandra workshop guidance

Use the root and course authoring contracts. This is a copied owned Docker project,
not an ordinary classroom executor. Main tutorial units are reading notebooks;
opening or editing them must not start services or download packages.

The binary distribution is Apache Cassandra 5.0.9 with a verified published SHA512.
Its base is the prepared Scala/JVM image specifically for Java 17. Preserve procps
and explicit heap/direct-memory limits; upstream auto-sizing can inspect the full
VM rather than its container budget. Driver packages are prepared from separate
native AMD64/ARM64 hash locks, with no installation during a lesson. Never silently
use Java 21 or AMD64 emulation on an ARM engine.

Single and three-node topologies use unique labels, declarative saved settings,
PID locks, local Unix-socket engines and no host ports or engine socket mounts.
A saved single-node copy cannot silently become a replicated cluster. Legacy
settings without a topology field mean single. Resume reuses all retained exact
container identities without pulling/building; down retains state. Destruction
requires explicit owned-data confirmation and never affects other projects.

The fixed coordinator policy makes namespace and replica experiments reproducible.
It is a teaching fixture, not a general production load-balancing recommendation.
Only the declared node names may enter generated configuration. Health probes must
connect to their own node. Preserve composite customer/day keys, UTC semantics,
clustering ties and independent row identities. Unexpected retained data is an
error, not permission to reset a table.

Unavailable and index-building diagnostics can be wrapped by the Python driver.
Inspect actual underlying causes and exact replica counts or the specific index
readiness category. A connection failure or unrelated read error cannot satisfy a
negative consistency/index case. Controlled outages stop only verified owned nodes,
restore those exact containers and keep unknown/interrupted outcomes explicit.

Snapshot/SSTable restore is limited to the single-node fixture. Keep compatible
schema and correct keyspace/table staging directory names; tool exit zero does not
prove any rows were imported. Verify exact source/target rows and component hashes.
Never truncate/drop original tables or delete live SSTables. Up to four separate
restore targets remain as evidence until explicit project destruction. Receipts
use atomic create without overwrites. Preserve actual restore success and report
storage/cleanup warnings separately, with no blind retry of an unknown outcome.

Keep source, pure-contract tests, native service operation, exact resume,
replacement, replicated outage and remote-backup claims separate. Local acceptance
uses native ARM64 only. Native AMD64 execution belongs to hosted runners; portable
locks/manifests do not establish runtime acceptance. Follow the parent owner's
resource queue before starting a large pack, and leave shared CI/runtime/UI changes
to their assigned owner.
