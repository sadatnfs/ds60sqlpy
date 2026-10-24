# C: memory, systems and reliable native programs

Open the unified Docker classroom and choose **C**. The prepared `c17` worker
compiles one `main.c` and executes it with bounded time and output. You do not need
a host compiler. Windows uses WSL 2 and the same Linux-container route as other
hosts. Saved source, notes and results remain isolated from other languages.

This 42-lesson route develops a precise model of values, storage, lifetime and
resource ownership before introducing data structures, POSIX facilities,
concurrency and maintainable native projects. It teaches safe alternatives to
undefined behavior instead of asking you to infer safety from a program that
happens not to crash.

## Choose your route

| Lessons | Capabilities and observable evidence |
| --- | --- |
| 001-007 | Compile/link/run, ranges, sequencing, loops, function contracts, arrays and bounded strings |
| 008-014 | Pointer targets, array views, tagged values, lifetime, const access, macros and complete numeric parsing |
| 015-021 | Checked allocation, vectors, ownership moves/clones, streams, byte order, callbacks and linked lists |
| 022-028 | Queues, hash tables, binary search, recursion, string builders, injected failure and multi-file builds |
| 029-035 | Aliasing, sanitizers, arithmetic boundaries, generic byte APIs, flexible records, descriptors and signals |
| 036-042 | Pthreads, predicate-based waiting, atomics, layout, ABI contracts, state-machine parsing and a validated pipeline |

A new learner should follow the prerequisite chain. An experienced learner can
start later after independently explaining the earlier memory and bounds
contracts. The time estimates are suggestions, not a required schedule.

## How to use each lesson

1. Read the mechanism, vocabulary and syntax anatomy.
2. Predict both worked examples, including failure behavior.
3. Implement the six investigations in the answer-free source.
4. Keep actual compiler diagnostics and assertion results with your notes.
5. Reveal the complete reference and explained answers for comparison.
6. Return later and solve a changed input or ownership pattern independently.

References use an always-on `CHECK` helper, so `NDEBUG` cannot erase required
operations or checks. Do not discard errors or remove checks to get a successful
process result. A successful
run establishes only the checked cases and their stated assumptions.

## Execution boundaries

Ordinary references use bounded synthetic data and owned temporary resources.
No lesson opens a host file, fetches packages, mounts an engine socket or receives
an ambient cluster context. A pointer is valid only under its documented lifetime,
alignment, bounds and access rules.

The language target is C17. Descriptor and pthread chapters explicitly use POSIX
APIs supplied by the Linux worker. They are not promises about native Windows
compilation. The browser does not accept arbitrary compiler flags, interactive
input or multi-file archives.

The [real multi-file project](fixtures/stats-project/README.md) teaches headers,
object compilation, linking, Make dependencies and sanitizer qualification in a
separately prepared contributor environment. The ordinary pad teaches the same
API reasoning in one file and does not claim to run that external Makefile.

The final parser and pipeline deliberately define narrow grammars. They are not
general CSV implementations. Read the accepted-input policy before adapting them
to data containing quoting, embedded newlines, Unicode identifiers or untrusted
sizes.

## Contribute

[Authoring instructions](authoring/README.md) identify the durable sources and
regeneration command. [Subject agent guidance](AGENTS.md) records the stable IDs,
runtime contract and safety rules. Never edit a generated guide without changing
its maintained specification.
