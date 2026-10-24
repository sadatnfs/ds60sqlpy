# ruff: noqa: E501
# Long original prose and embedded programs are content, not Python expression layout.
"""Swift composition, ownership, packages and structured concurrency."""

from render import lesson

lesson(
    "Protocols and behavioral substitution",
    """A protocol declares capabilities that a conforming type must supply. It lets a consumer depend on a behavior rather than one storage representation. Both structs and classes can conform, which separates the choice of value or reference semantics from the public capability.

A conforming type must preserve the behavioral contract, not just compile with the right method names. Specify units, invalid inputs and mutation. Protocol extensions can share default behavior, but dispatch differences matter when a method is not a protocol requirement. Begin with explicit requirements and test the consumer with distinct implementations.""",
    "`protocol Pricer` declares a required method. A type lists conformance after a colon. `any Pricer` is an existential container that can hold differing conforming concrete types behind the protocol interface.",
    [
        ("Protocol", "A declared set of required capabilities."),
        ("Conformance", "A type satisfying a protocol contract."),
        ("Existential", "A value hiding a concrete type behind a protocol interface."),
    ],
    (
        "Use a capability",
        "let price: any Pricer = FlatPrice(unit: 3)\nprecondition(price.cost(units: 4) == 12)",
        "The consumer calls the pricing capability without needing its storage details.",
        "The interface preserves units and result meaning while hiding representation.",
    ),
    (
        "Substitute another policy",
        "let prices: [any Pricer] = [FlatPrice(unit: 3), CappedPrice(unit: 3, cap: 10)]\nprecondition(prices.map { $0.cost(units: 4) } == [12, 10])",
        "Two conforming policies produce different valid prices.",
        "Substitution allows variation within the documented contract, not arbitrary semantic disagreement.",
    ),
    [
        "Trace the protocol call to each concrete implementation.",
        "Add a second flat price without changing the consumer.",
        "Define a protocol for a deterministic label formatter.",
        "Diagnose two conformers using incompatible units.",
        "Test zero units and the exact cap.",
        "Choose a dependency worth abstracting in the importer and explain why a protocol helps.",
    ],
    "A protocol is not automatically a good abstraction for every type. Default extension methods not declared as requirements can have surprising static dispatch. Preserve behavior and error semantics across conformers.",
    helpers="protocol Pricer { func cost(units: Int) -> Int }\nstruct FlatPrice: Pricer { let unit: Int; func cost(units: Int) -> Int { unit * units } }\nstruct CappedPrice: Pricer { let unit: Int; let cap: Int; func cost(units: Int) -> Int { min(unit * units, cap) } }",
)

lesson(
    "Generics and relationships between types",
    """Generics preserve type relationships across an algorithm or container. A generic pair stores two values of the same chosen type. The compiler rejects mixing unrelated types unless the API explicitly models that possibility. This is stronger and clearer than storing Any and casting later.

Constraints expose the capabilities an algorithm needs. Comparable permits ordering, while Equatable permits equality. Use the narrowest useful constraint and state behavior for ties and empty inputs. Generic abstraction is valuable when it removes duplicated mechanisms without erasing domain meaning.""",
    "`func larger<T: Comparable>` introduces a constrained type parameter. The return type T preserves the input relationship. Generic structs use the same parameter syntax.",
    [
        ("Generic parameter", "A type placeholder constrained at compile time."),
        ("Constraint", "A required capability for a type argument."),
        ("Type relationship", "A connection between input, stored and output types."),
    ],
    (
        "Reuse an ordering mechanism",
        'precondition(larger(3, 8) == 8)\nprecondition(larger("apple", "pear") == "pear")',
        "One implementation preserves Int and String results.",
        "The Comparable requirement makes ordering available without dynamic casts.",
    ),
    (
        "Preserve container element type",
        'let pair = Pair(first: "left", second: "right")\nlet swapped = pair.swapped()\nprecondition(swapped.first == "right" && swapped.second == "left")',
        "Swapping retains the same concrete element type.",
        "The relationship is encoded in the type rather than a runtime convention.",
    ),
    [
        "Identify inferred generic types at every call.",
        "Use larger with Double values and a tie.",
        "Create a generic immutable triple with a rotation operation.",
        "Diagnose calling an unavailable method on an unconstrained T.",
        "State tie behavior and test equal inputs.",
        "Choose generic or existential abstraction for an API that must preserve concrete result type.",
    ],
    "Any discards useful type information. Excessively broad constraints make reuse harder. A generic algorithm still needs domain-specific failure and ordering policies.",
    helpers="func larger<T: Comparable>(_ left: T, _ right: T) -> T { left >= right ? left : right }\nstruct Pair<T> { let first: T; let second: T; func swapped() -> Pair<T> { Pair(first: second, second: first) } }",
)

