# Rust: ownership, reliable systems and Arrow data engineering

From the repository root, prepare this worker with:

```bash
./classroom --profile rust-stable
```

Choose the subject from **All learning paths**. The [setup guide](../../docs/one-command-classroom.md)
explains Docker on macOS, Linux and Windows WSL 2. Use `./classroom stop` and
`./classroom resume` with the same project to retain your source, notes and
results. An explicit profile list replaces the saved runtime selection while
preserving work in its named volume.

This path contains 48 detailed practice chapters, with sixteen beginner, sixteen intermediate and sixteen advanced chapters. Open Rust from the unified Docker classroom. Stable rust-001 through rust-048 identities preserve separate pads, notes and progress. Move at your own pace and revisit prerequisites whenever a mechanism is unfamiliar.

The first stage teaches source/compile/run, types, arithmetic, UTF-8, control flow, functions, ownership, moves, borrowing, slices, structs, enums, Option, Result and a validated importer. The intermediate stage develops traits, generics, lifetimes, iterators, closures, error design, modules, tests, files, collection costs, scoped threads, Arc/Mutex, bounded channels, Send/Sync and smart pointers.

The advanced stage covers futures and executor boundaries, unsafe/FFI reasoning, memory and performance, Cargo release policy and eight substantial Arrow chapters. Arrow topics include typed arrays, null versus NaN, schemas and RecordBatch, compute kernels, nested values, zero-copy slices, IPC, real CSV/JSON readers, decimals, timestamps and cross-language contracts. Bounded pipelines, diagnostics, stronger tests and an analytical capstone connect the mechanisms.

The prepared rust-stable profile compiles one main.rs with pinned Rust 1.99.1, edition 2024 and Arrow 60. The standard library and Arrow csv/ipc/json features are prepared in the image. Ordinary attempts do not run Cargo resolution, install packages, accept arbitrary command arguments or read interactive stdin. Reference programs remain deterministic and offline. Parquet, DataFusion, Tokio, PyArrow and additional FFI integrations are separate ecosystems requiring explicit project preparation.

Each chapter includes original mechanism teaching, vocabulary, syntax, two complete worked programs, six progressive tasks, diagnosed mistakes, an answer-free starter and separate executable/explanatory solutions. The lesson marker establishes the checked fixture ran, not independent mastery. The [InventoryLab](fixtures/InventoryLab/README.md) supplies an actual multi-file library, executable and integration-test project outside the single-source pad.

Contributors should read [AGENTS.md](AGENTS.md) and [authoring instructions](authoring/README.md). The maintained route is [track.json](track.json), and [lessons.json](lessons.json) admits complete bundles. Compile, runtime, browser, project and cross-platform evidence remain distinct. A finite course cannot promise expertise in every future library or production system.

See [validation scope](VALIDATION.md) for executed surfaces and deliberate external boundaries.
