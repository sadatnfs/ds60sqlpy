"""Lesson outcomes for the published C route: one observable ability per lesson.

render.py requires an entry for every generated lesson ID and rejects templated text.
MINUTES overrides the level-based estimate where a lesson is larger than its stage.
"""

OUTCOMES = {
    "c-001": "Compile, link and run a one-file C17 program whose checks fail loudly instead of printing an unchecked result.",
    "c-002": "Predict integer division, unsigned wraparound and floating rounding, and widen before a multiplication can overflow.",
    "c-003": "Predict grouping, short-circuit evaluation, integer promotion and signed-unsigned conversions before running an expression.",
    "c-004": "Write branches and loops with explicit invariants that handle zero iterations, exact thresholds and safe reverse traversal.",
    "c-005": "Declare prototypes and use output parameters that are written only on success and validated before use.",
    "c-006": "Pass arrays with an explicit element count and keep every access inside the logical length.",
    "c-007": "Manage strings with explicit capacity, detect truncation from snprintf's return value and compare content with strcmp.",
    "c-008": "Use pointers to read or update a caller-owned object and reject a null target before dereferencing it.",
    "c-009": "Traverse and slice arrays with pointer arithmetic while keeping one-past-the-end pointers undereferenced.",
    "c-010": "Model domain values with structs, enums and tagged unions, and reject an invalid tag instead of guessing.",
    "c-011": "Distinguish scope from storage duration and return only addresses whose objects outlive the call.",
    "c-012": "Use const-qualified views to state which functions may mutate data, and explain what const does not guarantee.",
    "c-013": "Write safe parenthesized macros, prefer typed functions for side effects and enforce assumptions with _Static_assert.",
    "c-014": "Parse integers with strtol and reject empty input, trailing characters and out-of-range values using errno and the end pointer.",
    "c-015": "Allocate with a checked size calculation, initialize the memory and release it exactly once on every path.",
    "c-016": "Implement a growable vector whose reallocation preserves contents and leaves the vector unchanged when growth fails.",
    "c-017": "Design owning and borrowing APIs, clone independent storage and make cleanup safe to call twice.",
    "c-018": "Read and write files with stdio while handling short reads, end-of-file and close errors explicitly.",
    "c-019": "Encode and decode fixed-width big-endian integers with explicit length checks and promotion-safe shifts.",
    "c-020": "Pass function pointers as callbacks and write a qsort comparator that is correct for extreme values and ties.",
    "c-021": "Build, count and reverse a singly linked list in place without losing or leaking nodes.",
    "c-022": "Implement a ring buffer that rejects reads when empty and writes when full while reusing storage in FIFO order.",
    "c-023": "Implement an open-addressing hash table that resolves collisions and distinguishes an absent key from a stored zero.",
    "c-024": "Implement a lower-bound binary search that handles empty input, duplicates and the no-match boundary.",
    "c-025": "Traverse a binary tree recursively with an explicit depth budget and correct empty-tree behavior.",
    "c-026": "Build a bounded string builder whose appends either succeed completely or leave the buffer unchanged.",
    "c-027": "Inject allocation failures into tests and assert that outputs and existing state survive every failure path.",
    "c-028": "Split a program into a header and translation units with one definition per symbol and reproducible behavior.",
    "c-029": "Inspect object bytes with unsigned char and memcpy, and name the aliasing rule that a pointer cast would break.",
    "c-030": "Turn a sanitizer finding into a bounds-checked regression test that runs safely without the original undefined behavior.",
    "c-031": "Check addition and multiplication for overflow before computing a value or an allocation size.",
    "c-032": "Write a generic byte-swap API that is parameterized by element size and respects alignment and zero-length calls.",
    "c-033": "Allocate a record with a flexible array member in one checked allocation and clone it without sharing storage.",
    "c-034": "Move bytes through a POSIX pipe, observe end-of-file after every write end is closed, and account for duplicated descriptors.",
    "c-035": "Install a minimal signal handler that only records a flag, and explain why -std=c17 builds must reinstall it after each delivery.",
    "c-036": "Create POSIX threads with separate argument storage and join every thread before using its result.",
    "c-037": "Protect shared state with a mutex and wait on a condition variable inside a predicate loop.",
    "c-038": "Use C11 atomics for counters and compare-and-exchange, and publish initialized data with release-acquire ordering.",
    "c-039": "Compare row and column data layouts with an honest, repeatable experiment that keeps results identical.",
    "c-040": "Design a C ABI function with caller-owned buffers, a size query and explicit insufficient-capacity errors.",
    "c-041": "Parse a bounded input grammar with an explicit state machine that rejects empty fields, trailing separators and overflow.",
    "c-042": "Build a validated record pipeline that commits a summary only when every record parses, so a malformed record never publishes a partial total.",
}

MINUTES = {"c-042": 180}