lesson(
    "Associated types, opaque results and existentials",
    """An associated type names a type relationship inside a protocol. A producer can declare the type of item it produces without fixing that type for every conformer. A generic consumer retains this relationship. Opaque `some` results hide a concrete implementation while preserving one consistent underlying type selected by the function.

Existential `any` values erase more concrete information and can hold different conforming types. These tools solve different problems. Use generics or opaque types when preserving relationships helps the compiler and consumer; use existentials when heterogeneous storage or runtime substitution is the intended feature. Do not choose based only on which spelling makes an error disappear.""",
    "`associatedtype Item` names a conformer-selected type. `P.Item` refers to that relationship in generic code. `some Protocol` hides one concrete return type; `any Protocol` stores an existential value.",
    [
        ("Associated type", "A type selected by each protocol conformance."),
        ("Opaque type", "A hidden but consistent concrete type."),
        ("Type erasure", "Hiding concrete type information behind an interface."),
    ],
    (
        "Retain a produced type",
        "let source = IntegerSource()\nlet value: Int = read(source)\nprecondition(value == 7)",
        "The generic consumer knows the produced value is an Int.",
        "The associated type relationship survives through the generic function.",
    ),
    (
        "Hide representation with an opaque result",
        'let labels = makeLabels()\nprecondition(Array(labels) == ["a", "b"])',
        "The caller uses sequence behavior without naming the concrete array type.",
        "The function selects one underlying result type while exposing its element relationship.",
    ),
    [
        "Trace the associated Item type through read.",
        "Add a String-producing conformance.",
        "Write a generic transformation preserving the producer item type.",
        "Explain why returning unrelated concrete types from one opaque-return function is invalid.",
        "Test empty and nonempty opaque sequences.",
        "Choose opaque output or existential storage for an API and document the preserved relationships.",
    ],
    "Some does not mean any arbitrary type at each return. Existential containers can lose relationships needed by generic operations. Compiler diagnostics often point to a missing type relationship rather than a missing cast.",
    helpers='protocol Producer { associatedtype Item; func produce() -> Item }\nstruct IntegerSource: Producer { func produce() -> Int { 7 } }\nfunc read<P: Producer>(_ producer: P) -> P.Item { producer.produce() }\nfunc makeLabels() -> some Sequence<String> { ["a", "b"] }',
)

lesson(
    "Collection protocols, laziness and algorithm costs",
    """Sequence promises iteration but not necessarily repeatability or efficient indexing. Collection adds reusable traversal with indices, and more specialized protocols add bidirectional or random access. Write an algorithm against the capability it needs rather than assuming every sequence behaves like an array.

Lazy transformations defer work until consumption. This can avoid intermediate storage, but it also delays side effects and errors. Keep transformation closures pure. A slice can retain original indices, so using zero-based offsets indiscriminately breaks otherwise generic code. Complexity belongs to the chosen collection and operation, not merely to its spelling.""",
    "`collection.indices` supplies valid positions. `lazy.map` creates deferred transformation. `Array(sequence)` materializes. reduce summarizes a sequence without requiring indexing.",
    [
        ("Sequence", "A source that can be iterated."),
        ("Collection", "A sequence with reusable traversal and indices."),
        ("Materialization", "Creating stored elements from a sequence."),
    ],
    (
        "Use slice indices honestly",
        "let values = [10, 20, 30, 40]\nlet slice = values[1...2]\nprecondition(slice.startIndex == 1)\nprecondition(slice.map { $0 / 10 } == [2, 3])",
        "The slice starts at index 1 while traversal still produces two elements.",
        "Element count and index origin are different properties.",
    ),
    (
        "Materialize a lazy transformation",
        "let transformed = [1, 2, 3].lazy.filter { $0 > 1 }.map { $0 * 10 }\nprecondition(Array(transformed) == [20, 30])\nprecondition([Int]().reduce(0, +) == 0)",
        "The lazy recipe produces 20 and 30 when consumed.",
        "Pure transformations keep delayed execution understandable and reproducible.",
    ),
    [
        "Predict slice count and startIndex separately.",
        "Traverse the slice using its indices.",
        "Write a generic sum over Sequence where the element type is suitable.",
        "Diagnose indexing a slice from zero to count minus one.",
        "Test an empty slice and a single-pass custom sequence.",
        "Choose lazy or materialized processing for a large input and explain repeatability and memory costs.",
    ],
    "Not every Sequence can be traversed repeatedly. Index movement may be linear. Side effects in lazy closures can run later or more often than a caller expects.",
)

