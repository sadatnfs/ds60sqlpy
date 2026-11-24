---
phase: 08-release-image-security
plan: 04
subsystem: release-image-security
status: partial
requirements: [SEC-01]
tags: [trivy, cve, trixie, digest-pin, postgres, spark, r, policy]
requires: [08-01, 08-02, 08-03]
provides:
  - C and C++ workers on the digest-pinned python 3.12.16 slim trixie base with only the toolchain packages
  - Go, Rust, PHP, Swift, .NET and Java workers refreshed to digest-pinned bases with 0 fixable findings
  - R worker on digest-pinned rocker/r-ver 4.6.1 with build compilers purged (0 High/Critical)
  - DS60-owned postgres image (docker/postgres/Dockerfile) built locally by the launcher
  - pip 26.3 vendored pkg_resources pruned in the app image (python-core inherits it)
  - universal digest-pin contract test
  - docker/cve-policy.json finalized locally (274 pending-owner entries)
  - 08-SCAN-LEDGER.md with local results and CI placeholders
affects: [08-05]
tech-stack:
  added: []
  patterns:
    - compiled toolchains copied from pinned stages onto one slim trixie runtime
    - compilers purged after source builds when lessons do not compile
    - shaded jar overrides with a manifest checked against Spark RELEASE
key-files:
  created:
    - docker/workers/spark/apply_jar_overrides.py
    - docker/workers/spark/jar-overrides.json
    - .planning/phases/08-release-image-security/08-SCAN-LEDGER.md
  modified:
    - docker/workers/Dockerfile.{c,cpp,go,rust,php,swift,csharp,java,r,spark}
    - docker/workers/r/packages.lock.json
    - docker/workers/r/README.md
    - courses/tmb-modeling/projects/tmb-local/Dockerfile
    - compose.modules.yaml
    - docker/registry-mirrors.env.txt
    - docker/cve-policy.json
    - scripts/classroom.sh
    - .github/workflows/publish-images.yml
    - tests/test_docker_classroom.py
    - tests/test_image_scan.py
    - tests/test_classroom_launchers.py
    - tests/test_image_revision.py
decisions:
  - Postgres is a DS60-built derivative tagged ds60sqlpy-postgres:<release version>; the launcher builds it locally in every mode and pulls only when DS60_POSTGRES_IMAGE is overridden. It is not published to Docker Hub yet.
  - The R worker moves to rocker/r-ver (Ubuntu, source-built R) instead of Debian r-base; Matrix 1.7-6 is added to the lock to keep the qualified version.
  - R compilers are purged after package builds; the TMB project image installs its own toolchain.
  - The 27 app misconfigurations stay as reviewed D-06 policy entries instead of a scanner skip-dir, so new learner Dockerfiles are still scanned.
  - Spark shaded jar findings are not accepted in policy. Spark moved to 4.3.0 and its shaded libraries are re-shaded from pinned Maven Central jars, so the Spark images pass with 0 fixable findings.
  - Hadoop's shaded Jetty 9.4 is removed from hadoop-client-runtime because no fixed 9.4 release exists and local mode never loads it.
metrics:
  completed: 2026-11-24
actuals:
  tasks: 3
  commits: 0
---

# Phase 8 Plan 04: Worker Image Remediation Summary

C, C++, Go, Rust, PHP, Swift, .NET, Java, R, app, python-core, python-web,
data-engineering, the new DS60 postgres image and the Spark worker all scan locally
with 0 fixable findings, and each one passes its qualification. The Spark worker now
runs Spark 4.3.0 with re-shaded patched libraries (see Spark Resolution).

Status is **partial**. Everything is uncommitted by instruction (the orchestrator commits),
so `commits: 0` is expected. The CI proof is pending. The Spark fix landed separately in
`fix(08): Spark 4.3.0 with re-shaded patched libraries`.

## Results

Per-image counts and the CI marker table are in `08-SCAN-LEDGER.md`. In summary:

- **0 fixable findings, passed:** app, python-core, python-web, data-engineering,
  postgres (reference), c17, cpp20, go, rust-stable, php-cli, csharp-dotnet, java21,
  swift-linux, r-statistics, scala-jvm, spark-local-scala, spark-local-python.
- **Spark:** the earlier 50 fixable findings (shaded jetty, guava, jackson, jline,
  commons-configuration2 and kerby) are gone. The Spark image now reports 0 blocking,
  53 suppressed unfixed findings (C0 H53 M75 L79 U16).

### Qualification

