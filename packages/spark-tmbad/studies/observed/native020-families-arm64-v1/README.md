# Observed native 0.2 family, panel and independent-fit smoke

These unchanged local Linux ARM64 Spark 4.0.1 local[2] receipts cover five study
shards at replication zero, seed 381729. They contain 22 method records: 21
accepted and one beta-binomial line-search failure on binomial truth. That failed
record has no fitted prediction result. Completion does not mean every fit passed.

The independent-group records include four separate group fits each, all of
which passed in these two scenarios. Method-record counts and individual group-fit
counts are distinct. Every scenario has one generated replication, so conditional
scalar MCSE remains null. No broad calibration, posterior, distributed-worker or
cloud qualification follows.

| Receipt | SHA256 |
| --- | --- |
| [sim-009-r0.json](sim-009-r0.json) | `c39f8f8abdbb64ba75c1546aa0b1b6d3eac94ee7687ce874507e8638c148b9a0` |
| [sim-020-r0.json](sim-020-r0.json) | `35acd8f903c17a4a26e1392d16d9040407d988c0c1fd447191f892204c69e210` |
| [sim-022-r0.json](sim-022-r0.json) | `775aafcb78fc72d34997b423a4230135979f0c120038773bab82ef5a1c8dc3e9` |
| [sim-024-r0.json](sim-024-r0.json) | `a1ca420587ed2b08a63d84d2959be7a308228806e954787e476e9fb051eebc77` |
| [sim-028-r0.json](sim-028-r0.json) | `5c3bd172e2665f408ad82b31f02ed10ddc7f51c85b45b04f9d58ac4d94dbac3a` |
| [source-inventory.json](source-inventory.json) | `14d35de67e65cef065fcb66b280ad740741f234296f85b02b2341bcfe46cb462` |

The source inventory and receipts bind exact fixture, package, native and JVM
identities. See [the worked guide](../../guides/native020-study-expansion.md)
for normalized scores, failure interpretation and remaining study contrasts.
Do not overwrite these observations after changing a source, criterion or input.
