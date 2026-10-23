# C++20 track design

Status: planned, checked 2026-10-22. This document proposes a track. It does not register lessons, install a compiler, enable a runner, build an image or change the working Learning Lab. The existing `cpp` descriptor remains save/view only until an adapter passes its implementation gates.

## Outcome and learner entry

A learner starts with no programming experience and finishes able to deliver a tested C++20 program, explain its ownership and error boundaries, and defend measured concurrency/performance decisions. There are no required Python or SQL catalog prerequisites. Terminal/file vocabulary and the compile/link/run distinction are taught first. Existing `python-foundations-01`, `python-10` and `python-perf-01` are optional transfer/review material, not planner gates.

The plan contains 42 lessons because it separates 39 teachable mechanisms and three substantial integration reviews. Fourteen beginner units establish a complete small-program workflow; fourteen intermediate units develop reusable libraries and diagnostic discipline; fourteen advanced units develop bounded concurrent systems and defensible measurement. A compile error, a memory-lifetime error and an invalid benchmark require different teaching, so they are not compressed into one tool demonstration. The canonical per-lesson outcome, lab, independent verification, prerequisites and timing live in [the planned JSON](../plans/cpp.json). Timings describe focused study, not a deadline for mastery; capstones span several sessions.

## Teaching structure

The beginner route builds visible success before abstraction: files and toolchain evidence, a first target, values/control flow/functions, trustworthy parsing, owning sequences, references/lifetimes, records/files, translation units and CTest. The [pilot `cpp-009`](../samples/cpp-pilot.md) is a complete lesson preview, with a separate [explanatory solution](../samples/cpp-pilot-solutions.md). Learners predict a state change, run two small worked examples, complete six progressively different tasks, check explicit outcomes, then retrieve the ownership argument without the solution.

Intermediate work moves from resource acquisition and the rule of zero to errors, views, generic interfaces, serialization, ABI boundaries, property/corpus tests, diagnostic builds and dependency delivery. Advanced work gives concurrency its own sequence: lifetime/joining, predicates, memory ordering, backpressure, deterministic testing and race diagnostics. Layout, algorithmic growth, compile-time work, numerical stability, hardening and release evidence remain separate concerns. Modules, coroutines and C++23/26 library features are optional future electives, not hidden requirements of this C++20 baseline.

## Runtime contract before implementation

`reading` and `cpp20` are planned runtime IDs, not current executable capabilities. The canonical future `cpp20` profile is a pinned Linux amd64/arm64 compiler worker with GCC 14 or newer, matching libstdc++, CMake 3.28 or newer, Ninja, CTest and offline diagnostic tools. These are qualification targets, not tested installation claims. Record the exact compiler, standard library, target triple and image/tool hashes after proving the profile. A compiler version or `-std=c++20` flag alone does not prove every library feature; compile probes must cover the track's required `span`, ranges and `jthread` subset. `jthread` lessons require an affirmative library probe, with a clearly labeled joining-thread alternative for an incomplete native library. The [Clang implementation table](https://clang.llvm.org/cxx_status.html) motivates this explicit qualification.

Compilation and execution are separate jobs. A successful compile produces an artifact hash plus diagnostics; it does not run that artifact or complete a lesson. Run uses that exact successful artifact and records its source/build hashes. A failed or canceled compile must invalidate the current runnable artifact instead of silently executing yesterday's binary. Run cannot accept an arbitrary executable path or compiler flag string. Compiler plugins, response files, arbitrary output paths and environment-driven tool replacement are outside the initial adapter.

The host provisioner creates the worker. Browser code never receives a Docker socket or host compiler control. Source is copied into an owned job directory; the worker gets no home directory, credentials, repository parent or network access. Build outputs and saved text are bounded and returned only through reviewed paths. User-authored CMake can execute processes, so configure/generate must be isolated and bounded too. Initial lessons use immutable instructor CMake templates; advanced edited build scripts run only inside the same isolated worker. This is defense in depth for a personal trusted-code learning environment, not a claim of safe arbitrary hostile multi-user execution.

