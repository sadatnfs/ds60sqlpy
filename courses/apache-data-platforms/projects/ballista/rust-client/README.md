# Native Rust extension boundary

This separate project shows the selected Ballista54.1.0 Rust client API. It is
not prepared in the ordinary Arrow-only Rust classroom pad. Source presence does
not establish dependency resolution, successful compilation or a remote query
receipt. The parent project's qualification ledger reports those gates explicitly.

Prepare an isolated Cargo environment, generate and review Cargo.lock, then compile
with that lock in Docker. This can require substantial disk and build time; do not
start it implicitly while opening a chapter. The client needs the same private
network and read-only `/state/orders.parquet` source as the Python workshop. Never
mount the Docker socket to provide network access. Before treating this as an
admitted native route, compare exact returned group values, source identity and a
negative case with the prepared Python oracle, not just the two-row assertion.

The existing Python route uses actual native Rust scheduler and executor code
and has a smaller preparation path. A new Rust-client runtime is a separate
extension, with compatible crate/codec versions and its own validation.
