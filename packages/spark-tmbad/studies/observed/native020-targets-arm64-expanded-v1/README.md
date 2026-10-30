# Expanded native 0.2 named-target observations

This is the separate local Linux ARM64 Spark stage for sim-003/004, seed 381729,
replications 0 through 15. It combines thirty new runtime shards with the two
unchanged original smoke shards. All 256 method fit records were accepted. Each
of the 16 target/scenario/method/reduction groups has 16 independent generated
datasets. Methods, reductions and the two studies intentionally reuse matched
datasets; they do not create 256 independent replications.

The files have distinct evidence roles:

| File | Role | SHA256 |
| --- | --- | --- |
| [AGGREGATE.json](AGGREGATE.json) | Unchanged observed aggregate of 32 actual shards | `56032af2e35fb0ec856518b4fd3ba2ef7ed4d4090f5e241f617d44466d72f08d` |
| [source-inventory.json](source-inventory.json) | Unchanged frozen source/fixture inventory | `f3b624c529936cc0b40118386266db9556044ee7c0bb3fdafb18e15a45a859fe` |
| [identity.json](identity.json) | Derived verification of raw receipt and dataset hashes; no refits | `1e86498f74c0e2b49e39fc5f016a6861f4991b20ff43d06754de89949ca8a06d` |
| [paired-risk.json](paired-risk.json) | Derived paired comparisons of actual squared errors; no refits | `659e19a021ce22d335eab427fa4acffa0285875fede7ff68a43ccce130e517a2` |
| [analytic-risk-reference.json](analytic-risk-reference.json) | Analytic repeated-sampling reference; not observed Monte Carlo or native output | `3fe291b29d7011e7eac73881d3a1292318886369d6d8ad6ce750eba439beb6f7` |
| [analytic-risk-crosscheck.json](analytic-risk-crosscheck.json) | Independent host quadrature check of the analytic reference; not native inference | `6aad35cc0674bc8ad905d88665145d4425badcd31de6842e71a429ad5663e074` |

Every raw canonical receipt hash was verified, all within-study/scenario training
and future datasets are distinct across replication indices, and the aggregate
was recomputed exactly. The bounded public files omit the full raw trace set,
which remains in the retained run evidence. No original smoke receipt was edited.

Read [the guide](../../guides/native020-study-expansion.md) for observed means,
MCSE, analytic contrasts, failure limits and setup. Sixteen datasets do not
establish nominal coverage, general estimator superiority, posterior inference,
hosted/cloud execution or distributed-scale performance.
