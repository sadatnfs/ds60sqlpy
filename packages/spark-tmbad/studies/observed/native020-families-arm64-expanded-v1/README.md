# Independently derived family-study expansion

This bounded summary was independently derived from forty unchanged observed
local Linux ARM64 Spark 4.0.1 local[2] shards: the five initial replication-zero
shards plus thirty-five new shards at replications 1 through 7. It uses the frozen
aggregate_extended.py/study_support.py implementations and is not a new model
run. Each study/scenario has eight distinct training and future datasets.

There are 22 target/scenario/method groups and 176 method records: 172 accepted and
four failed. All 64 individual normal-group fits passed. The four failed records
retain their original optimizer statuses and have no fitted predictions or future
metrics. No tolerance was changed and no failure was retuned or reclassified.

The observations remain bound to JVM SHA256
`4bc78a3be973d8e3e62eea12df2bf1e2410299b7bf39144b2f75257958814b8c`.
They do not qualify a later proximal implementation or migrate saved models to a
different artifact. Root's separately reserved AGGREGATE.json was not written by
this derivation. The earlier raw receipts remain unchanged.

| File | Role | SHA256 |
| --- | --- | --- |
| [aggregate-derived.json](aggregate-derived.json) | Independent aggregation of actual unchanged shards | `8b703f6bde9a4e708069b31afa78c88e0d47a2e6f19a829a0144a45b3f3ab9fa` |
| [identity.json](identity.json) | Derived source/artifact/raw-receipt and dataset-hash verification | `4aed5d68d196ab3d1c0a5308004cb3b0ff37c9bf3c04c3f3f7b2fb431d48b985` |
| [failed-methods.json](failed-methods.json) | Derived ledger preserving the four actual failed methods | `c7f4836c9e0f361064d00161433c1904edeedac904fcf9756ed31cd9454cc55b` |
| [source-inventory.json](source-inventory.json) | Unchanged frozen source and selected-fixture inventory | `f3b624c529936cc0b40118386266db9556044ee7c0bb3fdafb18e15a45a859fe` |

See [the worked guide](../../guides/native020-study-expansion.md) for exact
denominators, observed MCSE, normalized scores, conditional versus procedural
coverage and remaining limits. The full raw traces are retained separately;
the public summary does not duplicate them. Eight datasets do not establish
general calibration, estimator superiority, posterior, hosted or cloud acceptance.
