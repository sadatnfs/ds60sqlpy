# Observed native 0.2 named-target studies

These files are unchanged execution receipts for sim-003 and sim-004, replication
zero, seed 381729, on Linux ARM64 with Spark 4.0.1 local[2]. Both scenarios, both
methods and both reductions passed, for sixteen fitted records. This is one
independent generated dataset per scenario. It does not establish repeated-data
calibration, a posterior sampler, distributed-worker or cloud acceptance.

- [sim-003-r0.json](sim-003-r0.json): SHA256 `b869a1c99a4697267ff0b4ec1b8546e47735c0c6a1e02154c8b6ae2b7b287241`.
- [sim-004-r0.json](sim-004-r0.json): SHA256 `bc66a3e4109fbb40ad3f61f30c8836a596bc6b049e487df429e25b7135cd4145`.
- [source-inventory.json](source-inventory.json): SHA256 `ce33f464f451fc97c1ba8f644f9f45cd9ddb6df61bbfd9e7f3a178253cb269a3`.

The receipts preserve exact source, fixture, package, native and JVM identities.
Read [the worked guide](../../guides/native020-study-expansion.md) for the likelihood,
prior constants, KKT rules, commands and interpretation. A changed source or
artifact needs a new receipt; do not relabel these observations.