Provisional normal-job budgets are 60 seconds for configure/compile and 10 seconds for an ordinary run; advanced profiles may explicitly offer 120/30 seconds after proof. CTest applies a per-test timeout as well. A timeout, output cap, compiler crash or cancellation must terminate descendants, retain the learner's sources and diagnostics, and leave no running worker. CPU, memory, process-count, input/file-count and artifact-size limits require measurement before publication; there is no performance claim from these proposed numbers. The feature menu must distinguish unavailable compiler, unsupported library feature, compile failure, missing diagnostic tool and execution failure.

## Cross-platform qualification matrix

| Learner host | Proposed default | Optional native path | Evidence still required |
| --- | --- | --- | --- |
| Windows 11 x64 | WSL 2/Linux containers, native Linux amd64 worker | MSVC 19.40+ in a Developer PowerShell with CMake/Ninja or its matching generator | Paths containing spaces, UTF-8 diagnostics, job-tree cancellation, Debug/Release and compiler/library feature probes |
| Windows ARM | No blanket compatibility claim | Native/translated toolchain only after separate qualification | Worker architecture availability, compiler/SDK/runtime compatibility and actual sanitizer support |
| macOS Apple Silicon | Native Linux arm64 worker through the existing local engine | Apple Clang/libc++ with successful feature probes | Actual compile/CTest, `jthread` availability, sanitizer runtime and arm64 process/output cleanup |
| macOS Intel | Native Linux amd64 worker | Apple Clang/libc++ where the OS/toolchain remains supported | Exact SDK/OS floor, required features and diagnostic profiles |
| Linux amd64/arm64 | Matching-architecture Linux worker | GCC or Clang with its matching standard library | cgroup/resource limits, rootless-engine behavior, symbolizer and disconnected build proof |

