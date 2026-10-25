# Optional worker implementation checkpoint

> Support boundary: this file retains historical implementation evidence. The
> supported product runs in Linux Docker containers, with Windows through WSL 2.
> Native Windows ACLs/backends and native executable builds are not supported
> targets or release gates. Current checks are defined in [validation](../validation.md).

The current registry contains sixteen ordinary Linux worker profiles, including
C17, Go, C#, Rust, Swift and PHP, plus separate HTML/CSS/JavaScript/D3 browser runtimes,
optional NVIDIA profiles and an explicitly prepared Kubernetes adapter.
Inspect [validation](../validation.md), the current
workflow artifacts and the exact revision's runtime receipts for acceptance.
The browser preview records client observations and does not claim worker
verification. Swift Apple UI projects and advanced Docker/cluster host labs
retain their documented external capability boundaries.

The observations below describe historical implementation phases and their
then-current process and resource contracts. They are not current test totals,
proof for newly added profiles, or native Windows release requirements. The
maintained adapter source and current [checkpoint](CHECKPOINT.md) own the latest
limits and qualification status.

## Observed source acceptance

- 42 focused worker/UI tests passed in 10.77 seconds on the existing macOS arm64 host
  environment with `PYTHONPATH=src` explicitly selecting this repository.
- Strict MyPy passed for both modules and all three test files; Ruff passed.
- The actual inline module UI passed twenty-two deterministic Node behavior checks
  covering stale responses, draft revisions, one polling loop, startup recovery,
  exact-source diagnostics, independent curated Scala/PySpark variant saves,
  and explicit interrupted-job recovery confirmations without source replay.
  No application HTTP server was started for that harness.
- Real loopback submit/poll/cancel, malformed bodies/types, bounded terminal
  retention and a real HTTP-to-Python process path passed.
- Python exit/error propagation, bounded head/tail logs, short flushed log
  visibility, cancellation and descendant termination passed.
- Existing Apple Clang compiled and ran the C++ reference through all 14 typed
  verifier checks. Incomplete learner source failed; compile errors did not run
  an older artifact. These are native snippet checks, not a Linux image proof.
- The NumPy attention reference passed thirteen checks, including independent
  nonuniform/prefix/future fixtures. Four actual child-process mutation cases
  rejected ignored queries/keys, omitted scaling, wrong normalization axis and
  swapped queries/keys, independently of the learner reference verify() function.
- The TensorFlow oracle was checked using an independent mathematical function,
  without importing or installing TensorFlow on the host. Actual framework
  import and numeric execution also passed in the integration receipts below.

## Production worker boundary

Each service runs one operation at a time. Source is bounded to 256 KiB, logs to
128000 bytes, disposable files to 32 MiB / 1024 files, and the total deadline to 15,
60 or 120 seconds. Compile has its own maximum 60-second phase within that total.
Worker terminal history retains at most 32 snapshots. The service never accepts
shell commands, image references, host mounts or learner-supplied tool flags.

Production readiness requires a Linux container supervisor, an actual UID/GID
65534 privilege drop, inability of that child to read the private token, and the
ability of the supervisor to kill that different-UID child. The supervisor
requires CHOWN, SETUID, SETGID, DAC_OVERRIDE and KILL. Its private token is outside
portable `.learning`, inside image-owned root mode 0700 `/run/ds60`; expanded
Windows-sharing file modes are accepted only under that exact protected parent
and still need the child-read probe to fail as intended.

A fixed backend smoke then runs with a 45-second total startup bound. Health
returns the cached result and a stable-for-process random `instance_id`.
Worker ports are unexposed on an internal project network. No Docker socket,
repository, learner home, cloud credentials or external model endpoints are
mounted. This personal trusted-code environment is not a hostile multi-user
sandbox or a tamper-resistant examination service.

## Dependency resolution evidence