lesson(
    "Throwing functions and explicit result values",
    """Swift errors represent recoverable failure that a caller must acknowledge with try. A throwing function can return its normal type or throw an Error value. Catching belongs at a layer that can recover, translate or report meaningfully. A generic fallback can hide a failed operation as an ordinary empty result.

Result stores success or failure as a value, useful when an outcome must be retained or passed through another API. Optional absence and errors are different: a missing lookup may be expected, while malformed input carries a reason. Preserve those distinctions instead of force-trying external operations.""",
    "`throws` declares failure capability. `try` acknowledges a throwing call. `do/catch` handles errors. Result<Success, Failure> stores an outcome, with Failure conforming to Error.",
    [
        ("Error", "A value describing recoverable failure."),
        ("Throwing function", "A function that can exit through an error path."),
        ("Result", "A stored success-or-failure value."),
    ],
    (
        "Validate before returning",
        'let parsed = try parseQuantity("3")\nprecondition(parsed == 3)\nvar rejected = false\ndo { _ = try parseQuantity("-1") } catch QuantityError.invalid { rejected = true }\nprecondition(rejected)',
        "Three is accepted and a negative quantity is rejected.",
        "Failure carries a domain category instead of masquerading as zero.",
    ),
    (
        "Store an outcome for later inspection",
        'let outcome = Result { try parseQuantity("bad") }\nswitch outcome { case .success: preconditionFailure("invalid input accepted"); case .failure(let error): precondition(error is QuantityError) }',
        "The stored outcome retains a QuantityError.",
        "Result separates when an operation executes from when its outcome is examined.",
    ),
    [
        "Trace the normal and throwing paths.",
        "Distinguish malformed text from negative quantity with separate error cases.",
        "Write a throwing validator for an inventory record.",
        "Diagnose try? used where discarding the error reason loses required evidence.",
        "Test empty, zero and out-of-range input.",
        "Choose Optional, throws or Result for three APIs and explain each semantic distinction.",
    ],
    "Try! turns recoverable failure into a trap. Try? deliberately discards error detail, so use it only when absence is the intended contract. Do not catch assertion failures as ordinary input errors.",
    helpers="enum QuantityError: Error { case invalid }\nfunc parseQuantity(_ text: String) throws -> Int { guard let value = Int(text), value >= 0 else { throw QuantityError.invalid }; return value }",
)

lesson(
    "ARC, weak references and retain cycles",
    """Automatic Reference Counting tracks strong references to class instances. When the last strong owner releases an instance, its lifetime can end. Value types do not participate as independently reference-counted objects in the same way, although they can contain references. ARC manages memory ownership, not file or task completion.

A cycle of strong references can keep objects alive even when the application no longer needs them. A weak reference does not retain its target and becomes nil when that target disappears. An unowned reference asserts a stricter lifetime relationship and can trap if that assertion is wrong. Closure capture lists need the same ownership analysis, especially when an object stores a closure that captures itself.""",
    "`weak var owner: Owner?` is optional and non-retaining. `[weak self]` captures a non-retaining reference for an escaping closure. Identity diagrams make cycles easier to detect than guessing from deinit timing.",
    [
        ("ARC", "Automatic management of strong class-reference counts."),
        ("Weak reference", "A non-owning optional reference that can become nil."),
        ("Retain cycle", "A cycle of strong references preventing release."),
    ],
    (
        "Observe weak lifetime",
        "var owner: Owner? = Owner()\nweak var observer = owner\nprecondition(observer != nil)\nowner = nil\nprecondition(observer == nil)",
        "The weak observer becomes nil after the last strong reference is removed.",
        "The example observes a controlled ownership boundary without retaining the target accidentally.",
    ),
    (
        "Break a parent-child cycle",
        "var parent: Parent? = Parent()\nlet child = Child()\nparent?.child = child\nchild.parent = parent\nweak var observed = parent\nparent = nil\nprecondition(observed == nil && child.parent == nil)",
        "The child survives independently without retaining its parent.",
        "The weak back-reference breaks the ownership cycle while preserving navigation when the parent exists.",
    ),
    [
        "Draw strong and weak arrows in both examples.",
        "Add a temporary second strong owner and predict when the weak observer clears.",
        "Design a weak delegate relationship.",
        "Diagnose an object retaining a closure that strongly captures the same object.",
        "Test a callback after its weak owner has disappeared.",
        "Choose weak or unowned for a relationship and justify the lifetime guarantee required.",
    ],
    "Weak is not a general replacement for ownership. A local strong binding can extend lifetime during observation. ARC does not cancel asynchronous work or close external resources automatically.",
    helpers="final class Owner {}\nfinal class Parent { var child: Child? }\nfinal class Child { weak var parent: Parent? }",
)

