# C++ from first compilation to complete projects

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **C++ from first compilation to complete projects** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work. Native terminal/editor commands below are optional alternatives.


This 42-lesson journey begins with source files, the compiler, the linker and
a running process. It develops values and control flow into ownership, standard
containers, generic programming, error handling, concurrency and maintainable
projects. Every lesson has a guide, a learner worksheet and separate solutions.

Start with [cpp-001](guides/cpp-001.md), then open the course's **Journeys** page
and select the next lesson. The `cpp20` Docker worker compiles one C++20 source
file with GCC and returns compiler diagnostics, standard output and exit status
to the browser. No host C++ installation is required. Use the
[Docker classroom guide](../../docs/docker-classroom.md) to build and start it.

For multiple source files, headers, CMake, CTest and installed libraries, follow
[Compile, run and organize a C++ project](compile-and-run.md). Those complete
project fixtures use explicit Docker commands and explain which directory is
the source, which is the build tree, and which files are generated. The browser
pad remains a single-source-file environment.

Read the guide, predict a result, attempt the exercises and request a hint when
needed. Inspect compiler messages before changing code. The app saves your pad,
notes and job history in its learning volume. Reference programs remain separate
and are revealed for comparison; a passing example does not establish mastery.

## Lesson sequence

| Lesson | Level | Runtime |
| --- | --- | --- |
| [cpp-001: Files, terminals and the compile-to-run journey](guides/cpp-001.md) | Beginner | `reading` |
| [cpp-002: Your first C++20 target](guides/cpp-002.md) | Beginner | `cpp20` |
| [cpp-003: Values, types and conversions](guides/cpp-003.md) | Beginner | `cpp20` |
| [cpp-004: Branches, loops and state traces](guides/cpp-004.md) | Beginner | `cpp20` |
| [cpp-005: Functions and parameter contracts](guides/cpp-005.md) | Beginner | `cpp20` |
| [cpp-006: Strings and trustworthy integer input](guides/cpp-006.md) | Beginner | `cpp20` |
| [cpp-007: Vectors and standard algorithms](guides/cpp-007.md) | Beginner | `cpp20` |
| [cpp-008: Copies, const references and lifetimes](guides/cpp-008.md) | Beginner | `cpp20` |
| [cpp-009: Vectors own; references borrow](guides/cpp-009.md) | Beginner | `cpp20` |
| [cpp-010: Structs, enums and meaningful states](guides/cpp-010.md) | Beginner | `cpp20` |
| [cpp-011: Files, streams and scoped resources](guides/cpp-011.md) | Beginner | `cpp20` |
| [cpp-012: Headers, translation units and the linker](guides/cpp-012.md) | Beginner | `cpp20` |
| [cpp-013: Warnings and CTest as feedback](guides/cpp-013.md) | Beginner | `cpp20` |
| [cpp-014: Capstone 1: auditable readings CLI](guides/cpp-014.md) | Beginner | `cpp20` |
| [cpp-015: RAII and unique ownership](guides/cpp-015.md) | Intermediate | `cpp20` |
| [cpp-016: Move semantics and the rule of zero](guides/cpp-016.md) | Intermediate | `cpp20` |
| [cpp-017: Errors as values and exceptions](guides/cpp-017.md) | Intermediate | `cpp20` |
| [cpp-018: Views, iterators and invalidation](guides/cpp-018.md) | Intermediate | `cpp20` |
| [cpp-019: Ranges and deliberate algorithms](guides/cpp-019.md) | Intermediate | `cpp20` |
| [cpp-020: Templates and concepts](guides/cpp-020.md) | Intermediate | `cpp20` |
| [cpp-021: Strong types and generic value APIs](guides/cpp-021.md) | Intermediate | `cpp20` |
| [cpp-022: Portable files and serialization](guides/cpp-022.md) | Intermediate | `cpp20` |
| [cpp-023: Library boundaries and ABI](guides/cpp-023.md) | Intermediate | `cpp20` |
| [cpp-024: Property tests and bounded fuzzing](guides/cpp-024.md) | Intermediate | `cpp20` |
| [cpp-025: Sanitizers and observable memory failures](guides/cpp-025.md) | Intermediate | `cpp20` |
| [cpp-026: Debugging and measurement tools](guides/cpp-026.md) | Intermediate | `cpp20` |
| [cpp-027: Reproducible dependencies and delivery](guides/cpp-027.md) | Intermediate | `cpp20` |
| [cpp-028: Capstone 2: reusable record library](guides/cpp-028.md) | Intermediate | `cpp20` |
| [cpp-029: Threads, joining and cancellation](guides/cpp-029.md) | Advanced | `cpp20` |
| [cpp-030: Mutexes, conditions and producer-consumer flow](guides/cpp-030.md) | Advanced | `cpp20` |
| [cpp-031: Atomics and the memory model](guides/cpp-031.md) | Advanced | `cpp20` |
| [cpp-032: Bounded parallel work and failure propagation](guides/cpp-032.md) | Advanced | `cpp20` |
| [cpp-033: Testing concurrent code](guides/cpp-033.md) | Advanced | `cpp20` |
| [cpp-034: Data layout, allocation and locality](guides/cpp-034.md) | Advanced | `cpp20` |
| [cpp-035: Algorithmic and representation choices](guides/cpp-035.md) | Advanced | `cpp20` |
| [cpp-036: Compile-time computation with a budget](guides/cpp-036.md) | Advanced | `cpp20` |
| [cpp-037: Composing generic interfaces](guides/cpp-037.md) | Advanced | `cpp20` |
| [cpp-038: Numerical and integer correctness](guides/cpp-038.md) | Advanced | `cpp20` |
| [cpp-039: C interfaces and loading boundaries](guides/cpp-039.md) | Advanced | `cpp20` |
| [cpp-040: Hardening parsers and execution boundaries](guides/cpp-040.md) | Advanced | `cpp20` |
| [cpp-041: Portable release and performance evidence](guides/cpp-041.md) | Advanced | `cpp20` |
| [cpp-042: Capstone 3: bounded parallel analyzer](guides/cpp-042.md) | Advanced | `cpp20` |

## Validation and limits

All runnable reference programs have successful local Linux arm64 Docker
receipts for their current source bytes. The
[implementation checkpoint](../../docs/implementation/CHECKPOINT.md) records
runtime, test and platform acceptance separately. Reading lessons use reasoning
and written evidence. Windows/WSL2 and amd64 configuration support does not by
itself establish an observed run on those systems.

Both complete CMake projects and all 76 added worked programs also compiled and
ran in the prepared GCC image. New source changes or another toolchain require
appropriate new checks. Course fixtures use local authored inputs and do not
install dependencies while a lesson runs.
