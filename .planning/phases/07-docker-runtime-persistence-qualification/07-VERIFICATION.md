---
phase: 07-docker-runtime-persistence-qualification
status: passed
verified_at: 2026-11-24T13:07:59Z
sha: 6be2ffd438559c5cb59fb9defa74fdf016a3c5eb
run_id: 45390263162
---

# Phase 7 verification ledger

## Summary

- Qualified SHA: `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb`
- Runtime qualification run: [45390263162](https://github.com/sadatnfs/ds60sqlpy/actions/runs/45390263162), conclusion `success`
- Group reports: 38 image revision reports and 38 qualification reports
- Every value below is generated from the downloaded run artifacts in
  `work/p7-evidence/45390263162/` and the local report `work/p7-lifecycle-local.json`.
- The images carry the pre-release version label from this SHA. Release 2.0.0 changes
  version strings only and republishes through the Publish workflow, which re-runs the
  same qualification jobs before promotion.

## RUN-01 image revision table

| Architecture | Group | Profile | Image ID | Revision | Version | Source | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| amd64 | bayesian | app | `sha256:4519bfc9a0b5` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | bayesian | python-core | `sha256:62c4d4aa6a37` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | bayesian | bayesian-cpu | `sha256:2f8e2dca50ae` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | c-go | app | `sha256:9873915c4e91` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | c-go | python-core | `sha256:a599107bf449` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | c-go | c17 | `sha256:31f8bd1d9f06` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | c-go | go | `sha256:4b3169a9e706` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | cpp | app | `sha256:f6cca20b7b36` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | cpp | python-core | `sha256:62727cf8dda7` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | cpp | cpp20 | `sha256:86d033ca63e2` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | csharp | app | `sha256:ec905f5db6aa` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | csharp | python-core | `sha256:beaa173c4cfb` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | csharp | csharp-dotnet | `sha256:22f614471dc8` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | data-engineering | app | `sha256:4a4a559b27a2` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | data-engineering | python-core | `sha256:a7ddd6da1f48` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | data-engineering | data-engineering | `sha256:6442d37a9f43` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | data-engineering | dbt-duckdb | `sha256:b95c5f61381c` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | data-platforms | app | `sha256:5cd2cf950028` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | data-platforms | python-core | `sha256:4e532233b8c7` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | data-platforms | data-platforms-python | `sha256:41aac144d14d` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | data-platforms | rust-stable | `sha256:9a19ccdd6c79` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | java | app | `sha256:2e0c6e5a0ceb` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | java | python-core | `sha256:8e5ce2209c3a` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | java | java21 | `sha256:b9960f6cb757` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | javascript-typescript | app | `sha256:dada59be8f51` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | javascript-typescript | python-core | `sha256:1187ae7a4ed4` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | javascript-typescript | javascript-node | `sha256:dfa9d8d18c8f` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | javascript-typescript | typescript-node | `sha256:de2141406852` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | jax | app | `sha256:664410e226fe` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | jax | python-core | `sha256:2baa0163312e` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | jax | jax-cpu | `sha256:f4cf18748ea3` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | julia | app | `sha256:1cd4794fda03` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | julia | python-core | `sha256:8b75dba14af9` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | julia | julia | `sha256:4ce5c2cb9078` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | php | app | `sha256:fa961eac3443` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | php | python-core | `sha256:6cb2a283ae9a` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | php | php-cli | `sha256:3c6fbdcade9c` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | python-core | app | `sha256:cded70a6bd19` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | python-core | python-core | `sha256:f224f6629a55` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | python-web | app | `sha256:4bb9a283eeb0` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | python-web | python-core | `sha256:04fd75a83725` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | python-web | python-web | `sha256:563dec5000f7` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | pytorch | app | `sha256:273a72c9f98d` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | pytorch | python-core | `sha256:be4226bf6075` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | pytorch | llm-torch-cpu | `sha256:1b61772423a6` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | r | app | `sha256:377d34bf272b` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | r | python-core | `sha256:d113a19d2d08` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | r | r-statistics | `sha256:30ffdf08561b` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | scala-spark | app | `sha256:908354627441` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | scala-spark | python-core | `sha256:d1403bdb3a31` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | scala-spark | scala-jvm | `sha256:7e83482d8207` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | scala-spark | spark-local-scala | `sha256:9a3f3cd2518b` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | scala-spark | spark-local-python | `sha256:8a4b4f7941e3` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | stan | app | `sha256:5617f9279448` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | stan | python-core | `sha256:58002a8583e3` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | stan | stan-cpu | `sha256:c2977af9684c` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | swift | app | `sha256:9514f0bbea2a` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | swift | python-core | `sha256:9b7279e2efc5` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | swift | swift-linux | `sha256:b8740c997132` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | tensorflow | app | `sha256:feb2aa88a8ab` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | tensorflow | python-core | `sha256:88ac514cada6` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| amd64 | tensorflow | tensorflow-cpu | `sha256:546ff763678e` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | bayesian | app | `sha256:f25785bf4112` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | bayesian | python-core | `sha256:33e2aa2cab52` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | bayesian | bayesian-cpu | `sha256:b8ecc9fe39c6` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | c-go | app | `sha256:6b815465515b` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | c-go | python-core | `sha256:fefd191d8e30` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | c-go | c17 | `sha256:e3bd4a4bb15d` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | c-go | go | `sha256:815847ed0872` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | cpp | app | `sha256:83e95c758447` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | cpp | python-core | `sha256:dfc1075d5ac0` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | cpp | cpp20 | `sha256:adb4935db734` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | csharp | app | `sha256:e43053ccbfc0` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | csharp | python-core | `sha256:2308834a6dbe` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | csharp | csharp-dotnet | `sha256:368ae43fca97` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | data-engineering | app | `sha256:fea981f2e4d3` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | data-engineering | python-core | `sha256:a2dbe2726a3e` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | data-engineering | data-engineering | `sha256:41f1f54a6098` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | data-engineering | dbt-duckdb | `sha256:2f5e0037c1f7` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | data-platforms | app | `sha256:677122bb34ef` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | data-platforms | python-core | `sha256:d8a284a0a1a9` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | data-platforms | data-platforms-python | `sha256:c47c5ec6a0df` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | data-platforms | rust-stable | `sha256:771c28a62455` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | java | app | `sha256:94aba759ed3f` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | java | python-core | `sha256:291e7e9a4b1c` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | java | java21 | `sha256:3fd111d19323` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | javascript-typescript | app | `sha256:c474f04357a1` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | javascript-typescript | python-core | `sha256:2e49378df436` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | javascript-typescript | javascript-node | `sha256:35a4f767019b` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | javascript-typescript | typescript-node | `sha256:25caa9e75d89` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | jax | app | `sha256:fdd628d45112` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | jax | python-core | `sha256:6a13b42ffdff` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | jax | jax-cpu | `sha256:7c6b17d41d82` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | julia | app | `sha256:6505373915c4` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | julia | python-core | `sha256:0d1962366e8d` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | julia | julia | `sha256:8a1d06b32a97` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | php | app | `sha256:922bc9f6c93f` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | php | python-core | `sha256:7a0d97411188` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | php | php-cli | `sha256:379f1c6a04ca` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | python-core | app | `sha256:ae23b4534f0f` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | python-core | python-core | `sha256:cfec6f3e3d2e` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | python-web | app | `sha256:03dbc184ad26` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | python-web | python-core | `sha256:039a21220806` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | python-web | python-web | `sha256:c3a494d4169f` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | pytorch | app | `sha256:8cafcb8e481a` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | pytorch | python-core | `sha256:ed4518552ac8` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | pytorch | llm-torch-cpu | `sha256:62c329f1769f` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | r | app | `sha256:77a8bd388ed6` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | r | python-core | `sha256:edcec7b4012b` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | r | r-statistics | `sha256:c4deeb4384c3` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | scala-spark | app | `sha256:e77a7f677bd4` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | scala-spark | python-core | `sha256:1a8b32376d86` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | scala-spark | scala-jvm | `sha256:25b563b38b45` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | scala-spark | spark-local-scala | `sha256:09847fa72611` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | scala-spark | spark-local-python | `sha256:dce6b4fbc4b4` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | stan | app | `sha256:76d327267f50` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | stan | python-core | `sha256:711d9fb9f367` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | stan | stan-cpu | `sha256:9ac72219e6bf` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | swift | app | `sha256:02f59143ca15` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | swift | python-core | `sha256:e2f4128c21b3` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | swift | swift-linux | `sha256:7b4664fb210a` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | tensorflow | app | `sha256:bdc1c5ed5426` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | tensorflow | python-core | `sha256:e51b5f6574e1` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |
| arm64 | tensorflow | tensorflow-cpu | `sha256:b77240e9ca8b` | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | 1.4.3 | https://github.com/sadatnfs/ds60sqlpy | pass |

## Group qualification table

| Architecture | Group | Job conclusion | Checks | ci-qualification revision | Verdict |
| --- | --- | --- | --- | --- | --- |
| amd64 | bayesian | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | c-go | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | cpp | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | csharp | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | data-engineering | success | 11 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | data-platforms | success | 8 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | java | success | 8 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | javascript-typescript | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | jax | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | julia | success | 9 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | php | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | python-core | success | 19 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | python-web | success | 8 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | pytorch | success | 8 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | r | success | 9 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | scala-spark | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | stan | success | 9 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | swift | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| amd64 | tensorflow | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | bayesian | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | c-go | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | cpp | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | csharp | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | data-engineering | success | 11 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | data-platforms | success | 8 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | java | success | 8 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | javascript-typescript | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | jax | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | julia | success | 9 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | php | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | python-core | success | 19 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | python-web | success | 8 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | pytorch | success | 8 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | r | success | 9 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | scala-spark | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | stan | success | 9 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | swift | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |
| arm64 | tensorflow | success | 7 | `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb` | pass |

## Lifecycle tables

Columns come from the harness checks: Container IDs shows whether every service container
was kept, intentionally recreated or stopped; Progress files compares the learner
`progress.json` and `coaching.json` digests across the transition; the persistence probe
re-reads the saved Python pad, its lesson evidence, the original run receipt and the
learner-created SQL sentinel table.

### Local arm64 (Docker Desktop on macOS)

Project `ds60-p7-local4-46dc32fc`, mode `seeded`, base `2f9521b20dcd57938193d34036de2783ee619048`, target `46dc32fc41badbe5128ceeb145740b5bcdc32f89`, profiles starter. Report passed: True. Skipped steps: update. Protected errors: 0. Residue: containers False, networks False, volumes False. Cleanup down exit 0, worktree removed True.

| Step | Exit | Seconds | Container IDs | Volumes retained | Progress files | Persistence probe (draft, receipt, SQL sentinel) | Token digest | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fresh | 0 | 29.0 | created 4 | pass | pass | pass | pass | passed |
| stop | 0 | 1.0 | stopped: pass | pass | n/a | n/a | n/a | passed |
| resume | 0 | 23.0 | kept 2: pass | pass | pass | pass | pass | passed |
| rerun | 0 | 6.3 | kept 3: pass | pass | pass | pass | pass | passed |
| restart | 0 | 23.8 | kept 2: pass | pass | pass | pass | pass | passed |
| recreate | 0 | 24.1 | recreated: pass | pass | pass | pass | pass | passed |
| update | n/a | 0.0 | n/a | n/a | n/a | n/a | n/a | skipped |
| final-rerun | 0 | 6.2 | kept 3: pass | pass | pass | pass | pass | passed |

Local deviation: this Mac can only reach Python packages through the Microsoft package proxy, which did not yet carry the locked `certifi==2026.11.20` when this ledger was generated, so a local build-mode run stops at the lab image build (report kept in `work/p7-lifecycle-local-build-proxy-fail.json`). The local run therefore seeds the published 1.4.3 lab and python-core images and records `update` as skipped. The update step (rebuild from base to target, image ID change, revision label and persistence probe) is proven by both CI lifecycle runs below, which must pass all eight steps.

Local target note: the local run targets `46dc32fc41badbe5128ceeb145740b5bcdc32f89`, one commit
before the qualified SHA. That commit (`6be2ffd4`) changes the PyTorch worker locks and requirement
pin, the CVE policy, a CI classroom mirror passthrough, PyTorch course prose and tests, and Prettier
layout of two JSON locks. None of it touches the lab, python-core or postgres services the local
lifecycle exercises, and both CI lifecycle runs below qualify the exact SHA.

### CI amd64 (ubuntu-24.04)

Project `ds60-p7-amd64-45390263162-1`, mode `build`, base `46dc32fc41badbe5128ceeb145740b5bcdc32f89`, target `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb`, profiles starter. Report passed: True. Skipped steps: none. Protected errors: 0. Residue: containers False, networks False, volumes False. Cleanup down exit 0, worktree removed True.

| Step | Exit | Seconds | Container IDs | Volumes retained | Progress files | Persistence probe (draft, receipt, SQL sentinel) | Token digest | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fresh | 0 | 129.9 | created 4 | pass | pass | pass | pass | passed |
| stop | 0 | 2.8 | stopped: pass | pass | n/a | n/a | n/a | passed |
| resume | 0 | 46.4 | kept 2: pass | pass | pass | pass | pass | passed |
| rerun | 0 | 17.5 | kept 3: pass | pass | pass | pass | pass | passed |
| restart | 0 | 49.0 | kept 2: pass | pass | pass | pass | pass | passed |
| recreate | 0 | 45.7 | recreated: pass | pass | pass | pass | pass | passed |
| update | 0 | 77.8 | rebuilt images, revision label: pass | pass | pass | pass | pass | passed |
| final-rerun | 0 | 17.8 | kept 3: pass | pass | pass | pass | pass | passed |

### CI arm64 (ubuntu-24.04-arm)

Project `ds60-p7-arm64-45390263162-1`, mode `build`, base `46dc32fc41badbe5128ceeb145740b5bcdc32f89`, target `6be2ffd438559c5cb59fb9defa74fdf016a3c5eb`, profiles starter. Report passed: True. Skipped steps: none. Protected errors: 0. Residue: containers False, networks False, volumes False. Cleanup down exit 0, worktree removed True.

| Step | Exit | Seconds | Container IDs | Volumes retained | Progress files | Persistence probe (draft, receipt, SQL sentinel) | Token digest | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fresh | 0 | 166.1 | created 4 | pass | pass | pass | pass | passed |
| stop | 0 | 4.0 | stopped: pass | pass | n/a | n/a | n/a | passed |
| resume | 0 | 54.8 | kept 2: pass | pass | pass | pass | pass | passed |
| rerun | 0 | 24.4 | kept 3: pass | pass | pass | pass | pass | passed |
| restart | 0 | 61.3 | kept 2: pass | pass | pass | pass | pass | passed |
| recreate | 0 | 55.0 | recreated: pass | pass | pass | pass | pass | passed |
| update | 0 | 102.8 | rebuilt images, revision label: pass | pass | pass | pass | pass | passed |
| final-rerun | 0 | 24.4 | kept 3: pass | pass | pass | pass | pass | passed |

## Protected resources

The local run recorded every container, image and volume outside its own `ds60-p7-` project
before and after the lifecycle. CI runs use fresh hosted runners with `ds60-p7-` and `ds60-ci-`
projects only. No Compose project outside `ds60-p7-` and `ds60-ci-` was touched.

- Containers before 15, after 15; identical IDs and states: True.
- Images before 2, after 2; identical: True.
- Volumes before 3, after 3; identical: True.
- Harness protected errors: 0; warnings: 0.

## Exclusions

- GPU profiles: hosted runners have no GPU and the release excludes them at
  `scripts/docker_release.py:175`.
- Kubernetes images: they use a separate owned-cluster workflow.
- Docker daemon restarts: they cannot be exercised on hosted runners and would disrupt the
  user's other containers locally.

## Verdicts

- RUN-01: PASS
- RUN-02: PASS
