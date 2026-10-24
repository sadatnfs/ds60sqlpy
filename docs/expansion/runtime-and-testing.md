# Runtime preparation and acceptance

Status: implementation plan, not a claim that optional runtimes have been built. No heavy runtime is installed or downloaded by the design preview.

## Preparation before practice

The launcher should offer one explicit Prepare action per profile. It first checks the current engine and selected platform, CPU and memory allocation, host and engine-VM disk space, existing owned resources, required downloads, and a conservative unpack/build allowance. Show unknown measurements as unknown. The engine data disk may be full while the host still has space.

Use course-specific image and cache names, pinned dependencies, checksums, licenses, a software bill of materials, and repeatable build logs. Verify downloaded bytes before unpacking. A failed build or unhealthy engine stops new jobs and preserves progress. Do not automatically restart a VM, alter engine settings, remove unrelated resources, or run broad prune commands. Docker cache garbage collection is configurable and distinct from manually pruning all builder caches. [Docker cache garbage collection](https://docs.docker.com/build/cache/garbage-collection/)

Provisional worker budgets below guide a prototype only. Measure peak memory, scratch growth, image size, unpack space, and execution time on both target architectures before publishing installation requirements. Total engine allocation must also fit the app, PostgreSQL, cluster nodes where applicable, and reserve capacity. Initially allow only one heavy job at a time.

| Worker | Initial experiment envelope | Evidence needed before promising support |
| --- | --- | --- |
| C++ | 1 GiB RAM, 2 CPUs | Debug/release builds, sanitizer-specific limits, compiler cold start |
| TensorFlow CPU | 3 GiB RAM, 2 CPUs | Import, deterministic gradient, tiny fit/reload, actual wheel compatibility |
| Tiny LLM CPU | 3 GiB RAM, 2 CPUs | Masking checks, one training step, bounded generation, checkpoint reload |
| Spark local | 4 to 6 GiB RAM, 2 CPUs | JVM plus Python RSS, Scala compile, shuffle, Arrow, bounded streaming |
| kind cluster plus worker | Start by evaluating 3 GiB RAM, 2 CPUs | Real node/control-plane footprint, scheduling, image loading, recovery |

Do not use virtual-address limits that prevent sanitizer shadow-memory reservations and then interpret that failure as a learner bug. Record cgroup memory usage and actual worker exit/OOM reason. Docker stats reports container resource usage, with platform-specific interpretation, and is one input rather than proof of host capacity. [Docker stats reference](https://docs.docker.com/reference/cli/docker/container/stats/)

## OS and engine matrix

| Target | Beginner route | Acceptance required |
| --- | --- | --- |
| Windows 11 | Existing one-click launcher, WSL2-backed Linux-container engine | Fresh user install, reboot/resume, paths with spaces, PowerShell, browser launch, host persistence, profile preparation |
| macOS Apple Silicon | Existing launcher and local Linux arm64 engine | Native arm64 images, file ownership, VM disk preflight, browser, restart/resume |
| macOS Intel | Local Linux amd64 engine | Supported host OS and framework wheels inside the image; no claim based on Apple Silicon testing |
| Linux amd64/arm64 | Existing launcher and Docker-compatible engine | Permissions, browser-open fallback, UID/GID mapping, storage, both native architectures |

Test Docker Engine and at least one desktop engine before claiming portability. Rancher Desktop with a Docker-compatible endpoint is one row, not every engine. If an engine lacks the required API, network, or platform feature, explain it before building. Rootless engines and alternative Compose implementations need explicit rows. Windows and macOS host Python, JDK, TensorFlow, compiler, and PostgreSQL installations should not be prerequisites for the Docker route.

## Test layers

1. **Content:** Plan schema, source links, lesson IDs, DAG, all six exercises, worked examples, distinct outcomes, reference/solution separation, no unfinished material in the active catalog.
2. **Verifier:** Reference passes, misconception fails, edge cases, bounded failure, cancellation, source mapping, no success after truncated output or nonzero exit.
3. **Worker:** Clean build, offline start, fixture import, profile handshake, digest match, write limits, process cleanup, memory exhaustion, interrupted preparation and retry.
4. **Language semantics:** C++ ownership/UB cases; TensorFlow gradients and saved-model reload; causal masking/loss/generation; Scala/PySpark/SQL row-bag parity and streaming recovery; Kubernetes actual readiness and endpoint behavior.
5. **Browser:** Document rendering, keyboard and mobile navigation, teacher steps, useful diagnostics, hint/reveal boundaries, reload/resume, profile absent/blocked/running/failed states.
6. **Persistence:** Container replacement, app upgrade, backup/export/import, legacy progress migration, crash-safe writes, credentials excluded, no learner data in image layers.
7. **Platform:** Cold install and actual execution for every claimed OS/architecture/engine. CI definitions and configuration alone do not prove this layer.

Keep quick validation separate from runtime qualification. Run ordinary unit tests with the existing four-worker grouped pytest suite. Resource-heavy worker suites should declare their profile and resource group, and execute under a measured concurrency budget; launching four Spark JVMs simply because unit tests use four workers defeats the purpose. Use deterministic per-test workspaces, ports, namespaces, and cluster leases. Avoid serializing unrelated lightweight tests.

## Per-track acceptance examples

| Journey | Minimum vertical-slice proof |
| --- | --- |
| C++ | Compile correct and broken source, line diagnostics, CTest success/failure, timeout/reap, intended sanitizer negative fixture |
| TensorFlow | Exact one-step gradient fixture, tiny held-out experiment, correct tolerance, no network, saved model reload |
| LLM | Masked attention invariants, deliberate future-token leak rejected, tiny model step, bounded deterministic decode |
| Scala/Spark | Same explicit-schema fixture in both languages; nulls, duplicates, ordering; bounded shuffle and restart checkpoint test |
| Kubernetes | Owned cluster receipt, scoped RBAC rejection, rollout and HTTP probe, deliberate bad image diagnosis, cleanup/lease expiry |

## Qualification receipt

Publish a small machine-readable receipt containing source commit, course and verifier versions, actual OS/architecture, engine/version, profile image digest, dependency lock hash, fixture hashes, executed test names/results, offline mode, measured resource peaks, and remaining limitations. Sanitize logs and exclude secrets. A green compatibility badge must link to this receipt and expire or be requalified when its image, dependencies, or verifier changes.
