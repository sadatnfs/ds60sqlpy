# Go: practical programs and Kubernetes controllers

Start in the unified Docker classroom and choose **Go**. You need the prepared
Go worker, not a host compiler. Windows uses WSL 2; all ordinary execution runs
inside Linux containers. Your source, notes and prior results belong to your
saved learner workspace and remain separate from every other language.

This 48-lesson route starts with source, values and control flow, then develops
ownership, interfaces, testing, data processing, HTTP, concurrency and production
boundaries. Its final fourteen lessons connect Go to Kubernetes: objects,
selectors, reconciliation, resource versions, watches, queues, client-go,
informers, finalizers, RBAC, leader election, admission, testing and a capstone.

## Choose a starting point

| Lessons | What you will build and explain |
| --- | --- |
| 001-008 | Checked programs, numeric contracts, loops, functions, slices, maps, Unicode and structs |
| 009-016 | Pointer ownership, method sets, interfaces, errors, cleanup, modules, tests, generics and closures |
| 017-024 | Bounded streaming, filesystem interfaces, strict JSON/CSV, CLI configuration, HTTP boundaries and goroutines |
| 025-032 | Channels, cancellation, protected state, worker pools, memory ordering, algorithms, logging and security |
| 033-034 | Transaction boundaries, build targets, containers and shutdown policy |
| 035-042 | Kubernetes desired state, selection, convergence, conflicts, watches, queues and actual client-go project structure |
| 043-048 | Owned deletion, least authority, coordination limits, admission, layered tests and a resumable controller design |

The route is a prerequisite chain for learners starting from zero. Experienced
learners may enter a later lesson after explaining its prerequisite vocabulary
and reproducing a normal and boundary case independently. The minute estimates
are planning aids rather than deadlines.

## A useful lesson routine

1. Read the mechanism and vocabulary before executing a program.
2. Predict both worked examples, including any error or absence result.
3. Open the answer-free source and implement the six investigations.
4. Save the actual compiler or runtime evidence with your notes.
5. Reveal the separate executable reference and explanations when you want to compare.
6. Return later and solve a changed case without copying the reference.

References deliberately contain checks that fail if the claimed behavior is
wrong. A success message alone is not the verifier, and running a reference does
not demonstrate independent understanding.

## What runs in the browser

The ordinary `go` profile stages one `main.go` and compiles it with the prepared
Go toolchain through fixed compile/link operations and a prepared immutable
standard-library import configuration. It does not run a writable package manager
or fetch dependencies during a learner job. References use the standard library, small synthetic inputs and
bounded work. They do not install dependencies or use ambient credentials.
Interactive standard input, arbitrary process arguments, multi-file projects,
cgo, host files and cluster operations are not implied by a language pad.

Kubernetes chapters use clearly labeled offline models to isolate decision
rules. They do not pretend that a simulated reconciliation proves a real
rollout. Use the owned Kubernetes module for actual cluster exercises.

The [prepared client-go project](fixtures/client-go-project/README.md) contains
real pinned client-go code, typed-client HTTP tests and an explicitly configured
read-only Pod listing command. Dependency preparation and deliberate execution
are separate from opening a lesson. It refuses ambient context selection and
credential plugins. No project command should use an unrelated cluster.

## Continue as a contributor

[Authoring instructions](authoring/README.md) explain the durable sources.
[Subject guidance](AGENTS.md) records the runtime and teaching boundaries.
The generated `track.json` and `lessons.json` are derived from those sources.
Do not edit generated guides alone or change stable IDs to reorder the route.
