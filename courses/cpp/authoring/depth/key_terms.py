"""Lesson-specific key terms appended to each depth guide's vocabulary section."""

import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
START = "<!-- terms:start -->"
END = "<!-- terms:end -->"

KEY_TERMS = {
    4: [
        ("branch", "a statement such as `if` that selects one path using a Boolean condition."),
        (
            "loop invariant",
            "a fact about the carried state that holds before and after every iteration, such "
            "as the total equaling the sum of the nonnegative values visited so far.",
        ),
        (
            "boundary input",
            "a value where a decision changes, such as zero for a nonnegative reading.",
        ),
        (
            "range-for loop",
            "a loop that visits each element once; a by-value loop variable is a copy, so "
            "changing it leaves the vector unchanged.",
        ),
    ],
    5: [
        (
            "pass by value",
            "each parameter receives its own copy, so changing it inside the function leaves "
            "the caller's variable unchanged.",
        ),
        (
            "precondition",
            "a promise the caller must satisfy before the call, such as low being at most high.",
        ),
        (
            "postcondition",
            "the guarantee the function makes about its result when the precondition holds.",
        ),
        (
            "pure function",
            "a function without hidden state, so the same inputs always produce the same value.",
        ),
    ],
    6: [
        ("`std::string`", "an owning container of characters."),
        (
            "`std::string_view`",
            "a non-owning view that observes characters owned by another object.",
        ),
        (
            "`from_chars`",
            "a locale-independent conversion that returns an error code and a pointer to the "
            "first unconsumed character.",
        ),
        (
            "full consumption",
            "the requirement that conversion stops at the end of the field, so input such as "
            "12x is rejected.",
        ),
        (
            "`std::optional<int>`",
            "a result that holds either a parsed number or absence, so a present zero stays "
            "distinct from a failure.",
        ),
    ],
    7: [
        ("`std::vector`", "an owning container that stores its elements in contiguous memory."),
        (
            "size and capacity",
            "size counts constructed elements the program may access; capacity counts how many "
            "elements fit before another allocation.",
        ),
        (
            "iterator",
            "an object that identifies a position in a sequence for a standard algorithm.",
        ),
        (
            "reallocation",
            "moving elements into a new buffer when capacity runs out, which invalidates every "
            "pointer, reference and iterator into the old storage.",
        ),
        (
            "predicate",
            "a function that returns true or false and tells an algorithm such as a count which "
            "elements match.",
        ),
    ],
    8: [
        (
            "value copy",
            "an independent object with its own state, so changing it leaves the original "
            "unchanged.",
        ),
        (
            "reference",
            "another name for an existing object that neither owns it nor extends its lifetime.",
        ),
        (
            "const reference",
            "an access path that blocks mutation through that name and avoids a copy, but does "
            "not freeze other aliases.",
        ),
        (
            "alias",
            "a second name for the same object, so a change through one name is visible through "
            "the other.",
        ),
        (
            "ownership",
            "responsibility for keeping an object alive; a vector owns its element storage.",
        ),
    ],
    10: [
        (
            "struct",
            "a type that groups related fields, such as id, cents and status, into one value.",
        ),
        (
            "`enum class`",
            "a scoped enumeration of named states that does not convert implicitly to an integer.",
        ),
        (
            "domain invariant",
            "a rule about which field combinations make sense, such as a settled payment "
            "carrying nonnegative cents.",
        ),
        (
            "aggregate initialization",
            "brace initialization that assigns fields in their declared order.",
        ),
    ],
    11: [
        (
            "stream",
            "an object that moves characters between a program and a source or destination and "
            "records whether its last operation succeeded.",
        ),
        (
            "`getline`",
            "extracts the next line and reports through the stream whether that extraction "
            "succeeded.",
        ),
        (
            "EOF",
            "the condition that no more input remains, which is set only after a read attempts "
            "to go past the available data.",
        ),
        (
            "bad I/O state",
            "a stream condition meaning an underlying device operation failed, which differs "
            "from reaching EOF.",
        ),
        (
            "RAII",
            "tying resource cleanup to scope exit, so a file stream closes its file when the "
            "stream object is destroyed.",
        ),
    ],
    12: [
        ("translation unit", "one source file after preprocessing has expanded its includes."),
        ("declaration", "states a name and its type so that calls can be type-checked."),
        ("definition", "supplies the function body or object storage for a declared name."),
        (
            "linker",
            "the tool that connects references in object files to the definitions they need.",
        ),
        (
            "one-definition rule",
            "the rule that forbids multiple or incompatible definitions of the same entity "
            "across translation units.",
        ),
    ],
    13: [
        (
            "compiler warning",
            "a diagnostic about suspicious code that does not by itself stop compilation.",
        ),
        (
            "CTest",
            "the CMake test driver, which runs registered test processes and reports their "
            "statuses.",
        ),
        (
            "`NDEBUG`",
            "a macro that, when defined, removes standard `assert` expressions together with "
            "any side effects inside them.",
        ),
        (
            "always-active check",
            "an ordinary condition with an explicit failure result that runs in every build "
            "configuration.",
        ),
        (
            "build configuration",
            "a named set of compiler options such as Debug or Release whose actual flags should "
            "be inspected.",
        ),
    ],
    14: [
        (
            "auditable CLI",
            "a command-line program whose inputs, accepted values, rejected records and output "
            "can be reconciled.",
        ),
        (
            "business validation",
            "the domain rule applied after a field parses as an integer, such as rejecting a "
            "negative reading.",
        ),
        (
            "conservation check",
            "the equation accepted plus rejected equals input rows, which catches dropped or "
            "uncounted records.",
        ),
        (
            "fatal operation failure",
            "an error such as a missing input file or an exceeded input budget that stops the "
            "run instead of counting as a rejected row.",
        ),
        ("integer cents", "whole-number currency units that avoid decimal rounding ambiguity."),
    ],
    15: [
        (
            "RAII",
            "acquiring a resource in an object and releasing it when that object leaves scope.",
        ),
        (
            "`unique_ptr`",
            "a move-only smart pointer that is the single owner of one dynamically allocated "
            "object.",
        ),
        ("`make_unique`", "constructs an object and returns the `unique_ptr` that owns it."),
        (
            "ownership transfer",
            "moving a `unique_ptr`, which hands cleanup responsibility to the destination and "
            "leaves the source empty.",
        ),
        (
            "borrowed raw pointer",
            "a non-owning pointer to an object managed elsewhere, which must never be used to "
            "delete it.",
        ),
    ],
    16: [
        (
            "move semantics",
            "letting a destination take internal resources from a source that will no longer be "
            "used in the same way.",
        ),
        (
            "rvalue reference",
            "a reference type written `T&&` that binds to objects eligible to be moved from.",
        ),
        (
            "`std::move`",
            "a cast that makes a move overload eligible; it does not transfer anything by itself.",
        ),
        (
            "rule of zero",
            "relying on members such as vector and string to supply copy, move and destruction "
            "behavior instead of writing those operations.",
        ),
        (
            "moved-from state",
            "a valid object whose exact contents are unspecified unless its type documents them.",
        ),
    ],
    17: [
        ("`std::optional`", "holds either one value or absence, without a detailed error reason."),
        (
            "`std::variant`",
            "holds exactly one of several alternative types, such as an int or a `ParseError`.",
        ),
        (
            "`holds_alternative`",
            "checks which alternative a variant currently holds before the caller extracts a "
            "value.",
        ),
        (
            "exception",
            "transfers control to a matching catch handler and unwinds the intermediate scopes.",
        ),
        (
            "errors as values",
            "returning failure inside the result type for expected rejections such as invalid "
            "input.",
        ),
    ],
    18: [
        ("view", "a non-owning handle that describes storage owned by another object."),
        ("`std::span`", "a view over contiguous elements described by an address and an extent."),
        (
            "`subspan`",
            "selects an offset and count within a span; the caller must keep both within bounds.",
        ),
        (
            "iterator invalidation",
            "the loss of validity of an iterator when its container reallocates or erases "
            "elements.",
        ),
    ],
    19: [
        ("range", "anything that provides a beginning and an end that can be traversed."),
        (
            "lazy view",
            "a range adaptor such as a filter that does its work during iteration rather than "
            "when it is built.",
        ),
        (
            "materialization",
            "copying a view's results into an owning container so later changes to the source "
            "do not affect them.",
        ),
        (
            "projection",
            "a member pointer or function such as `&Score::points` that selects what an "
            "algorithm compares without changing the record.",
        ),
    ],
    20: [
        ("function template", "describes a family of functions parameterized by types or values."),
        (
            "template argument deduction",
            "the compiler choosing template arguments from the types of the call arguments.",
        ),
        (
            "instantiation",
            "the compiler generating a concrete specialization for the chosen template arguments.",
        ),
        (
            "concept",
            "a named compile-time requirement such as `std::integral` that decides which types "
            "a template accepts.",
        ),
        (
            "`static_assert`",
            "a check evaluated during compilation that stops the build when its condition is "
            "false.",
        ),
    ],
    21: [
        (
            "strong type",
            "a wrapper such as `Cents` that gives a representation a domain name so unrelated "
            "values cannot be mixed.",
        ),
        (
            "explicit constructor",
            "a constructor marked `explicit`, which blocks implicit conversion from the "
            "underlying representation.",
        ),
        (
            "operator overloading",
            "defining operators such as `+` and `==` for a type, which should keep their "
            "familiar meaning.",
        ),
        (
            "identity element",
            "a value, such as zero cents for addition, that leaves any other value unchanged.",
        ),
    ],
    22: [
        (
            "serialization",
            "converting a value into a documented byte or text format that a reader can decode.",
        ),
        (
            "`std::filesystem::path`",
            "a platform-aware description of a file location, not a file format.",
        ),
        ("endianness", "the byte order of multi-byte values in memory or in a file."),
        (
            "version marker",
            "a field such as `v1` that lets a reader reject representations it does not support.",
        ),
        (
            "round trip",
            "writing a value and reading it back to the same value, which works only when "
            "writer and reader agree on the format.",
        ),
    ],
    23: [
        ("API", "the source-level interface that callers compile against."),
        (
            "ABI",
            "the compiled calling, layout and symbol conventions that separately built binaries "
            "need to work together.",
        ),
        (
            '`extern "C"`',
            "a linkage specification that gives a function C language linkage; it does not "
            "make C++ types or exceptions safe for C callers.",
        ),
        (
            "status code",
            "an integer result that reports success or a named failure separately from the "
            "output value.",
        ),
        (
            "output pointer",
            "a parameter through which the function writes its result, here only on success.",
        ),
    ],
    24: [
        (
            "property",
            "a relation that should hold across many inputs, such as reversing twice returning "
            "the original sequence.",
        ),
        (
            "metamorphic property",
            "a property relating the outputs of several executions without a handwritten "
            "expected value for each input.",
        ),
        ("golden fixture", "input paired with independently chosen expected values."),
        ("corpus", "a retained set of useful edge and failure inputs."),
        (
            "bounded fuzzing",
            "exploring generated inputs within a finite budget and saving the exact failing "
            "case for reproduction.",
        ),
    ],
    25: [
        (
            "undefined behavior",
            "an operation outside the language contract, such as out-of-bounds access or signed "
            "overflow, that has no meaningful result.",
        ),
        (
            "`vector::at`",
            "checked element access that throws `std::out_of_range` when the index is not less "
            "than the size.",
        ),
        (
            "sanitizer",
            "compiler instrumentation that detects selected violations while the program runs.",
        ),
        (
            "AddressSanitizer",
            "a sanitizer for memory errors such as certain out-of-bounds accesses and "
            "use-after-free.",
        ),
        (
            "UndefinedBehaviorSanitizer",
            "a sanitizer that detects several kinds of undefined operations, such as signed "
            "overflow.",
        ),
    ],
    26: [
        (
            "debugger",
            "a tool that pauses a process so its call stack and local values can be inspected.",
        ),
        ("breakpoint", "a chosen location where the debugger stops execution."),
        (
            "call stack",
            "the chain of active function calls that shows which caller reached the current point.",
        ),
        (
            "hypothesis",
            "a prediction about the cause of a mismatch that a specific observation can confirm "
            "or reject.",
        ),
        ("profile", "a measurement of where execution time or work was spent."),
    ],
    27: [
        (
            "reproducibility",
            "the ability of another environment to reconstruct the same declared build inputs.",
        ),
        (
            "dependency identity",
            "the exact source or artifact, version, build options and toolchain behind a "
            "dependency.",
        ),
        ("vendoring", "keeping an approved dependency's source inside the project."),
        (
            "CMake target",
            "a named build unit that passes its include paths, compile features and link "
            "requirements to consumers.",
        ),
        (
            "lock",
            "a record of exact dependency identities that still needs an actual offline build "
            "check.",
        ),
    ],
    28: [
        (
            "reusable record library",
            "a library whose data contract and parser are separate from user-interface and I/O "
            "code.",
        ),
        ("public contract", "the headers, types and behavior that callers rely on."),
        (
            "owning result",
            "a returned `Record` that holds its own id and cents values, so it stays valid "
            "after the input string is destroyed.",
        ),
        ("packaging", "declaring the headers and link targets that consumers use."),
        (
            "compatibility test",
            "a test that protects callers from accidental changes to the library contract.",
        ),
    ],
    29: [
        (
            "`std::thread`",
            "starts a function on a new thread of execution and must be joined or detached "
            "before it is destroyed.",
        ),
        (
            "join",
            "waits for a thread's function to finish, so the state it borrows can then be "
            "safely read or destroyed.",
        ),
        (
            "cooperative cancellation",
            "a stop request that the running code checks and honors, not a forced kill.",
        ),
        (
            "`std::jthread`",
            "a C++20 thread that requests a stop and joins automatically in its destructor.",
        ),
        (
            "`stop_token`",
            "the object a jthread's function checks to learn whether a stop was requested.",
        ),
    ],
    30: [
        (
            "mutex",
            "a lock that serializes access to shared state so only one thread holds it at a time.",
        ),
        (
            "condition variable",
            "a waiting mechanism that releases the mutex while a thread waits and reacquires it "
            "before the thread rechecks state.",
        ),
        (
            "predicate wait",
            "the overload of `wait` that rechecks the protected condition after every wakeup.",
        ),
        (
            "spurious wakeup",
            "a return from waiting without a matching state change, which is why the predicate "
            "is the source of truth.",
        ),
        ("queue invariant", "a rule about valid queue states, such as size at most capacity."),
    ],
    31: [
        (
            "atomic operation",
            "an indivisible access to one atomic object that cannot form a data race.",
        ),
        (
            "data race",
            "conflicting unsynchronized accesses to one non-atomic object from two threads, at "
            "least one a write, which is undefined behavior.",
        ),
        (
            "happens-before",
            "the ordering relation that guarantees one operation's effects are visible to another.",
        ),
        (
            "release and acquire",
            "a release store paired with an acquire load that reads it, which publishes the "
            "writes made before the store.",
        ),
        (
            "relaxed ordering",
            "atomicity without ordering of surrounding operations, suitable for independent "
            "counters.",
        ),
    ],
    32: [
        (
            "`std::future`",
            "a handle to a result that may arrive later and carries either a value or an "
            "exception.",
        ),
        (
            "`std::launch::async`",
            "the launch policy that runs a task asynchronously instead of letting the "
            "implementation defer it.",
        ),
        ("bounded parallelism", "limiting the number of simultaneous workers and queued items."),
        ("backpressure", "slowing producers when the system has no spare capacity."),
        (
            "failure propagation",
            "carrying a worker's error to the owner, for example by rethrowing it from `get`, "
            "instead of reporting partial success.",
        ),
    ],
    33: [
        ("schedule", "one ordering of the operations performed by different threads."),
        (
            "synchronization point",
            "an observable event, such as a fulfilled promise or a join, that establishes "
            "ordering in a test.",
        ),
        (
            "promise",
            "the producer side of a future, which a worker fulfills to signal that a value is "
            "ready.",
        ),
        (
            "stress test",
            "repeating a scenario many times, which can expose timing defects but does not "
            "enumerate every schedule.",
        ),
        (
            "ThreadSanitizer",
            "a sanitizer that detects many data races and needs a separate instrumented build "
            "from AddressSanitizer.",
        ),
    ],
    34: [
        (
            "data layout",
            "the arrangement that determines which values sit next to each other in memory.",
        ),
        ("array of structures", "a layout that stores complete records together."),
        ("structure of arrays", "a layout that stores each field in its own sequence."),
        (
            "locality",
            "accessing nearby memory, which can reduce memory traffic when a calculation reads "
            "one field.",
        ),
        (
            "allocation count",
            "the number of dynamic allocations, a cost separate from algorithmic work.",
        ),
    ],
    35: [
        ("algorithmic complexity", "how work grows with input size under a stated model."),
        (
            "index",
            "a structure built once, such as a map of counts, so that later queries cost less "
            "than a linear scan.",
        ),
        (
            "amortized cost",
            "index construction work spread across the repeated queries that actually reuse the "
            "index.",
        ),
        ("benchmark", "a comparison of defined workloads under measured conditions."),
        (
            "`map::operator[]`",
            "access that inserts a value-initialized mapped value when the key is absent, "
            "unlike `find`.",
        ),
    ],
    36: [
        (
            "`constexpr`",
            "allows a function or object to take part in constant evaluation when its inputs "
            "and operations allow it.",
        ),
        (
            "`consteval`",
            "marks an immediate function whose every call must be evaluated during compilation.",
        ),
        ("constant evaluation", "computing a value during compilation instead of at run time."),
        (
            "compile-time budget",
            "the build time, compiler memory and binary size that compile-time computation adds.",
        ),
    ],
    37: [
        (
            "input range",
            "a range that may support only one pass, so reading an element can consume the source.",
        ),
        (
            "single-pass algorithm",
            "an algorithm that visits each element once, which keeps it correct for input ranges.",
        ),
        (
            "owning return",
            "returning a vector with its own storage, which stays valid even when the caller "
            "passed a temporary.",
        ),
        ("dangling view", "a view whose underlying storage has already been destroyed."),
        (
            "semantic contract",
            "the meaning of an operation that a concept cannot express, so prose and tests must "
            "state it.",
        ),
    ],
    38: [
        (
            "signed overflow",
            "an `int` result outside the representable range, which is undefined behavior "
            "rather than wraparound.",
        ),
        (
            "checked add",
            "an addition guarded by a test, such as `a > max - b`, that runs before the "
            "dangerous operation.",
        ),
        (
            "floating-point rounding",
            "the approximation of most decimal fractions, such as 0.1, by nearby binary values.",
        ),
        ("tolerance", "the acceptable numerical error chosen for a specific scale."),
        (
            "stable algorithm",
            "an algorithm that limits the rounding error accumulated across many operations.",
        ),
    ],
    39: [
        (
            "C interface",
            "functions with C linkage and C-compatible types that clients built with another "
            "compiler can call.",
        ),
        (
            "opaque handle",
            "a pointer-shaped value that hides the implementation layout from consumers.",
        ),
        (
            "paired allocation and release",
            "the rule that the provider that created an object also destroys it, instead of the "
            "consumer using its own delete.",
        ),
        (
            "no-throw boundary",
            "an interface that catches exceptions internally and reports failure as null or a "
            "status code.",
        ),
        (
            "custom deleter",
            "a function given to `unique_ptr`, such as the provider's destroy function, so "
            "cleanup uses the correct release.",
        ),
    ],
    40: [
        ("hardening", "enforcing explicit bounds before processing input of untrusted shape."),
        (
            "identifier grammar",
            "a narrow character and length policy, such as accepting `batch_7`, that keeps user "
            "input from being interpreted as a path.",
        ),
        (
            "path traversal",
            "using separators or parent references such as `../secret` to reach locations "
            "outside an intended directory.",
        ),
        (
            "resource budget",
            "a cap on input bytes, record count and field length that is enforced while "
            "reading, before expensive work.",
        ),
        (
            "gated publication",
            "writing a report only after the accepted and rejected accounting meets the "
            "declared policy.",
        ),
    ],
    41: [
        (
            "release packet",
            "a record that links source identity to a tested binary, a documented platform and "
            "its evidence.",
        ),
        ("source identity", "a revision or hash that names exactly which source was built."),
        ("portability", "a claim demonstrated only by execution on each claimed environment."),
        (
            "output schema",
            "the report format that consumers rely on, such as schema 1 with rows and total.",
        ),
        (
            "performance evidence",
            "a statement of workload, limits and measurements, not a single unqualified timing.",
        ),
    ],
    42: [
        (
            "serial oracle",
            "a single-threaded computation that establishes the expected result independently "
            "of scheduling.",
        ),
        ("task budget", "a limit on worker count and input size."),
        (
            "conservation of work",
            "the rule that every accepted task ends as completed, canceled or failed before the "
            "outcome is reported.",
        ),
        (
            "failure accounting",
            "naming rejected input and canceled work instead of hiding them inside an "
            "apparently successful total.",
        ),
        (
            "disjoint partition",
            "input slices that do not overlap, so each worker writes only its own subtotal.",
        ),
    ],
}