lesson(
    "Codable and validated data boundaries",
    """Codable combines encoding and decoding capabilities. The compiler can synthesize conformance for suitable value models, but successful decoding proves only the representational contract. A negative quantity can still decode into an Int. Apply domain validation after structural decoding and before admitting the value to application state.

Schema evolution needs explicit choices about renamed fields, defaults and versions. CodingKeys controls mapping between external names and internal properties. Do not expose internal state merely because automatic synthesis makes it easy. Keep transport models small and separate from resource-owning or secret-bearing objects.""",
    "JSONEncoder produces Data; JSONDecoder reconstructs a Codable type. CodingKeys maps property names. A DecodingError describes a structural mismatch, while domain validation has its own error policy.",
    [
        ("Codable", "The combined encoding and decoding protocol capability."),
        ("Coding key", "A named field in an external representation."),
        ("Schema evolution", "Maintaining meaning as stored formats change."),
    ],
    (
        "Round-trip a value model",
        'let original = Item(name: "pear", quantity: 3)\nlet data = try JSONEncoder().encode(original)\nlet restored = try JSONDecoder().decode(Item.self, from: data)\nprecondition(restored == original)',
        "The modeled fields round-trip through JSON.",
        "Value equality checks the data meaning rather than incidental JSON property ordering.",
    ),
    (
        "Reject a decoded domain violation",
        'let data = Data("{\\"name\\":\\"pear\\",\\"quantity\\":-2}".utf8)\nlet decoded = try JSONDecoder().decode(Item.self, from: data)\nprecondition(!decoded.isValid)\nprecondition(!Item(name: "", quantity: 1).isValid)',
        "Valid JSON can still describe an invalid item.",
        "Structural decoding and domain admission are separate responsibilities.",
    ),
    [
        "State what the round-trip check proves.",
        "Add an optional description field and test missing versus present data.",
        "Write a decoder that validates before returning a trusted item.",
        "Diagnose assuming synthesized Codable enforces business invariants.",
        "Test malformed JSON, missing required fields and unknown fields.",
        "Plan migration of a renamed field without discarding existing saved records.",
    ],
    "JSON key order is not a semantic equality rule. Defaults can hide missing required information. Do not decode directly into a complex object with side effects.",
    helpers="struct Item: Codable, Equatable { let name: String; let quantity: Int; var isValid: Bool { !name.isEmpty && quantity >= 0 } }",
)

lesson(
    "Files, URLs and owned persistence",
    """Foundation represents file locations with URLs as well as path strings. A file URL is distinct from an HTTP URL. Relative locations depend on a working directory, and a worker temporary directory is not the classroom progress store. Keep ownership and persistence scope explicit.

A portable example creates a unique temporary directory, writes a small value, reads it back and removes only that owned directory. Defer places cleanup near acquisition and executes when scope exits, including throwing paths. Durable application storage needs additional policies for atomic replacement, schema migration, backups and errors. A temporary round trip does not prove crash recovery.""",
    "FileManager.default.temporaryDirectory supplies a temporary base. appendingPathComponent constructs a child URL. Data.write and Data(contentsOf:) operate on bytes. defer registers cleanup for the current scope.",
    [
        ("File URL", "A structured location identifying a filesystem resource."),
        ("Defer", "A cleanup action executed when the current scope exits."),
        ("Persistence scope", "The lifetime and location in which data is expected to survive."),
    ],
    (
        "Round-trip in an owned directory",
        'let manager = FileManager.default\nlet root = manager.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)\ntry manager.createDirectory(at: root, withIntermediateDirectories: true)\ndefer { try? manager.removeItem(at: root) }\nlet file = root.appendingPathComponent("note.txt")\nlet expected = Data("café".utf8)\ntry expected.write(to: file)\nlet actual = try Data(contentsOf: file)\nprecondition(actual == expected)',
        "The UTF-8 bytes round-trip in a uniquely owned location.",
        "Random path identity prevents collisions while content and assertions remain deterministic.",
    ),
    (
        "Distinguish file and network locations",
        'let file = URL(fileURLWithPath: "/tmp/example.txt")\nlet remote = URL(string: "https://example.invalid/data")!\nprecondition(file.isFileURL && !remote.isFileURL)',
        "The two URLs carry different location schemes.",
        "A URL is not permission to access its target; the example classifies values without contacting either target.",
    ),
    [
        "Trace acquisition, use and defer cleanup.",
        "Write and read two separate small files under the owned directory.",
        "Persist a Codable value in a temporary file and validate after reading.",
        "Diagnose assuming worker temporary files survive container replacement.",
        "Test empty bytes and a missing file as distinct outcomes.",
        "Design a durable app save with atomic replacement and a recoverable previous version.",
    ],
    "Never remove an arbitrary caller-provided directory. A normalized path does not defeat symlink races. Try? in cleanup intentionally suppresses a secondary error here; production code should record cleanup failure appropriately.",
)

