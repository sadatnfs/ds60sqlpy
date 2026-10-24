# Progression from first contact to independent projects

Use this as a design lens, not a required number of lessons or a claim that a
course can make every learner an expert. Reuse existing prerequisites and
remove topics irrelevant to the requested outcome. Advanced work should explain
tradeoffs and diagnose failure, not merely name more APIs.

## A reusable learning arc

| Stage | Learner capability | Useful evidence |
| --- | --- | --- |
| Orientation | Locate the source, run or inspect it, identify output and interpret one error | Explain source versus runtime versus result; repair a small mistake |
| Foundations | Trace values and control/query flow; choose basic representations | Predict output, construct a small program/query, test boundaries |
| Composition | Separate responsibilities, model data/state and handle failure | Build multiple cooperating functions/components with explicit contracts |
| Reliable work | Debug from evidence, test meaningful cases and preserve data | Diagnose a defect, demonstrate a negative case and recover without data loss |
| Advanced mechanisms | Explain ownership, complexity, concurrency or distribution | Compare alternatives using measured or logically derived evidence |
| Independent project | Design a bounded solution and justify its limits | Reproducible artifact, tests, operational notes and an explanation without copying |

Each practice lesson should move through observe/predict, guided modification,
independent construction, debugging, edge cases and transfer. A checkpoint can
revisit prerequisites rather than adding a new topic. A tutorial chapter uses
worked reasoning and complete examples instead of an exam or hidden answer.

## What the existing languages teach

| Route | Beginner foundations | Intermediate composition | Advanced independence |
| --- | --- | --- | --- |
| Python | Values, mutability, branches, loops, functions, tracebacks, files and modules | Collections, iterators, types, tests, environments, NumPy shapes/broadcasting, pandas grain/nulls/joins | Algorithms and complexity, concurrency, data contracts, packaging, bounded services and reproducible pipelines |
| PostgreSQL | Tables, row grain, keys, filters, NULL and deterministic ordering | Joins, aggregation, subqueries, CTEs, windows, constraints and transactions | Plans/indexes, isolation, migrations, roles, restore reasoning, temporal analytics and stateful projects |
| C++ | Source/compile/link/run, types, expressions, functions, strings and vectors | References, lifetimes, RAII, ownership, classes, templates and standard algorithms | Value/move semantics, exception guarantees, concurrency, measured performance, build boundaries and larger programs |
| Java | Source/bytecode/JVM, primitives, methods, arrays, objects and diagnostics | Collections/generics, interfaces, exceptions, streams, I/O and tests | Concurrency, memory/visibility, performance, API contracts, packaging and maintainable applications |
| JavaScript/TypeScript | Values/coercion, scope, functions, arrays/objects and modules | Promises, event loop, errors, type narrowing, interfaces and tests | Async cancellation, API boundaries, runtime validation, browser security and project architecture |
| Scala/Spark | Expressions, immutable values, types, functions and collections | Case classes, pattern matching, Options/errors, functional composition and tests | Spark schemas, lazy plans, partitions/shuffles, joins/skew, deterministic output, storage and distributed failure reasoning |
| C | Compile/link/run, scalar types, arrays, pointers and representation | Ownership discipline, strings, structs, files, error contracts and tests | Undefined behavior, concurrency, ABI, performance, robust parsers and systems boundaries |
| Go | Packages, values, slices/maps, functions and explicit errors | Interfaces, composition, tests, contexts, goroutines and channels | Service lifecycles, bounded concurrency, Kubernetes API/controller reasoning and operational recovery |
| C# | .NET compilation, values/references, methods, classes and collections | Generics, LINQ, exceptions, async/await, cancellation and testing | Memory/performance, concurrency, API boundaries, dependency design and application architecture |
| Rust | Ownership, borrowing, moves, enums, pattern matching and Result | Traits, generics, iterators, lifetimes, collections and tests | Concurrency, unsafe boundaries, performance, Arrow arrays/schema/nulls and data interoperability |
| Swift | Values, optionals, collections, functions and structs | Protocols, generics, errors, async tasks, actors and Foundation | Isolation, cancellation, app state and architecture; SwiftUI/UIKit/signing require the separate Apple SDK route |
| D3 specialization | SVG, selections, joins, scales, axes and data validation | Statistical graphics, missingness, reusable components and accessible interaction | Brush/zoom, hierarchy/network/geo layouts, Canvas, coordinated dashboards and actual browser acceptance |
| Docker | Process/image/container distinction, Dockerfile, ports and Compose | Networking, durable data, backup/restore, permissions and resource constraints | BuildKit, multi-stage/multi-platform, supply chain, CI, failure domains and scoped recovery |
| Kubernetes networking | Pod/node/Service addresses, CIDRs, CNI, DNS and endpoint readiness | Service data planes, NodePort, load balancers, Ingress/Gateway and TLS | Source-IP/NAT, policy enforcement, dual-stack, topology, draining, observability and request-path diagnosis |


Do not collapse Scala language foundations into the first Spark job. Keep
JavaScript's Node environment distinct from the browser DOM. Explain C++ and
Java entrypoints, staged filenames, compile errors and runtime errors before
asking for larger applications. SQL queries need row-grain contracts rather
than only matching one displayed result.

For each route, study its `README.md`, `AGENTS.md`, metadata and a beginner,
intermediate and advanced guide before designing a new subject. Prefer the
current manifests over memorized lesson counts. Preserve language-specific
semantics rather than translating another language's syllabus word for word.

## Projects, examples and assessment

A small project should combine already taught mechanisms and expose real
choices. Examples include a tested data-cleaning pipeline, transaction-safe
inventory workflow, bounded file-processing tool or local analytical job.
Choose one whose inputs, outputs, failure behavior and resource needs are
inspectable in the classroom. Avoid a project requiring an undeclared web
service, package install or production account. Check how the learner supplies
arguments, standard input, files and multiple source modules before choosing a
CLI or packaged-project capstone. Match the implemented browser channel or
provide a clearly separated prepared external workflow.

Show at least two worked examples with changed conditions, not only different
numbers. Include malformed/empty inputs where relevant, explain expected
invariants, and distinguish intentional failure from a defect. Tests should
reject a plausible wrong solution rather than merely repeat implementation
text. Do not mistake a completed checklist or reference run for independence.

For mathematical or ML material, explain notation, units, assumptions, objective,
identifiability or leakage risks, numerical implementation and interpretation.
For systems, explain ownership, isolation, observation, cleanup and recovery.
Reading-only lessons can use traces, diagrams, counterexamples and derivations
without inventing code execution. Tutorial chapters expose their full examples
and discussions directly when the chosen learning mode calls for it.