Metadata resolution selected 38 TensorFlow packages and 11 CPU PyTorch packages
for Python 3.12 Linux amd64/arm64. It installed no framework and downloaded no
model. The resolver fetched a 1.2 MiB setuptools metadata helper. Docker installs
use exact versions, `--require-hashes` and binary wheels only. TensorFlow uses
its common `tensorflow` package without a CUDA extra because the 2.20.0
`tensorflow_cpu` package lacks an ARM64 wheel.

The root integration agent found the engine mounts worker tmpfs noexec by
default. The overlay now explicitly enables exec for private `/tmp`, which is
necessary to run compiled C++ and may be needed for framework/JVM native code.
Root also observed apt CMake 3.25 in Bookworm; the C++ image now adds a separate
hash-locked CMake 3.28.4 environment to meet the authored project minimum.
No host tool was installed.

Actual image IDs, startup/UID/process tests, framework imports, Spark JVM jobs,
Windows host mount behavior, amd64 execution and Kubernetes lease qualification
must be recorded by the integration owner. No configuration-only claim fills
those evidence gaps. Kubernetes uses a separately injected lease-aware adapter;
the generic operation explicitly refuses cluster work without that adapter.

## Qualification-driven process-budget repair

The integration owner observed a Spark JVM exhausting the 128-task limit,
preventing a thread-per-request server from starting its HTTP control thread.
The worker now keeps health/poll/cancel on an existing synchronous control loop,
with the single job in the background. A regression forces all further thread
creation to fail while confirming health, polling and cancellation still work.
Child JVMs receive a fixed ActiveProcessorCount=2 and bounded GC worker counts.
Only the Spark services increase their task ceiling to 384; other profiles
retain 128. Actual JVM peak usage and successful runtime jobs remain in the
integration owner's image ledger.

The same pressure review reproduced a child-process leak when an output-reader
thread could not start after Popen. Reader setup now belongs to the complete
process cleanup try/finally; a real-child regression confirms termination and
wait. Job-controller thread admission failure also becomes an explicit failed
receipt instead of a permanently queued job. Unexpected infrastructure errors
make readiness false and do not claim cancellation cleanup was confirmed.

## Inspected integration receipts and remaining qualification

On 22 October 2026, read-only inspection of `work/modules-acceptance/*.json`
found Ready=true and actual positive/negative results for the following Linux
aarch64 workers. These are separate from the macOS source-test results above.

| Profile | Recorded execution evidence |
| --- | --- |
| `python-core` | Ordinary execution, thirteen attention checks, a negative learner and cancellation |
| `tensorflow-cpu` | Fifteen gradient-step checks, real TensorFlow execution and a negative learner |
| `cpp20` | Fourteen ownership checks, negative learner, compile failure and cancellation |
| `scala-jvm` | Compiled Main entry point and nonzero negative source |
| `spark-local-scala` | Six typed row/schema/NULL/transfer checks and a negative learner |
| `spark-local-python` | Same six logical checks through PySpark and a negative learner |

The integration owner refreshes image source layers and records the exact image
IDs and latest runtime results in those receipts. A passing result does not
qualify every code path or erase the regression repairs described above.
The later expansion qualified `llm-torch-cpu` using the complete executable
PyTorch route, LLM theory tensor references and applied fine-tuning examples.
Java, JavaScript and TypeScript also have actual compile/run/failure receipts.
The optional pretrained image separately completed pinned acquisition, full
fine-tuning, LoRA, repeatability checks and offline adapter reload. See the
current checkpoint and `work/pretrained-seeded-training-acceptance.json`.
The original NumPy attention foundation still needs only `python-core`.

Windows WSL 2/file-sharing behavior, Intel macOS host use, Linux amd64 execution,
arm64 hosts beyond this tested engine, rootless-engine mappings and emulation
performance remain separate unqualified rows. The existing Linux aarch64 proof
does not establish any of those rows. Kubernetes lease and cleanup execution
is recorded separately by the systems integration owner; generic workers still
refuse cluster operations without the dedicated adapter.
