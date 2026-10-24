# Rust curriculum ownership

Read root AGENTS.md, CONTRIBUTING.md and the add-learning-path skill. Own this subject's content, not shared runtime or CI code unless assigned. Preserve stable IDs, prerequisite relationships, saved-state namespaces and separate source/solution paths.

Durable source lives in authoring/foundations.py, composition.py and advanced.py. Edit that source before generated guides, learners or solutions, then run `python courses/rust/authoring/build.py`. Do not hand-edit generated HTML. Keep original teaching, two complete examples, six progressive tasks, explicit misconceptions and separate answer-free starters.

The runtime contract is rust-stable, main.rs, Rust1.99.1, edition2024 and the prepared Arrow60 csv/ipc/json dependency. Ordinary source has no Cargo manifest, arbitrary argv, interactive stdin or package installation channel. Arrow examples must use the real prepared APIs and valid null/schema/ownership semantics. Parquet, DataFusion, Tokio, PyArrow and optional FFI capabilities are not silently installed.

Use assert!/assert_eq! rather than debug_assert! for runtime reference invariants. Do not suppress a failed check or substitute expected output. Treat compilation, execution, browser delivery, external Cargo projects and cross-language interoperability as separate evidence. Keep all ordinary examples bounded, deterministic and offline after image preparation.

The InventoryLab fixture is directly authored and must retain complete build/test instructions. Cleanup only owned test resources, preserving learner volumes. Do not use em dashes, workplace details or private host paths in authored content.
