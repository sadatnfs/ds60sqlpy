# Rust validation scope

All 48 published references passed the actual worker `execute_operation` path with `isolate_user=True` in the prepared Rust1.99.1 and Arrow60 Linux ARM64 image. The checks retained the normal 32 MiB scratch/file allowance, unprivileged learner identity, no network, read-only image, bounded temporary storage, process count, memory and CPU. Every accepted receipt's source hash matches the published reference.

The executed Arrow examples use actual typed arrays, null validity, RecordBatch schema checks, filter/take kernels, nested list builders, sliced arrays, IPC writers/readers, CSV/NDJSON readers, decimal precision/scale and timestamp types. They do not replace Arrow with local imitation classes. The initial reader check exposed a generator newline defect; the durable source was corrected and the affected current references were executed again.

The separate InventoryLab Cargo package passed four integration tests and its executable under `--locked --offline` in a disposable Linux workspace. Its simple two-field input is intentionally not advertised as a general quoted CSV parser. The Arrow CSV chapter uses the actual library parser.

All 194 generated route, manifest and teaching artifacts reproduced without drift. The subject's Python authoring sources pass scoped lint and format checks, and shared module admission recognizes all 48 lessons. External Tokio, Parquet, DataFusion, PyArrow and C Data Interface integration remain separately prepared project surfaces and are not claimed executed by these references.

These checks establish the tested Linux ARM64 source behavior, not every architecture, engine configuration, external project or absence of undiscovered defects. Browser delivery and repository release CI are separate integration gates. Validation containers were disposable, mounted no learner volumes and were removed after execution.