| Check | Result |
|---|---|
| c17 | 42/42 |
| cpp20 | 41/41 |
| go | 48/48 |
| rust | 48/48 |
| php | 26/26 |
| csharp | 48/48 |
| java21 | 36/36 |
| swift | 48/48 |
| r-statistics | 108/108 |
| R references | 270/270 |
| scala-jvm | 9/9 |
| spark-local-scala | 43/43 |
| spark-local-python | 47/47 |

Other checks:

- **tmb-local:** compile.R and acceptance.R passed, as did public_api.R and tmb-cpp-api/check.R.
- **postgres:** init, the gosu 1.20 privilege drop, and a restart on an existing volume all worked.
- **pip 26.3 in the app image:** version, list, show, freeze, check and debug work, and a
  real offline install and uninstall in a scratch venv works.

## 08-03 Owner Items Closed

1. **Postgres:** the derivative from 08-03 is finished.
   - The `scripts/classroom.sh` database build now runs before the service builds and
     receives the release and revision build args in every mode.
   - Pulling happens only when `DS60_POSTGRES_IMAGE` is overridden.
   - The tag follows the release version.
   - Launcher tests cover the build, the override pull, and the Hub mode rule that only
     postgres builds locally.
2. **pip vendored setuptools:** the prune is verified inside a built image.
   - python-core is FROM app, so it inherits the prune.
   - python-web and data-engineering uninstall pip entirely.
3. **App misconfigurations:** the 08-03 learner Dockerfiles now end non-root.
   - The remaining 27 DS-0002 entries are reviewed misconfig entries (D-06).
   - I added one entry for the course's postgres example, because the official
     entrypoint starts as root and then drops privileges with gosu.
4. **Spark:** jar overrides removed every Critical finding. The remaining shaded findings
   were fixed by the Spark 4.3.0 move and re-shading (see Spark Resolution).

## Deviations from Plan

1. **[Rule 3] C and C++ base:** these workers use the shared `python:3.12.16-slim-trixie`
   digest with gcc/g++ from apt, instead of a separate slim trixie image. That gives one
   maintained base, and the compose build-arg defaults equal the Dockerfile ARG defaults.
   The cmake pip locks were removed.
2. **[Rule 1] R base (D-09):** rocker/r-ver 4.6.1 is pinned by digest. On rocker, the
   bundled recommended Matrix 1.7-5 broke the tmb-local base check, so Matrix 1.7-6 is now
   the first package in the lock (SHA-256 verified from CRAN).
3. **[Rule 2] R compilers purged:** this brought R from many unfixed linux-libc-dev
   findings to 0 High/Critical, with no policy entries needed. Learners can no longer
   install source packages inside the R worker. Lessons and references do not need that.
4. **[Rule 3] tmb-local toolchain:** tmb-local now installs gcc, g++, gfortran, make and
   libc6-dev in its dependencies stage, because it compiles TMB models.
5. **[Rule 2] openssl vignette removed:** `site-library/openssl/doc` is removed from the R
   image because it contains sample private keys that the secret scan flags.
6. **[Rule 1] publish-images scan uploads:** the upload paths are now
   `work/scan-reports/*.json`, matching the small-JSON-artifact contract that
   `test_image_publication` enforces.
7. **[Rule 1] test_image_revision:** the test now expects the third build row, for the
   locally built postgres image.
8. **[Rule 1] test_image_scan:** the starter-policy test now accepts misconfig entries,
   provided they have a DS-* id and a file path.

## Policy

`docker/cve-policy.json` has 274 entries: 247 vulnerability and 27 misconfig.

- All entries are pending-owner and cover unfixed findings only. `validate-policy` passes.
- This plan added 187 entries and extended 560 others with additional image or target
  coverage, including the Spark unfixed Ubuntu findings.
- Worker entries were reviewed on 2026-11-24 and expire on 2026-12-24.
- The app misconfig entries expire on 2027-02-21.
- The merge tool refused every fixable finding.

## Validation

- ruff check and ruff format --check: clean. Scope was src, scripts, tests, bridge,
  python/professional, docker/init_module_runtime.py, docker/prune_pip_vendor.py and
  docker/workers/spark/apply_jar_overrides.py.
- pytest on the 34 docker, image, compose, workflow, publish, release, launcher, TMB,
  spark-deployment and parity test files: 1070 passed and 1 skipped. The skip needs a
  prepared Spark/TMB environment.
- actionlint with shellcheck: clean.
- `scripts/lint-repo --language docker`: passed (49 files).
- Dash scan of all changed and created files: clean.
- Cleanup: all `ds60-p8-scan/*` images and the base digests I pulled were removed. No
  `ds60-p8-scan-*` containers or volumes remain. Protected resources were not touched.

