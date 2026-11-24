# Phase 8 Image Scan Ledger

Local evidence: `work/p8-scan/<profile>.json` and `work/p8-scan/reports/` (not committed).
Scanner: `scripts/image_scan.py scan` with `docker/cve-policy.json` (274 entries, all
pending-owner: 247 vulnerability, 27 misconfig; `validate-policy` passes).
Local host: macOS arm64 (Docker Desktop, linux/arm64 images). Scan date 2026-11-24.

"Fixable" means serious findings with a fixed version upstream; they always block and
are never placed in the policy. "Suppressed" counts unfixed findings covered by
reviewed pending-owner entries (expiring within 90 days) plus D-06 misconfig entries.

## Local results (linux/arm64)

| Image (profile) | Base | Passed | Fixable H/C | Unfixed H/C (suppressed) | Misconfig suppressed | Qualification |
|---|---|---|---|---|---|---|
| app | python:3.12.16-slim-trixie | yes | 0 | 60 | 27 | pip 26.3 verified after vendor prune |
| python-core | FROM app | yes | 0 | 60 | 0 | inherits app |
| python-web | python slim trixie | yes | 0 | 53 | 0 | pip removed |
| data-engineering | python slim trixie | yes | 0 | 53 | 0 | pip removed |
| postgres (DS60 derivative, reference) | postgres:17.12-trixie + gosu 1.20 / Go 1.26.11 | yes | 0 | 73 reported (1 Critical libxml2 CVE-2026-6653, no fix) | 0 | init, gosu drop, restart on existing volume |
| c17 | python slim trixie + gcc | yes | 0 | 73 | 0 | 42/42 |
| cpp20 | python slim trixie + g++ | yes | 0 | 87 | 0 | 41/41 |
| go | golang:1.27.4-trixie stage, python slim trixie | yes | 0 | 53 | 0 | 48/48 |
| rust-stable | rust:1.99.1-slim-trixie stage, python slim trixie | yes | 0 | 73 | 0 | 48/48 |
| php-cli | php:8.4.28-cli-trixie | yes | 0 | 112 | 0 | 26/26 |
| csharp-dotnet | mcr dotnet/sdk:10.0 | yes | 0 | 0 | 0 | 48/48 |
| java21 | temurin 21 stage, python slim trixie | yes | 0 | 53 | 0 | 36/36 |
| swift-linux | swift:6.3.3-noble | yes | 0 | 137 | 0 | 48/48 |
| r-statistics | rocker/r-ver:4.6.1, compilers purged | yes | 0 | 0 (no High/Critical at all) | 0 | 108/108, R references 270/270 |
| scala-jvm | spark:4.3.0 jars + overrides and re-shades | yes | 0 | 53 | 0 | 9/9 |
| spark-local-scala | same image | yes | 0 | 53 | 0 | 43/43 |
| spark-local-python | same image | yes | 0 | 53 | 0 | 47/47 |

Supporting checks on images built from the R worker: tmb-local (toolchain installed in
its own dependencies stage) compiled and passed `tests/acceptance.R`; `tests/public_api.R`
and `tmb-cpp-api/check.R` passed (R 4.6.1, TMB 1.9.25, Matrix 1.7.6).

### Spark blocker (Rule 4, resolved)

Before: fixable libraries shaded inside upstream jars blocked Spark 4.0.1: jetty 11.0.24
(spark-core), guava 33.4.0 (spark-network-common), jackson 2.18.1 (parquet-jackson), and
in hadoop-client-runtime 3.4.3: jackson 2.12.7, guava 33.4.8, jetty 9.4.57, jline 3.9.0,
commons-configuration2 2.10.1, kerby-asn1 2.0.3.

After: Spark 4.3.0 (`sha256:6f4beaaae1b084cad88493a894141d9f26a0a810f6c688519b036d34f1c2475e`)
with the `reshade_jars` operation. spark-core carries Jetty 12.1.15, spark-network-common
guava 33.8.0-jre, parquet-jackson is 1.18.2, and hadoop-client-runtime 3.5.0 carries
jackson 2.18.12, guava 33.7.2, jline 3.30.17, kerby 2.1.2 and commons-configuration2
2.15.1. Hadoop's shaded Jetty 9.4 is removed; a local-mode `-verbose:class` smoke run
loaded 0 of its classes while the Spark UI, Parquet and CSV paths worked. Scan on
2026-11-24: 0 blocking, 53 suppressed (C0 H53 M75 L79 U16) for all three profiles. Details
are in `08-04-SUMMARY.md` under Spark Resolution.

Not scanned locally (CI is the first scan after the 08-03 base moves): javascript-node,
typescript-node, tensorflow-cpu, llm-torch-cpu, dbt-duckdb, stan-cpu, julia, jax-cpu,
bayesian-cpu, data-platforms-python.

## CI proof (amd64 + arm64)

Workflow: `.github/workflows/targeted-images.yml`, push-triggered. Each pushed HEAD commit
must carry exactly one `[build-test-<group>]` marker; the job matrix then runs that group
on both amd64 and arm64 runners, and the seed job builds and scans app and python-core
plus the postgres reference. Nineteen groups means nineteen marker commits.

| Group (marker) | Profiles | Run id | amd64 | arm64 |
|---|---|---|---|---|
| `[build-test-python-core]` | python-core | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-python-web]` | python-web | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-cpp]` | cpp20 | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-java]` | java21 | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-php]` | php-cli | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-c-go]` | c17, go | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-csharp]` | csharp-dotnet | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-swift]` | swift-linux | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-javascript-typescript]` | javascript-node, typescript-node | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-scala-spark]` | scala-jvm, spark-local-scala, spark-local-python | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-tensorflow]` | tensorflow-cpu | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-pytorch]` | llm-torch-cpu | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-data-engineering]` | data-engineering, dbt-duckdb | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-stan]` | stan-cpu | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-julia]` | julia | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-jax]` | jax-cpu | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-bayesian]` | bayesian-cpu | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-r]` | r-statistics | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |
| `[build-test-data-platforms]` | data-platforms-python, rust-stable | `<RUN_ID_PENDING>` | `<PENDING>` | `<PENDING>` |

Artifacts to capture per run: `scan-reports-*` and `scan-evidence*.json` uploads, plus
`r-build-logs-*` for the r group.