lesson(
    "Dates, calendars and elapsed time",
    """Date represents an instant, independent of how a user sees it. Calendar and time-zone rules translate instants into local components. A fixed offset does not capture an entire region's daylight-saving history. Adding a duration and asking for the next calendar day can therefore answer different questions.

Use fixed instants in tests rather than the current machine clock. ISO 8601 is useful for exchanging timestamps, while localized formatting serves display. For performance measurement, use a monotonic clock rather than wall-clock time, which can be adjusted. Keep the unit of every duration explicit.""",
    "Date(timeIntervalSince1970:) constructs a fixed instant. addingTimeInterval uses seconds. ISO8601DateFormatter translates an exchange representation. Calendar operations require an explicit calendar and time zone for reproducible component reasoning.",
    [
        ("Instant", "A point on the time line."),
        ("Calendar", "Rules mapping instants to civil date components."),
        ("Monotonic clock", "A clock suitable for elapsed time without wall-clock adjustments."),
    ],
    (
        "Measure a fixed duration",
        "let start = Date(timeIntervalSince1970: 0)\nlet end = start.addingTimeInterval(90 * 60)\nprecondition(end.timeIntervalSince(start) == 5400)",
        "The elapsed interval is 5,400 seconds.",
        "Explicit units prevent confusing minutes with the seconds expected by the API.",
    ),
    (
        "Parse equal instants with different offsets",
        'let formatter = ISO8601DateFormatter()\nlet first = formatter.date(from: "2025-01-01T12:00:00+02:00")\nlet second = formatter.date(from: "2025-01-01T10:00:00Z")\nprecondition(first != nil && first == second)',
        "Both strings represent the same instant.",
        "Offset information must be included when comparing wall-clock representations.",
    ),
    [
        "Convert the duration between seconds and minutes.",
        "Add a day-sized duration and explain why this is not a universal next-local-day rule.",
        "Build a report from fixed timestamp fixtures.",
        "Diagnose treating an offset as a complete time-zone identity.",
        "Test an interval crossing midnight and malformed timestamp text.",
        "Design storage, display and duration-measurement policies for an appointment app.",
    ],
    "Date has no inherent display time zone. Locale-sensitive formatting should not be used as an undocumented machine-data contract. Daylight-saving changes can create missing or repeated local times.",
)

lesson(
    "Swift packages and module boundaries",
    """A package describes targets, products and dependencies. A target is a compilation unit with a module boundary; a product exposes something consumers can build or import. Splitting a domain library from an executable lets tests and an app share the same core without duplicating source.

The single-file pad cannot accept Package.swift or install dependencies. The checked-in JourneyCore package is a separate complete project with a library, executable and tests, using only the Swift toolchain. Build it deliberately in a prepared environment. Package success on one platform does not establish Apple UI behavior or every deployment architecture.""",
    "Package.swift declares a tools-version header and target graph. import exposes another module public API. Internal is the usual default access level, while public members define cross-module contracts.",
    [
        ("Package", "A versioned collection of targets and products."),
        ("Target", "A compilation and dependency unit."),
        ("Module", "A namespace and visibility boundary produced by compilation."),
    ],
    (
        "Keep a pure core function",
        "func total(_ values: [Int]) -> Int { values.reduce(0, +) }\nprecondition(total([2, 3]) == 5)\nprecondition(total([]) == 0)",
        "The pure kernel is suitable for a reusable library.",
        "A portable contract can be shared by an executable, tests and a later app adapter.",
    ),
    (
        "Separate presentation from calculation",
        'func render(_ total: Int) -> String { "total=\\(total)" }\nprecondition(render(5) == "total=5")',
        "Presentation is independently testable.",
        "Moving this function into another target requires a deliberate public interface rather than copying implementation text.",
    ),
    [
        "Identify the core and presentation responsibilities.",
        "Build the complete JourneyCore package with swift build.",
        "Run swift test and the journey-demo executable.",
        "Diagnose a symbol that is internal when another module needs public access.",
        "Perform a clean package build using only the lab-owned output directory.",
        "Add a new target only when it creates a useful dependency boundary and document that direction.",
    ],
    "A manifest is not executed by the classroom source pad. Do not assume adding a dependency is offline. Public API choices become compatibility obligations.",
    notes="Use the complete [JourneyCore project](../fixtures/JourneyCore/README.md). It contains real Package.swift, source and test files and no external package dependencies.",
    source="https://www.swift.org/documentation/package-manager/",
)

