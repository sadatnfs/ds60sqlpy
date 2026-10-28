# Ballista workshop maintenance

Use the root/course guidance and repository Add a learning path skill. Keep the
released Ballista 54.1.0, DataFusion 54 and Arrow 23 environment separate from the
ordinary DataFusion 55 worker. Native wheels require glibc 2.39 or later; prepare
AMD64/ARM64 explicitly, never silently emulate another architecture.

The supported route has separate real scheduler, executor and client processes
in one container namespace. The released Python wrapper does not expose the
scheduler's advertised external host, so a separate-container trial failed even
though listeners were ready. Preserve that evidence; do not rewrite localhost
DNS or claim cross-host shuffle or multi-executor availability.

Task-slot changes are explicit quiescent reconfigurations of the native pair.
A failed/unknown request is retained and its client reaped before an explicit
fresh request. Saved evidence inspection never replays a query. Default scheduler
state is not qualified as durable job-history storage.

Keep independent row/count/sum oracles. A removed Parquet listing can return empty
rather than throw; source correctness is not a zero-exit-code assertion. Bound
Parquet metadata before materialization and keep immutable canonical data separate
from temporary negative fixtures and bounded receipts.

Receipt storage must be atomic, preserve existing completed/pending state, and
print the actual execution outcome with a distinct storage warning on save failure.
The private control socket owns exact subprocess objects and tolerates observer
disconnects. Never target arbitrary host processes or mount an engine socket.

Use ownership/native-image guards, exact resume, retained-volume replacement and
confirmed scoped deletion. Do not prune unrelated resources. The native Rust
extension is separately prepared and must not be described as compiled or runtime
qualified merely because the Arrow-only Rust classroom image works.