def block(n):
    """Render and validate one lesson's key-term bullets."""
    terms = KEY_TERMS[n]
    names = [term.lower() for term, _ in terms]
    if not 3 <= len(terms) <= 5 or len(set(names)) != len(names):
        raise SystemExit(f"cpp-{n:03d}: needs three to five distinct key terms")
    for term, definition in terms:
        text = term + definition
        if not term.strip() or not definition.strip().endswith("."):
            raise SystemExit(f"cpp-{n:03d}: each key term needs a full definition")
        if "\u2014" in text or "\u2013" in text:
            raise SystemExit(f"cpp-{n:03d}: key terms must not use em or en dashes")
    rows = "\n".join(f"- **{term}:** {definition}" for term, definition in terms)
    return f"{START}\n\n{rows}\n\n{END}"


def apply_key_terms(text, n):
    """Insert or replace the marked key-term list at the end of Vocabulary and concepts."""
    section = re.search(r"(?ms)^## Vocabulary and concepts\n.*?(?=^## )", text)
    if not section:
        raise SystemExit(f"cpp-{n:03d}: missing Vocabulary and concepts section")
    body = re.sub(
        rf"\n*{re.escape(START)}.*?{re.escape(END)}\n*", "\n\n", section.group(0), flags=re.S
    )
    body = body.rstrip("\n") + "\n\n" + block(n) + "\n\n"
    return text[: section.start()] + body + text[section.end() :]


if __name__ == "__main__":
    for n in KEY_TERMS:
        path = BASE / f"guides/cpp-{n:03d}.md"
        text = path.read_text()
        updated = apply_key_terms(text, n)
        if updated != text:
            path.write_text(updated)