lesson(
    "Testing behavior with the prepared package",
    """A meaningful test rejects a plausible wrong implementation. Examples should include independently derived expected values, boundaries and a known misconception. Properties such as idempotence can cover a wider family, but they complement concrete expected cases rather than replacing them.

The pad uses precondition for dependency-free executable checks. The JourneyCore package includes XCTest tests available with the prepared Swift toolchain. Swift Testing is another modern test framework and its macro-based API has a distinct project/toolchain requirement. Keep whichever test surface is actually prepared explicit. Unit tests do not prove UI interaction, signing or remote service availability.""",
    "Table-driven checks separate input fixtures from execution. XCTest test methods use XCTAssertEqual and XCTAssertThrowsError in the package. Async tests should await owned work rather than sleep and guess.",
    [
        ("Oracle", "An independent rule deciding correct behavior."),
        ("Regression", "A test retaining evidence of a repaired defect."),
        ("Property", "A relationship expected across a family of inputs."),
    ],
    (
        "Check independently derived cases",
        "let cases = [(-2, 0), (0, 0), (3, 3)]\nfor (input, expected) in cases { precondition(max(0, input) == expected) }",
        "Normal and boundary values satisfy the clamp contract.",
        "Literal expected results are derived from the domain rule rather than a duplicated implementation.",
    ),
    (
        "Catch a plausible wrong boundary",
        "func wrong(_ value: Int) -> Int { value <= 0 ? 1 : value }\nprecondition(wrong(0) != max(0, 0))\nprecondition(max(0, max(0, -4)) == max(0, -4))",
        "The zero case catches the wrong default and clamping is idempotent.",
        "A property adds evidence while the boundary example remains decisive.",
    ),
    [
        "Name a wrong implementation rejected by each fixture.",
        "Add the minimum Int case without unsafe negation.",
        "Add a real JourneyCore test for rejected negative quantity.",
        "Diagnose a test comparing the same function call on both sides.",
        "Test empty, duplicate and malformed inputs separately.",
        "Create a verification plan distinguishing unit, package, UI and device evidence.",
    ],
    "Random tests need reproducible seeds and an oracle. A test that catches its own precondition failure is not valid verification. Avoid narrow elapsed-time assertions on shared machines.",
    notes="Run the checked-in package tests using the commands in [JourneyCore](../fixtures/JourneyCore/README.md). Apple UI tests are a separate later lab.",
)

lesson(
    "Async functions and suspension points",
    """An async function can suspend while waiting for another operation. Suspension is not the same as blocking a thread, and async does not automatically make CPU work parallel. Await marks a place where the current task may pause and other work may run. This boundary matters when shared state can change.

Keep ownership of the asynchronous result explicit. An unstructured task can outlive the scope that created it, while structured child tasks have a parent lifetime. This chapter uses tiny deterministic async functions, preparing for task groups and actors. A returned value proves this fixture completed, not that every future network or storage operation is reliable.""",
    "`async` permits suspension; `await` acknowledges an async call. An async throwing method is called with try await. The entrypoint already supports async, so no semaphore or blocking bridge is needed.",
    [
        ("Suspension point", "A place where a task may pause without holding a thread blocked."),
        ("Task", "A unit of asynchronous work with an outcome and lifetime."),
        ("Structured concurrency", "Child work whose lifetime is bounded by its parent scope."),
    ],
    (
        "Await an asynchronous result",
        "func double(_ value: Int) async -> Int { value * 2 }\nlet result = await double(4)\nprecondition(result == 8)",
        "The awaited result is 8.",
        "The fixture introduces the call boundary without pretending a tiny calculation needs a separate thread.",
    ),
    (
        "Propagate async failure",
        "func validated(_ value: Int) async throws -> Int { guard value >= 0 else { throw AsyncError.invalid }; return value }\nlet accepted = try await validated(3)\nprecondition(accepted == 3)\nvar rejected = false\ndo { _ = try await validated(-1) } catch AsyncError.invalid { rejected = true }\nprecondition(rejected)",
        "The async boundary preserves both the valid result and the domain error.",
        "Suspension capability does not change the requirement to handle failure honestly.",
    ),
    [
        "Distinguish an async declaration from actual parallel execution.",
        "Await two dependent calculations in order.",
        "Write an async adapter that returns a validated domain value.",
        "Diagnose blocking with a semaphore to wait for async code on a constrained executor.",
        "Test a valid and throwing async outcome.",
        "Identify suspension points in an app load operation and explain what state may change around them.",
    ],
    "Async does not promise a background thread. Do not block an executor waiting for work that needs the same executor. Retain and await meaningful results.",
    helpers="enum AsyncError: Error { case invalid }",
)

