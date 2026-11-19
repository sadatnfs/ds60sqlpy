"""Lesson outcomes for the published Java route: one observable ability per lesson.

render.py requires an entry for every rendered lesson ID and rejects an outcome that
merely repeats the first sentence of the mental model.
"""

OUTCOMES = {
    "java-001": "Compile and run Main.java with assertions enabled and tell a compiler diagnostic from a runtime failure.",
    "java-002": "Predict integer and decimal arithmetic, widen before overflow, and use BigDecimal value and scale deliberately.",
    "java-003": "Write guarded conditions, loops with explicit invariants and an exhaustive switch expression, and expose an off-by-one boundary.",
    "java-004": "Write methods with explicit preconditions and predict what a call can change for primitive and object arguments.",
    "java-005": "Copy arrays safely and count, slice and normalize strings by code point instead of by UTF-16 unit.",
    "java-006": "Choose a List, Set or Map for a counting task and produce deterministic output from unordered collections.",
    "java-007": "Encapsulate state in a class whose methods reject invalid input and leave the object unchanged on failure.",
    "java-008": "Write records and constructors that normalize, copy and validate their components so every instance is valid.",
    "java-009": "Manage resources with try-with-resources and read close order, suppressed exceptions and translated causes.",
    "java-010": "Program to an interface, compose behavior by delegation, and switch exhaustively over a sealed type with record patterns.",
    "java-011": "Implement consistent equals, hashCode and Comparator ordering and show the failures that inconsistent keys cause.",
    "java-012": "Use generic types and bounded wildcards so producers, consumers and return types stay type-safe.",
    "java-013": "Use lambdas and functional interfaces, compose functions in the intended order, and avoid mutable captured state.",
    "java-014": "Build stream pipelines with collectors, explain laziness and single use, and choose a reduction identity that is safe.",
    "java-015": "Represent instants, local dates and zoned times correctly across daylight-saving gaps and overlaps.",
    "java-016": "Read and write files with explicit encodings, close directory streams and keep path checks honest.",
    "java-017": "Model optional results with Optional, choose eager or lazy fallbacks, and validate input at the boundary.",
    "java-018": "Write tests that fail on a broken implementation, including boundary, property and exception checks.",
    "java-019": "Choose a queue, stack or priority queue for a task and measure the work a linear search performs.",
    "java-020": "Implement binary search, stable sorting and dynamic programming that handle empty, tied and unreachable cases.",
    "java-021": "Create threads, publish results safely through start, join or volatile, and respond correctly to interruption.",
    "java-022": "Run tasks with executors and futures that use bounded waits, cooperative cancellation and bounded queues.",
    "java-023": "Protect shared state with locks, atomics and concurrent maps, and avoid deadlock with a single lock order.",
    "java-024": "Use virtual threads for blocking work, limit scarce resources with a semaphore and cancel blocked tasks.",
    "java-025": "Explain object reachability and retention and measure allocation and memory use without misleading claims.",
    "java-026": "Compile and run a two-module application and read its module descriptors, exports and dependency errors.",
    "java-027": "Build a runnable JAR reproducibly and detect when a changed source produces a different artifact.",
    "java-028": "Serve and call an owned loopback HTTP endpoint and keep status, method and route errors distinct.",
    "java-029": "Use JDBC prepared statements and transactions against H2, binding untrusted values and rolling back failures.",
    "java-030": "Serialize a versioned binary format and reject unknown versions, truncation, oversized lengths and trailing data.",
    "java-031": "Inspect annotations, invoke methods reflectively and load services with ServiceLoader while preserving failure causes.",
    "java-032": "Measure performance with warm-up, checksums and JFR events and report the result without overclaiming.",
    "java-033": "Enforce secure file and operation boundaries that reject traversal, symbolic links, oversized input and unknown commands.",
    "java-034": "Separate pure domain logic from infrastructure so validation and failures are testable before any repository call.",
    "java-035": "Build and test a small local HTTP data service that validates queries strictly and leaves its storage unchanged.",
    "java-036": "Package, self-test and verify a release artifact, rejecting tampering before execution and recording its runtime scope.",
}