## Spark Resolution

The earlier Spark blocker (Rule 4) is resolved. Spark 4.0.x and 4.1.x shade Jetty 11, which
is end of life; CVE-2024-6763 and CVE-2025-11143 are fixed only in Jetty 12. Spark 4.3.0
already uses Jetty 12.1, so the worker moved to
`spark:4.3.0-scala2.13-java17-python3-ubuntu@sha256:6f4beaaae1b084cad88493a894141d9f26a0a810f6c688519b036d34f1c2475e`
(Scala 2.13.18, Hadoop 3.5.0).

Approach:

- `apply_jar_overrides.py` gained a `reshade_jars` operation backed by
  `docker/workers/spark/jar_reshade.py`, a standard-library relocator. It downloads each
  source jar from Maven Central, pinned by SHA-256 and failing closed on a mismatch. It
  removes the old shaded packages, relocates the new classes into the original prefix
  (class constants, descriptors, string constants, resource paths and `META-INF/services`),
  and replaces the old `META-INF/maven/<group>/<artifact>` metadata with the new library's
  real `pom.properties` and `pom.xml`, so the scanner sees the true version. No metadata is
  removed while vulnerable classes stay.
- Standalone jar swaps: guava 33.8.0-jre, jackson 2.21.8, jline 3.30.17, log4j 2.25.5,
  lz4-java 1.11.4, snappy-java 1.1.10.12, netty 4.2.21.Final, parquet-jackson 1.18.2.
- spark-core: shaded Jetty 12.1.8 replaced by Jetty 12.1.15 under `org/sparkproject/jetty`.
- spark-network-common: shaded guava replaced by 33.8.0-jre plus failureaccess 1.0.3 under
  `org/sparkproject/guava`.
- hadoop-client-runtime 3.5.0: shaded jackson 2.18.12, kerby 2.1.2, commons-configuration2
  2.15.1, jline 3.30.17 and guava 33.7.2 under `org/apache/hadoop/shaded`.
- hadoop-client-runtime shaded Jetty 9.4 is removed: 753 entries under
  `org/apache/hadoop/shaded/org/eclipse/jetty/`, its 6 service registrations and its Maven
  metadata. Jetty 9.4 is end of life and 9.4.58 still carries the findings.

Why removing Hadoop's Jetty is safe: statically, only Hadoop daemon classes (HttpServer2,
the YARN and HDFS web servers) refer to it. At runtime, a local-mode smoke run with
`-verbose:class` read and wrote Parquet and CSV through LocalFileSystem and served the
Spark UI (`/jobs/`, `/SQL/` and `/api/v1/applications` all returned 200). Of 25595 loaded
classes, 0 came from `org.apache.hadoop.shaded.org.eclipse.jetty`; 698 came from the
relocated Jetty 12.1.15. All three qualifications below passed on the same image.

Bug found and fixed on the way: the first re-shade dropped zip directory entries, and the
Spark UI then failed with "Could not find resource path for Web UI". The relocator now keeps
directory entries and synthesizes missing parents; a test covers it.

Results on `linux/arm64`: scala-jvm, spark-local-scala and spark-local-python all report 0
blocking (53 suppressed). Qualification: scala-jvm 9/9, spark-local-scala 43/43,
spark-local-python 47/47.

Deferred on Spark 4.0.1: `packages/spark-likelihood` and `packages/spark-tmbad` (their own
wrapper preparation and native builds are qualified against 4.0.1 by their own workflows),
the advanced-spark-modeling spark-tmb and spark-torch projects, and the spark-deployment
track with its learner-built cluster lab. None of these is a classroom profile image.

## Follow-ups

- Publish the postgres image to Docker Hub. This needs docker_release SEEDS, staging and
  promotion. Until then, Hub mode builds the database image locally.
- Ten profiles have not been scanned locally and will first be scanned in CI. They are
  listed in the ledger.

## CI Proof Needed

Push the commit, then push one commit per group carrying exactly one
`[build-test-<group>]` marker for each of the 19 groups listed in the ledger.
`targeted-images.yml` runs each group on amd64 and arm64. Record the run ids, and keep the
`scan-reports-*`, `scan-evidence*.json` and `r-build-logs-*` artifacts in the ledger.
scala-spark is expected to pass now that Spark runs 4.3.0 with re-shaded libraries.

## Self-Check: PASSED

The ledger, this summary, the policy file, the Spark override files and the R lock all
exist. No commits were expected.