Native paths are alternatives, not evidence that the current course ships these compilers. Do not call emulation a native performance result. MSVC uses its own flags and ABI; GNU sanitizer flags are not pasted into a Windows build. [Microsoft's ASan documentation](https://learn.microsoft.com/en-us/cpp/sanitizers/asan?view=msvc-170) supports x86/x64 Windows ASan and lists incompatible options; this design does not promise MSVC TSan or UBSan. Linux Clang/GCC ASan+UBSan and a separate TSan build are distinct profiles. [Clang TSan](https://clang.llvm.org/docs/ThreadSanitizer.html) lists supported 64-bit targets. Supported does not mean tested here. Sanitizers detect classes of observed errors; an empty report is not a correctness proof and they do not enforce the execution boundary.

## Offline fixtures and repeatability

Prepare tools once while connected, then verify a disconnected clean build. The fixture pack contains small text/CSV/binary files with SHA-256 manifests, malformed/truncated/oversized variants, a versioned serialization example, a deterministic generated corpus, a tiny vendored library with license/provenance, reference outputs and curated negative diagnostic fixtures. No pretrained models, remote APIs or package-manager downloads are needed. CMake `FetchContent` and external project steps must not fetch during a normal lesson. A missing tool or fixture produces a precise capability failure, not a network retry from Run.

Use out-of-source build directories per toolchain/profile. Do not mix MSVC/GCC, standard libraries, architectures, Debug/Release iterator settings or sanitizer objects. Fix the language level with `CXX_STANDARD 20`, `CXX_STANDARD_REQUIRED ON` and `CXX_EXTENSIONS OFF`; CMake documents that an optional level can otherwise decay to an earlier standard. [CMake standard requirement](https://cmake.org/cmake/help/v3.28/prop_tgt/CXX_STANDARD_REQUIRED.html).

## Assessments and misconception checks

Each lesson has a prediction, normal-case test, boundary/failure test and explanation. Every fourth unit includes a short delayed-retrieval prompt that reuses an earlier idea in a different input. The teacher reviews evidence, offers one progressive hint and asks the learner to explain a counterexample before revealing a solution. A green CTest line is execution evidence; completion additionally needs the learner's ownership/error argument and an independent transfer task.

Misconceptions are tested directly: a reference is not an owner; `const` through one name does not freeze all aliases; `at()` and `operator[]` have different contracts; vector capacity is not its size; move does not guarantee an empty source; undefined behavior is not a predictable exception; a warning-free build is not memory safety; Release can remove `assert`; atomic does not automatically mean a correct ordering argument; TSan does not prove a memory-order protocol; and a single fast timing is not a portable performance claim. Resource ownership follows the [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines), with the actual object lifetime demonstrated rather than merely named.

## Capstone acceptance

1. `cpp-014`: a readings CLI must pass fresh Debug/Release CTest, precise output and exit-status fixtures, empty/malformed input checks, and a source-level ownership explanation.
2. `cpp-028`: an installable record library must pass independent consumer/relocation checks, versioned byte/corpus tests and every supported diagnostic profile, with unavailable matrix cells explicit.
3. `cpp-042`: a bounded parallel analyzer must match a reference, terminate workers on failure/cancellation, preserve a stated memory bound, and provide repeated measurements that preserve semantics and record uncertainty.

The [JSON capstone entries](../plans/cpp.json) carry deliverables and acceptance lists for the future journey UI. Cross-track projects may consume these library/analysis artifacts later; they do not make Python a hidden prerequisite.

## Activation gates and current evidence

This phase validates a design and representative lesson, not an adapter. Before activation, author `courses/cpp/` with local guidance, independent learner/guide/solution files, real fixture hashes and additive extension metadata; keep these planned IDs stable. The existing extension playbook still requires full depth/practice audits, prerequisite graph checks and reader/app/MCP discovery tests. Compile/run storage, cancellation, stale-artifact prevention, invalid flags/paths, hostile CMake boundaries and the OS matrix must be proved before capability changes from planned. No compiler installation, container build or Windows/Linux runtime execution is claimed by these documents. A narrow design-phase check used the already-installed Apple Clang 21.0.0 on Darwin arm64: the worked program and fourteen-check solution passed direct Debug/Release compilation and execution, and the learner stubs failed as expected. CMake/CTest and the adapter remain unverified.

## Planned lesson sequence

This table is a compact view of the canonical JSON plan; the JSON contains the concrete lab and independent verification for every row.

### Beginner

| ID | Lesson | Minutes | Direct planned prerequisites |
| --- | --- | ---: | --- |
| `cpp-001` | Files, terminals and the compile-to-run journey | 75 | None |
| `cpp-002` | Your first C++20 target | 90 | `cpp-001` |
| `cpp-003` | Values, types and conversions | 90 | `cpp-002` |
| `cpp-004` | Branches, loops and state traces | 90 | `cpp-003` |
| `cpp-005` | Functions and parameter contracts | 90 | `cpp-004` |
| `cpp-006` | Strings and trustworthy integer input | 105 | `cpp-005` |
| `cpp-007` | Vectors and standard algorithms | 90 | `cpp-005` |
| `cpp-008` | Copies, const references and lifetimes | 90 | `cpp-007` |
| `cpp-009` | Vectors own; references borrow | 120 | `cpp-006`, `cpp-008` |
| `cpp-010` | Structs, enums and meaningful states | 90 | `cpp-005`, `cpp-009` |
| `cpp-011` | Files, streams and scoped resources | 105 | `cpp-006`, `cpp-009` |
| `cpp-012` | Headers, translation units and the linker | 90 | `cpp-005`, `cpp-010` |
| `cpp-013` | Warnings and CTest as feedback | 90 | `cpp-009`, `cpp-012` |
| `cpp-014` | Capstone 1: auditable readings CLI | 180 | `cpp-010`, `cpp-011`, `cpp-013` |

### Intermediate

| ID | Lesson | Minutes | Direct planned prerequisites |
| --- | --- | ---: | --- |
| `cpp-015` | RAII and unique ownership | 105 | `cpp-014` |
| `cpp-016` | Move semantics and the rule of zero | 105 | `cpp-015` |
| `cpp-017` | Errors as values and exceptions | 105 | `cpp-006`, `cpp-015` |
| `cpp-018` | Views, iterators and invalidation | 105 | `cpp-009`, `cpp-016` |
| `cpp-019` | Ranges and deliberate algorithms | 105 | `cpp-018` |
| `cpp-020` | Templates and concepts | 120 | `cpp-005`, `cpp-018` |
| `cpp-021` | Strong types and generic value APIs | 105 | `cpp-010`, `cpp-020` |
| `cpp-022` | Portable files and serialization | 120 | `cpp-011`, `cpp-017` |
| `cpp-023` | Library boundaries and ABI | 105 | `cpp-012`, `cpp-017`, `cpp-021` |
| `cpp-024` | Property tests and bounded fuzzing | 120 | `cpp-013`, `cpp-017` |
| `cpp-025` | Sanitizers and observable memory failures | 120 | `cpp-015`, `cpp-018`, `cpp-024` |
| `cpp-026` | Debugging and measurement tools | 120 | `cpp-013`, `cpp-025` |
| `cpp-027` | Reproducible dependencies and delivery | 105 | `cpp-013`, `cpp-023` |
| `cpp-028` | Capstone 2: reusable record library | 240 | `cpp-022`, `cpp-024`, `cpp-025`, `cpp-027` |

### Advanced

| ID | Lesson | Minutes | Direct planned prerequisites |
| --- | --- | ---: | --- |
| `cpp-029` | Threads, joining and cancellation | 120 | `cpp-028` |
| `cpp-030` | Mutexes, conditions and producer-consumer flow | 120 | `cpp-029` |
| `cpp-031` | Atomics and the memory model | 135 | `cpp-030` |
| `cpp-032` | Bounded parallel work and failure propagation | 135 | `cpp-017`, `cpp-030` |
| `cpp-033` | Testing concurrent code | 120 | `cpp-025`, `cpp-031`, `cpp-032` |
| `cpp-034` | Data layout, allocation and locality | 120 | `cpp-019`, `cpp-026` |
| `cpp-035` | Algorithmic and representation choices | 120 | `cpp-034` |
| `cpp-036` | Compile-time computation with a budget | 120 | `cpp-020`, `cpp-026` |
| `cpp-037` | Composing generic interfaces | 120 | `cpp-019`, `cpp-020`, `cpp-036` |
| `cpp-038` | Numerical and integer correctness | 120 | `cpp-017`, `cpp-025` |
| `cpp-039` | C interfaces and loading boundaries | 120 | `cpp-017`, `cpp-023`, `cpp-027` |
| `cpp-040` | Hardening parsers and execution boundaries | 135 | `cpp-022`, `cpp-024`, `cpp-025`, `cpp-032` |
| `cpp-041` | Portable release and performance evidence | 150 | `cpp-027`, `cpp-033`, `cpp-035`, `cpp-040` |
| `cpp-042` | Capstone 3: bounded parallel analyzer | 300 | `cpp-033`, `cpp-035`, `cpp-038`, `cpp-039`, `cpp-041` |

## Primary sources checked 2026-10-22

- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines): Resource ownership, RAII, value semantics and interface/lifetime reasoning.
- [CMake 3.28 CXX_STANDARD_REQUIRED](https://cmake.org/cmake/help/v3.28/prop_tgt/CXX_STANDARD_REQUIRED.html): Require the selected C++ standard rather than allowing silent decay.
- [CMake 3.28 CTest manual](https://cmake.org/cmake/help/v3.28/manual/ctest.1.html): Portable test invocation and bounded test execution.
- [Clang C++ implementation status](https://clang.llvm.org/cxx_status.html): A dialect switch is not evidence that every language/library feature is available.
- [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html): Diagnostic build/link flags, symbolization and platform boundaries.
- [Clang ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html): Separate race-diagnostic profile, supported 64-bit platforms and limitations.
- [Microsoft AddressSanitizer](https://learn.microsoft.com/en-us/cpp/sanitizers/asan?view=msvc-170): Windows x86/x64 ASan support and incompatible compiler/link options; no implied MSVC TSan/UBSan support.