lesson(
    "Task groups and bounded parallel ownership",
    """A task group creates child tasks whose lifetimes remain inside the group scope. Children may finish in any order, so result collection should not accidentally depend on scheduling. If output ordering matters, include an identity or sort after collection. Structured ownership makes it possible to await all admitted work before returning.

A group is not automatically a concurrency limit. Adding a child for every element of a huge input can overwhelm memory or downstream systems. Bound admission by adding only a limited number and replacing completed work. The fixture uses three tiny tasks and explicitly avoids claiming a timing speedup.""",
    "withTaskGroup creates a scoped group. addTask admits a child. for await consumes completed child results. A child captures only sendable data crossing the concurrency boundary.",
    [
        ("Child task", "Work owned by a structured parent scope."),
        ("Completion order", "The order tasks finish, potentially different from submission."),
        ("Admission limit", "A bound on simultaneously outstanding work."),
    ],
    (
        "Collect results without assuming order",
        "let values = await withTaskGroup(of: Int.self, returning: [Int].self) { group in\n    for value in [1, 2, 3] { group.addTask { value * 2 } }\n    var results: [Int] = []\n    for await result in group { results.append(result) }\n    return results.sorted()\n}\nprecondition(values == [2, 4, 6])",
        "Sorted results are deterministic despite unspecified completion order.",
        "Independent values cross the boundary, and the parent alone mutates the result array.",
    ),
    (
        "Handle an empty group",
        "let count = await withTaskGroup(of: Int.self, returning: Int.self) { group in\n    var total = 0\n    for await value in group { total += value }\n    return total\n}\nprecondition(count == 0)",
        "No admitted children produces the identity result zero.",
        "The empty path needs no special background work or timer.",
    ),
    [
        "Identify who owns each task and the result array.",
        "Attach input indices and reconstruct submission ordering.",
        "Implement bounded admission for a small list with at most two outstanding children.",
        "Diagnose concurrent mutation of a shared result array inside child tasks.",
        "Test empty input and a failing child using a throwing group.",
        "Choose a concurrency bound for an I/O workload and explain its resource basis.",
    ],
    "Group completion order is unspecified. Cancellation is cooperative and does not instantly kill children. Avoid unbounded child creation for large inputs.",
)

lesson(
    "Cancellation and cleanup in asynchronous work",
    """Task cancellation records a request that cooperative code can observe. It does not forcibly stop every instruction. A cancelled task can still return a value if it never checks cancellation. Distinguish a caller no longer wanting a result from the operation having stopped before effects occurred.

Use cancellation checks before admitting expensive work and at meaningful loop boundaries. Cleanup remains necessary on cancellation paths. Do not replay a state-changing request simply because an observer was cancelled; the first operation may have completed. The fixture observes cancellation deterministically without relying on a race between sleep durations.""",
    "Task.isCancelled inspects state and Task.checkCancellation throws CancellationError. A task handle can be cancelled and then awaited to observe its actual completion. Cancellation handlers require careful sendable state ownership.",
    [
        ("Cooperative cancellation", "Work responding to a request to stop."),
        ("CancellationError", "The error signaling acknowledged task cancellation."),
        ("Operation outcome", "The actual result or effect, distinct from observer interest."),
    ],
    (
        "Cancel before observing a check",
        "let task = Task {\n    while !Task.isCancelled { await Task.yield() }\n    do { try Task.checkCancellation(); return false } catch is CancellationError { return true } catch { return false }\n}\ntask.cancel()\nlet acknowledged = await task.value\nprecondition(acknowledged)",
        "The task acknowledges cancellation and its completion is awaited.",
        "The loop observes cancellation state rather than guessing a scheduling delay.",
    ),
    (
        "Cancellation need not prevent a result",
        "let task = Task { 9 }\ntask.cancel()\nlet value = await task.value\nprecondition(value == 9)",
        "This task still returns 9 because its body does not check cancellation.",
        "A cancellation request alone is not proof that an operation failed to execute.",
    ),
    [
        "Separate cancellation request from acknowledged completion.",
        "Add a cancellation check before a simulated state-changing step.",
        "Write a bounded processing loop with cleanup on cancellation.",
        "Diagnose retrying an unknown write merely because its waiter was cancelled.",
        "Test cancellation before work and after an already completed result.",
        "Design a receipt distinguishing success, confirmed cancellation and unknown outcome.",
    ],
    "Polling cancellation in a tight CPU loop without yielding can waste resources. A cancellation handler must not race unsafely with the operation. Preserve result identity when deciding whether replay is safe.",
)

