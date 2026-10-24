# InventoryLab: a complete Rust library and executable

This is the separate Cargo project for rust-023, rust-032, rust-036 and rust-048. It contains a public library, a small executable and four integration tests. The package has no third-party dependencies. It uses edition 2024 and a checked-in Cargo.lock.

Copy this directory to your own ignored learning workspace. In a prepared Rust environment, from the copied directory:

```bash
rustc --version
cargo build --locked --offline
cargo test --locked --offline
cargo run --locked --offline
```

Expect four integration tests and the executable output `apple=3;pear=6;rejected=1`. Cargo also reports library and executable test targets with zero unit tests; those are not additional behavioral tests. `cargo clean` removes the copied package's target output, not your source. Use only this owned project directory.

The library validates the simple two-field fixture, retains valid zero, aggregates repeated identities, rejects malformed or overflowing records, and renders a stable order. Its format is intentionally not a complete quoted CSV parser. The Arrow CSV chapter teaches the actual parser needed for that format.

The integration tests reject plausible defects: replacing errors with zero, losing duplicate aggregation, allowing overflow to overwrite a valid total and treating extra fields as accepted data. Add a structured rejection-reason result as an independent extension while keeping the current accounting contract visible.

The browser pad accepts one main.rs file and cannot receive this Cargo manifest or arbitrary dependencies. To make a separate Arrow application, prepare an explicit Arrow60 dependency and lockfile in your own project, review its feature selection and licenses, then verify `--locked --offline` after preparation. The classroom's immutable prepared Arrow artifacts are a different build contract. Parquet, DataFusion, Tokio, PyArrow and FFI features require their own deliberate dependency setup and actual execution evidence.