lesson(
    "Actors and serialized state ownership",
    """An actor isolates mutable state so asynchronous callers cannot directly access it without crossing the actor boundary. This prevents many data races by making ownership part of the type system. Actor methods can still contain logical races: when an operation suspends, another task may enter and change state before it resumes.

Keep a state transition synchronous inside the actor whenever possible. If an operation must await external work, revalidate assumptions after suspension or model a reservation explicitly. Actors provide isolation, not an automatic transaction across every await. Sendable describes which values can safely cross concurrency boundaries.""",
    "`actor CounterActor` owns isolated state. Calls from outside use await even when the method body itself does not suspend. Read an actor result into a local value before passing it to precondition, whose autoclosure is synchronous.",
    [
        ("Actor isolation", "Exclusive ownership of actor state under concurrency rules."),
        ("Reentrancy", "Other work entering an actor while an operation is suspended."),
        ("Sendable", "A contract for values safely crossing concurrency boundaries."),
    ],
    (
        "Serialize increments",
        "let counter = CounterActor()\nawait withTaskGroup(of: Void.self) { group in for _ in 0..<20 { group.addTask { await counter.increment() } } }\nlet value = await counter.value\nprecondition(value == 20)",
        "All twenty increments are retained.",
        "The actor owns mutation, while child tasks send requests rather than sharing a writable integer.",
    ),
    (
        "Keep a reservation atomic within the actor",
        "let inventory = InventoryActor(stock: 3)\nlet first = await inventory.reserve(2)\nlet second = await inventory.reserve(2)\nlet remaining = await inventory.stock\nprecondition(first && !second && remaining == 1)",
        "The second reservation is rejected without making stock negative.",
        "The check and update contain no suspension, preserving the invariant as one actor operation.",
    ),
    [
        "Identify every actor-isolated read and write.",
        "Add a read-only snapshot method returning a value type.",
        "Implement a bounded actor-owned queue with explicit admission.",
        "Diagnose checking stock, awaiting another operation and then subtracting without revalidation.",
        "Test zero and excess reservations.",
        "Design a reservation state machine for an operation requiring external I/O before commitment.",
    ],
    "Actors do not make all multi-step workflows transactional. Await inside an invariant-sensitive operation is a reentrancy boundary. Do not use unchecked Sendable merely to silence a real ownership diagnostic.",
    helpers="actor CounterActor { private(set) var value = 0; func increment() { value += 1 } }\nactor InventoryActor { private(set) var stock: Int; init(stock: Int) { self.stock = stock }; func reserve(_ amount: Int) -> Bool { guard amount >= 0 && amount <= stock else { return false }; stock -= amount; return true } }",
)

lesson(
    "Composition project: an actor-owned import ledger",
    """The intermediate project gives one actor ownership of operation identities and accumulated totals. Validating a payload and recording its effect together prevents duplicate application within the actor lifetime. A repeated identity with a changed payload is a conflict, not a legitimate retry.

This is deliberately an in-memory example. Actor isolation proves a concurrency boundary, but it does not provide durable transactions across process restart. A production ledger needs storage that commits the effect and receipt atomically. The distinction between source logic, runtime checks and durable system behavior should remain explicit in the project README.""",
    "An actor dictionary records identity to payload/result. A synchronous actor method validates replay and applies new work without await between its check and update. Errors preserve conflicting requests as failures.",
    [
        ("Idempotency", "Repeated request identity does not duplicate the intended effect."),
        ("Receipt", "A retained description of an operation outcome."),
        ("Conflict", "A reused identity with incompatible meaning."),
    ],
    (
        "Replay without duplicate effect",
        'let ledger = ImportLedger()\nlet first = try await ledger.apply(id: "one", amount: 3)\nlet repeated = try await ledger.apply(id: "one", amount: 3)\nlet total = await ledger.total\nprecondition(first == 3 && repeated == 3 && total == 3)',
        "A repeated operation returns its receipt without applying again.",
        "Identity lookup and state change occur under one actor-owned transition.",
    ),
    (
        "Reject conflicting identity reuse",
        'let ledger = ImportLedger()\n_ = try await ledger.apply(id: "one", amount: 3)\nvar conflict = false\ndo { _ = try await ledger.apply(id: "one", amount: 4) } catch LedgerError.conflict { conflict = true }\nlet total = await ledger.total\nprecondition(conflict && total == 3)',
        "A changed payload is rejected and prior state remains intact.",
        "Reconciliation needs payload identity as well as an operation key.",
    ),
    [
        "Trace effect and receipt for the first and repeated calls.",
        "Apply a second unique identity and predict the total.",
        "Add a read-only receipt lookup that never re-executes work.",
        "Diagnose applying the effect before checking the operation identity.",
        "Test negative payloads and concurrent identical requests.",
        "Design a durable adapter and document what actor isolation alone cannot guarantee.",
    ],
    "An in-memory actor ledger loses its state after restart. Overflow and retention policy remain explicit production requirements. Do not claim exactly-once delivery from a local dictionary.",
    helpers="enum LedgerError: Error { case invalid; case conflict }\nactor ImportLedger { private var records: [String: (Int, Int)] = [:]; private(set) var total = 0; func apply(id: String, amount: Int) throws -> Int { guard !id.isEmpty, amount >= 0 else { throw LedgerError.invalid }; if let old = records[id] { guard old.0 == amount else { throw LedgerError.conflict }; return old.1 }; total += amount; records[id] = (amount, total); return total } }",
)
