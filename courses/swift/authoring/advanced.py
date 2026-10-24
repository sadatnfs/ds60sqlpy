# ruff: noqa: E501
# Long original prose and embedded programs are content, not Python expression layout.
"""Advanced Swift and complete Apple app workflows backed by portable kernels."""

from render import lesson

lesson(
    "Sendable and strict concurrency boundaries",
    """Sendable describes values that can cross concurrency boundaries without introducing unsafe shared mutation. Immutable structs composed of sendable members are a natural fit. A mutable reference type requires a real synchronization or isolation story; adding unchecked Sendable only removes the compiler's protection and transfers responsibility to the programmer.

Swift 6 checking makes many previously implicit assumptions visible. Treat diagnostics as design feedback: identify the owner of each mutable value and the boundary across which it moves. A MainActor-isolated UI model and a background actor can exchange immutable snapshots instead of sharing writable object graphs. This is both a language rule and an architecture technique.""",
    "`struct Snapshot: Sendable` declares a crossing contract. Actor calls and child tasks create concurrency boundaries. Capture immutable values and return results instead of mutating shared containers from several tasks.",
    [
        ("Sendable", "A capability for safely crossing concurrency boundaries."),
        ("Isolation domain", "The context owning access to mutable state."),
        ("Snapshot", "An independent value representing state at one point."),
    ],
    (
        "Send an immutable snapshot",
        'let snapshot = Snapshot(name: "pear", quantity: 3)\nlet task = Task { snapshot.quantity * 2 }\nlet result = await task.value\nprecondition(result == 6)',
        "The task receives immutable value data and returns 6.",
        "No mutable object identity is shared across the boundary.",
    ),
    (
        "Return values to the owner",
        'let result = await withTaskGroup(of: Snapshot.self, returning: [Snapshot].self) { group in\n    group.addTask { Snapshot(name: "b", quantity: 2) }\n    group.addTask { Snapshot(name: "a", quantity: 1) }\n    var snapshots: [Snapshot] = []\n    for await value in group { snapshots.append(value) }\n    return snapshots.sorted { $0.name < $1.name }\n}\nprecondition(result.map(\\.name) == ["a", "b"])',
        "The parent owns result aggregation and sorts it deterministically.",
        "Child tasks produce values instead of concurrently mutating one array.",
    ),
    [
        "Identify the owner of every value crossing a task boundary.",
        "Add another immutable field to the snapshot.",
        "Replace a shared mutable result class with a sendable value result.",
        "Diagnose an unchecked Sendable annotation hiding unsynchronized mutable state.",
        "Test empty snapshots and multiple concurrent producers.",
        "Design data exchange between a UI model and a background actor using immutable snapshots.",
    ],
    "Sendable does not mean every operation is cheap or atomic. Unchecked conformance requires a justified invariant and tests. MainActor protects UI isolation but does not make long CPU work appropriate on that actor.",
    helpers="struct Snapshot: Sendable { let name: String; let quantity: Int }",
)

lesson(
    "AsyncSequence, streams and bounded buffering",
    """AsyncSequence delivers values over time through asynchronous iteration. It can model events, streamed records or incremental results. A consumer awaits each next value instead of requiring the entire sequence immediately. The producer and consumer still need a clear completion and cancellation relationship.

AsyncStream bridges callback-style production into this model. Its buffering policy matters: an unbounded default can retain excessive events when a consumer is slow. A bounded policy can drop values, so the producer must inspect yield results when loss matters. The fixture produces a finite sequence synchronously and then finishes, making the data contract deterministic.""",
    "AsyncStream constructs a stream and exposes a continuation. yield admits an element according to the buffer policy; finish ends production. for await consumes until completion.",
    [
        ("AsyncSequence", "A sequence whose next value can require asynchronous waiting."),
        ("Buffer policy", "A rule for retaining or dropping values awaiting consumption."),
        ("Termination", "The event ending production and releasing owned resources."),
    ],
    (
        "Consume a finite stream",
        "let stream = AsyncStream<Int> { continuation in continuation.yield(2); continuation.yield(3); continuation.finish() }\nvar total = 0\nfor await value in stream { total += value }\nprecondition(total == 5)",
        "The finite stream totals 5 and terminates.",
        "Explicit finish prevents the consumer from waiting forever after the last value.",
    ),
    (
        "Make drop behavior observable",
        "let stream = AsyncStream<Int>(bufferingPolicy: .bufferingNewest(1)) { continuation in continuation.yield(1); continuation.yield(2); continuation.finish() }\nvar values: [Int] = []\nfor await value in stream { values.append(value) }\nprecondition(values == [2])",
        "The newest-one policy retains 2 and drops the older buffered value.",
        "Because production finishes before consumption starts here, the buffer outcome is deterministic.",
    ),
    [
        "Trace production, buffering and completion.",
        "Use bufferingOldest(1) and predict the retained value.",
        "Build a finite event stream with explicit completion ownership.",
        "Diagnose an infinite wait caused by never finishing a finite producer.",
        "Test zero events and a buffer overflow policy.",
        "Choose lossless backpressure or deliberate dropping for a real event source and explain cleanup on cancellation.",
    ],
    "AsyncStream buffering is not automatically backpressure. Ignoring dropped values can silently lose work. A continuation retained forever can keep resources alive after consumers stop.",
)

lesson(
    "Unsafe memory, buffers and scope-limited access",
    """Swift normally protects memory through value semantics, ARC and checked collection access. Unsafe pointer APIs deliberately cross that protection boundary for interoperability and specialized performance work. A pointer is valid only while its owner guarantees storage lifetime and binding. Compiling unsafe code does not prove its memory access is valid.

Prefer scoped buffer APIs that lend a pointer only for a closure. Do not store that pointer or use it after the closure returns. Distinguish initialized elements from allocated capacity, and preserve element alignment and type binding. This lesson uses read-only scoped access to an owned array, keeping the demonstration small enough to inspect fully.""",
    "withUnsafeBufferPointer temporarily borrows contiguous elements. The pointer count states initialized accessible elements. Return a copied result from the closure, never the borrowed pointer itself.",
    [
        ("Pointer", "An address-based view of storage with explicit lifetime obligations."),
        ("Borrowed access", "Temporary access without taking ownership."),
        (
            "Undefined behavior",
            "Behavior outside the guarantees of the language or memory contract.",
        ),
    ],
    (
        "Borrow only within the closure",
        "let values = [2, 3, 4]\nlet total = values.withUnsafeBufferPointer { buffer in buffer.reduce(0, +) }\nprecondition(total == 9)",
        "The result escapes as an integer while the borrowed pointer does not.",
        "Scoped access limits the lifetime reasoning to one visible closure.",
    ),
    (
        "Handle empty storage without dereferencing",
        "let values: [Int] = []\nlet count = values.withUnsafeBufferPointer { buffer in buffer.count }\nprecondition(count == 0)",
        "An empty buffer is valid to inspect by count.",
        "No base-address dereference is needed, avoiding assumptions about a pointer for empty storage.",
    ),
    [
        "Identify the pointer lifetime and the returned owned result.",
        "Compute a maximum with an explicit empty-input policy.",
        "Wrap a scoped read-only buffer operation behind a safe function contract.",
        "Diagnose returning the buffer baseAddress for later use.",
        "Test empty, singleton and multi-element buffers.",
        "Write an interoperability checklist covering ownership, alignment, initialization and error reporting.",
    ],
    "Unsafe does not disable all runtime checks or make an operation faster. Never infer lifetime from a pointer value remaining numerically unchanged. Keep native API ownership documented and avoid unsafe code when safe collections suffice.",
)

lesson(
    "Performance, copy costs and complexity",
    """Performance reasoning begins with the workload and the resource being measured. Array copy-on-write can make assignment cheap until mutation requires unique storage. Repeated front insertion still shifts elements and can dominate runtime regardless of that optimization. A collection's semantic convenience does not imply every operation has the same cost.

Use deterministic operation counts to explain algorithm growth, and use a prepared benchmark for elapsed-time claims. Warmup, optimization, allocation and system load can distort small measurements. Preserve correctness checks when comparing implementations. A faster result that omits validation or changes ordering is not an equivalent implementation.""",
    "Set membership can replace repeated linear searches when an equality index is appropriate. reserveCapacity can reduce reallocations but does not change the algorithmic complexity of shifting elements.",
    [
        ("Complexity", "Growth of resource usage as workload size changes."),
        ("Allocation", "Obtaining storage for values or objects."),
        ("Benchmark equivalence", "Ensuring compared implementations satisfy the same contract."),
    ],
    (
        "Count a linear search",
        "let values = [2, 4, 6, 8]\nvar comparisons = 0\nfor value in values { comparisons += 1; if value == 8 { break } }\nprecondition(comparisons == 4)",
        "The last-element search performs four comparisons.",
        "An exact operation count avoids fragile machine-speed assumptions.",
    ),
    (
        "Build a reusable membership index",
        "let index = Set([2, 4, 6, 8])\nprecondition(index.contains(8) && !index.contains(9))\nprecondition(index.count == 4)",
        "The index preserves four identities and answers membership.",
        "Index construction and storage are costs that should be justified by repeated queries.",
    ),
    [
        "Count comparisons for first, last and absent targets.",
        "Double input size and predict worst-case work.",
        "Compare repeated array scans with one built Set under the same identity policy.",
        "Diagnose a benchmark that excludes index construction for a one-shot query.",
        "Test duplicate inputs and empty workloads.",
        "Write a measurement plan covering workload, correctness, optimization mode and allocation evidence.",
    ],
    "Big-O is a growth model, not an elapsed-time promise. A single stopwatch observation is weak evidence. Avoid optimizing ownership complexity before measuring the real bottleneck.",
)

lesson(
    "Property wrappers and reusable access policy",
    """A property wrapper packages behavior around property storage and access. It can validate, normalize or project a reusable policy, but it should not hide surprising I/O or authorization. The wrappedValue is the property-facing interface; projectedValue can expose related information using dollar-prefixed access.

Wrapper behavior is part of the containing type's semantics. Decide whether invalid assignments are rejected, clamped or represented as an error, and make that choice visible to readers. A clamped value can be appropriate for a display control but inappropriate for financial input where silent correction hides an error.""",
    "`@propertyWrapper` marks a wrapper type. wrappedValue supplies get/set behavior. `@Clamped var level` applies it. A projectedValue is read through `$level` when declared.",
    [
        ("Property wrapper", "Reusable logic around a property access contract."),
        ("Wrapped value", "The value exposed through the decorated property."),
        ("Projection", "Additional wrapper-related information exposed separately."),
    ],
    (
        "Apply a bounded display policy",
        "var control = Control()\ncontrol.level = 12\nprecondition(control.level == 10)\ncontrol.level = -2\nprecondition(control.level == 0)",
        "Assignments are clamped into zero through ten.",
        "The wrapper enforces a deliberate display range at every assignment.",
    ),
    (
        "Retain valid interior values",
        "var control = Control()\ncontrol.level = 4\nprecondition(control.level == 4)\nprecondition(control.$level == 0...10)",
        "A valid interior value is unchanged and the projection exposes the range.",
        "The projected information explains the policy without exposing mutable internal storage.",
    ),
    [
        "Trace initialization and both setter calls.",
        "Change the allowed range and update boundary tests.",
        "Create a wrapper with an explicit normalization policy for a local display field.",
        "Explain why silently clamping a payment amount would be misleading.",
        "Test both endpoints and one value outside each.",
        "Choose a wrapper or explicit validation method based on whether assignment can fail meaningfully.",
    ],
    "A wrapper is not a substitute for validating external input. Hidden side effects make ordinary-looking assignment hard to reason about. Document projection and mutation semantics.",
    helpers="@propertyWrapper struct Clamped { private var value: Int; let range: ClosedRange<Int>; init(wrappedValue: Int, _ range: ClosedRange<Int>) { self.range = range; self.value = min(max(wrappedValue, range.lowerBound), range.upperBound) }; var wrappedValue: Int { get { value } set { value = min(max(newValue, range.lowerBound), range.upperBound) } }; var projectedValue: ClosedRange<Int> { range } }\nstruct Control { @Clamped(0...10) var level = 0 }",
)

lesson(
    "Result builders and declarative composition",
    """A result builder transforms a restricted-looking block of expressions into calls that combine intermediate results. SwiftUI uses this language feature to express view composition, but the feature itself is part of Swift and can be taught without Apple frameworks. Declarative syntax still has ordinary type and control-flow rules underneath.

Build only the operations the small language needs. Supporting conditionals, loops and optionals requires corresponding builder methods. A result builder should make a domain clearer rather than obscure evaluation or failure. The portable fixture constructs a list of report sections, while the later app project uses SwiftUI's own ViewBuilder.""",
    "`@resultBuilder` marks the builder. buildBlock combines expressions and buildOptional handles an if without else. A function parameter annotated with the builder accepts the transformed closure.",
    [
        ("Result builder", "A compile-time transformation for structured expression composition."),
        (
            "Declarative composition",
            "Describing a result structure rather than manual assembly steps.",
        ),
        ("Intermediate result", "A value produced by one expression before combination."),
    ],
    (
        "Compose report sections",
        'let report = sections { "Overview"; "Details" }\nprecondition(report == ["Overview", "Details"])',
        "Two expressions become an ordered array of sections.",
        "The builder supplies the combining mechanism; the block supplies domain content.",
    ),
    (
        "Include a conditional section",
        'let include = true\nlet report = sections { "Overview"; if include { "Diagnostics" } }\nprecondition(report == ["Overview", "Diagnostics"])',
        "The conditional contributes its section when true.",
        "The buildOptional method gives the conditional branch an explicit combination rule.",
    ),
    [
        "Translate the first block into its builder calls.",
        "Set include to false and predict the result.",
        "Build a small report declaration using the existing builder.",
        "Diagnose a loop in a builder that lacks buildArray support.",
        "Test an empty block and a false optional section.",
        "Explain why a domain-specific builder may be clearer or less clear than an ordinary array literal.",
    ],
    "A result builder is not runtime reflection or arbitrary syntax parsing. Type errors can surface inside generated combinations, so reduce the block to a small failing expression. Do not reinvent SwiftUI ViewBuilder for ordinary views.",
    helpers="@resultBuilder enum SectionBuilder { static func buildExpression(_ value: String) -> [String] { [value] }; static func buildBlock(_ components: [String]...) -> [String] { components.flatMap { $0 } }; static func buildOptional(_ component: [String]?) -> [String] { component ?? [] } }\nfunc sections(@SectionBuilder _ content: () -> [String]) -> [String] { content() }",
)

lesson(
    "App architecture: a portable domain core",
    """An app is a set of responsibilities with different lifetimes: domain rules, presentation state, views, persistence and external services. A portable domain core lets Linux tests establish business behavior independently of Apple UI rendering. The app adapter then translates user actions into core operations and renders their outcomes.

The JourneyCore package and JourneyApp fixture implement this separation with a small study planner. A lesson item has stable identity, title and completion state. The core rejects empty titles and duplicate identities. SwiftUI presents and edits those values on Apple platforms. Linux can compile and test the core, but cannot qualify view layout, accessibility or simulator behavior.""",
    "A struct model conforms to Identifiable, Codable, Equatable and Sendable where appropriate. A pure reducer maps a state plus action to a new state. The app owns presentation and storage adapters.",
    [
        ("Domain core", "Portable rules independent of UI frameworks."),
        ("Reducer", "A function computing next state from current state and an action."),
        ("Presentation state", "Values a view needs to explain current application behavior."),
    ],
    (
        "Apply a domain action",
        'let original = PlannerItem(id: "one", title: "Read", completed: false)\nlet changed = toggled(original)\nprecondition(changed.completed && !original.completed)',
        "The transformed item changes completion while retaining the original value.",
        "A pure transition supports undo, testing and separate UI rendering.",
    ),
    (
        "Keep identity stable during edits",
        'let original = PlannerItem(id: "one", title: "Read", completed: false)\nlet changed = toggled(original)\nprecondition(changed.id == original.id && changed.title == original.title)',
        "Completion changes do not manufacture a new identity.",
        "Stable identity lets navigation, persistence and UI reconciliation refer to the same domain item.",
    ),
    [
        "Identify domain and presentation responsibilities.",
        "Add a pure rename operation with nonempty-title validation.",
        "Build and test JourneyCore before opening the Apple app.",
        "Diagnose placing file access directly inside a model property getter.",
        "Test unknown identity and duplicate identity admission.",
        "Draw the dependency direction among core, persistence adapter, view model and SwiftUI views.",
    ],
    "A successful core test does not prove app rendering. Stable identity must survive edits and reloads. Keep domain validation outside UI-only button enablement.",
    helpers="struct PlannerItem: Equatable, Sendable { let id: String; let title: String; var completed: Bool }\nfunc toggled(_ item: PlannerItem) -> PlannerItem { var result = item; result.completed.toggle(); return result }",
    notes="Use [JourneyCore](../fixtures/JourneyCore/README.md) for the complete portable package and [JourneyApp](../fixtures/JourneyApp/README.md) for the real SwiftUI app files and Xcode workflow.",
)

lesson(
    "SwiftUI state, bindings and a single source of truth",
    """SwiftUI describes a view as a function of current state. When relevant state changes, the framework recomputes view descriptions and reconciles presentation. A view value is not a permanent screen controller. State storage and identity determine which information persists across those recomputations.

A binding grants read and write access to state owned elsewhere. It does not create an independent copy. The app fixture uses a MainActor observable model as the owner and passes bindings only where editing is intended. The portable pad demonstrates the value-state transition; the actual @State, @Bindable and @Observable interaction must be built and inspected in Xcode on macOS.""",
    "In the external app, @State retains the model reference, @Observable tracks relevant property access, and @Bindable creates bindings to editable model properties. The Linux kernel models the same single-source rule without importing SwiftUI.",
    [
        ("Source of truth", "The owner whose value defines the current state."),
        ("Binding", "Read/write access to state owned elsewhere."),
        ("View identity", "The continuity SwiftUI uses to associate state with a view position."),
    ],
    (
        "Derive presentation from one state",
        'let state = FormState(title: "Read", completed: false)\nprecondition(state.buttonLabel == "Mark complete")',
        "The label follows the stored completion state.",
        "Derived presentation avoids a second label field that can become stale.",
    ),
    (
        "A state change updates its derived view",
        'var state = FormState(title: "Read", completed: false)\nstate.completed = true\nprecondition(state.buttonLabel == "Mark incomplete")\nprecondition(state.title == "Read")',
        "Changing completion changes the derived label while retaining the title.",
        "The transition has one source of truth and independent fields remain unchanged.",
    ),
    [
        "Identify stored and derived state in the kernel.",
        "Add a derived disabled state for an empty title.",
        "Run JourneyApp and edit a title through its real binding.",
        "Diagnose a child view copying input into unrelated state and losing later parent updates.",
        "Test a title edit, cancellation and return to the list.",
        "Decide whether a piece of state belongs to the view, model or domain core and justify its lifetime.",
    ],
    "A binding is not a cloned value. Recreating a model in a transient view computation can discard edits. UI disablement does not replace domain validation.",
    helpers='struct FormState { var title: String; var completed: Bool; var buttonLabel: String { completed ? "Mark incomplete" : "Mark complete" } }',
    notes="Apple-only project lab: [JourneyApp state and editing workflow](../fixtures/JourneyApp/README.md). Linux verifies the domain kernel only.",
    source="https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app",
)

lesson(
    "Navigation, stable identity and deep-link validation",
    """Navigation is application state, not just an animation. A route should identify a destination with stable data rather than retaining a transient view instance. Typed route values make allowed destinations explicit and easier to test. If an item disappears, the app needs a clear missing-destination state.

A deep link is external input. Parse its scheme, host and path under an explicit allowlist and resolve resource identity through the model. Do not let arbitrary URL text choose a file path or execute a command. The app fixture uses NavigationStack and value-based destinations; the portable example checks route parsing independently of Apple rendering.""",
    "A Hashable Route enum can back a NavigationStack path. URLComponents exposes parsed URL fields. A route parser should return an optional or error for unrecognized shapes.",
    [
        ("Route", "A typed description of an application destination."),
        ("Deep link", "An external address requesting a particular application location."),
        ("Navigation path", "An ordered stack of route values."),
    ],
    (
        "Parse an admitted route",
        'let route = parseRoute("journey://item/one")\nprecondition(route == .item("one"))',
        "The admitted scheme and host resolve to item one.",
        "The parser translates untrusted text into a limited domain route.",
    ),
    (
        "Reject unrelated or incomplete links",
        'precondition(parseRoute("https://example.invalid/one") == nil)\nprecondition(parseRoute("journey://item/") == nil)\nprecondition(parseRoute("journey://delete/one") == nil)',
        "Unrelated schemes, missing identity and unlisted actions are rejected.",
        "A route parser is an allowlist, not a generic command interpreter.",
    ),
    [
        "Trace each URL component into the route decision.",
        "Add a separate explicit overview route.",
        "Run JourneyApp and navigate by stable item identity.",
        "Diagnose navigation keyed by array position after reordering.",
        "Test a missing item identity and an item deleted while its route is open.",
        "Design a restoration format for navigation without storing view instances or private payloads.",
    ],
    "Parsing a URL does not authorize access. Array offsets are unstable identities. Never route arbitrary URL text directly into file access or shell commands.",
    helpers='enum Route: Hashable { case item(String) }\nfunc parseRoute(_ text: String) -> Route? { guard let url = URLComponents(string: text), url.scheme == "journey", url.host == "item", url.query == nil, url.fragment == nil else { return nil }; let parts = url.path.split(separator: "/"); guard parts.count == 1 else { return nil }; return .item(String(parts[0])) }',
    notes="The [JourneyApp project](../fixtures/JourneyApp/README.md) includes a real NavigationStack and missing-item view. URL parsing in the pad is only the portable routing kernel.",
    source="https://developer.apple.com/documentation/swiftui/navigationstack",
)

lesson(
    "App persistence, migrations and recoverable saves",
    """Saving app state is a format and recovery contract. A successful encode does not mean bytes were durably committed. A successful write does not prove the next version can decode them. Include a schema version and define how unknown versions are handled. Never erase a user's existing file merely because decoding fails.

The app fixture stores a small Codable document in its application support directory and uses atomic replacement. On read failure it retains the file, reports the error and avoids an automatic overwrite. The Linux pad exercises the schema boundary with in-memory bytes. Filesystem and crash-recovery behavior need separate project evidence.""",
    "A versioned envelope contains schemaVersion and items. Decode first, then validate the version and domain invariants. Data.write with .atomic requests an atomic replacement strategy for the file operation.",
    [
        ("Schema version", "An identity for the meaning and layout of stored data."),
        ("Migration", "A reviewed transformation from an older format."),
        ("Recovery policy", "How the app retains or restores data after failure."),
    ],
    (
        "Read the supported version",
        'let document = SavedPlan(schemaVersion: 1, titles: ["Read", "Practice"])\nlet data = try JSONEncoder().encode(document)\nlet decoded = try JSONDecoder().decode(SavedPlan.self, from: data)\nprecondition(decoded.schemaVersion == 1 && decoded.titles.count == 2)',
        "The supported envelope round-trips with two titles.",
        "Version and payload are inspected independently after decoding.",
    ),
    (
        "Refuse an unknown future schema",
        'let document = SavedPlan(schemaVersion: 99, titles: ["Keep me"])\nprecondition(!supported(document))\nprecondition(document.titles == ["Keep me"])',
        "The unsupported document is rejected without modifying its payload.",
        "Rejection should preserve recoverable source data rather than silently resetting it.",
    ),
    [
        "Identify the schema and domain validation boundaries.",
        "Add a version-one optional field while preserving old decoding behavior.",
        "Inspect JourneyApp save and load errors with an owned test file.",
        "Diagnose replacing an unreadable saved file with an empty default automatically.",
        "Test empty data, malformed data and an unknown future version.",
        "Design a version-one to version-two migration with backup, rollback and verification steps.",
    ],
    "Atomic replacement is not a universal durability or backup guarantee. Do not store secrets in ordinary preferences or unencrypted example files. A migration must preserve meaning, not only produce parseable JSON.",
    helpers="struct SavedPlan: Codable { let schemaVersion: Int; let titles: [String] }\nfunc supported(_ document: SavedPlan) -> Bool { document.schemaVersion == 1 && document.titles.allSatisfy { !$0.isEmpty } }",
    notes="The actual save/load implementation is in the [JourneyApp project](../fixtures/JourneyApp/README.md). It deliberately retains an unreadable file for recovery.",
)

lesson(
    "Networking, loading states and stale-result protection",
    """A network-backed view needs more states than a Boolean loading flag. Idle, loading, ready and failed states carry different information and should be rendered honestly. Cancellation of an old request can reduce work, but a stale response can still arrive if the operation does not cooperate. A request generation or identity check prevents an older result from overwriting newer intent.

URLSession is a Foundation API with platform differences: Linux networking code requires FoundationNetworking. The ordinary pad uses an injected deterministic data source and a pure acceptance rule, so it contacts no server. The app lab explains where a real transport adapter belongs, with status, size, schema and cancellation checks before admission.""",
    "A request generation increments when intent changes. Accept a result only if its generation still matches current state. A transport protocol can return Data for a validated decoder while keeping the UI model independent of URLSession.",
    [
        ("Loading state", "A model of request progress and result category."),
        ("Stale result", "A response belonging to superseded user intent."),
        ("Transport adapter", "The component responsible for actual network exchange."),
    ],
    (
        "Accept the current request result",
        'var state = LoadState(generation: 2, title: nil)\nstate.accept("new", generation: 2)\nprecondition(state.title == "new")',
        "The matching generation updates current state.",
        "Identity connects a result to the intent that authorized it.",
    ),
    (
        "Ignore a superseded result",
        'var state = LoadState(generation: 2, title: "new")\nstate.accept("old", generation: 1)\nprecondition(state.title == "new")',
        "The stale response cannot overwrite the newer value.",
        "Cancellation alone would not establish this guarantee because an operation may still complete.",
    ),
    [
        "Trace current intent and result identity.",
        "Advance the generation and accept only the new response.",
        "Implement a deterministic fake transport returning success and failure values.",
        "Diagnose an old search response replacing a newer search result.",
        "Test empty data, malformed data, non-success status and cancellation separately in the prepared adapter.",
        "Design a URLSession boundary with explicit FoundationNetworking import on Linux, request timeout, size bound and schema validation.",
    ],
    "An awaited response is not automatically a successful HTTP status. Never assume cancellation prevents all late callbacks. Avoid logging authorization headers or raw private response bodies.",
    helpers="struct LoadState { var generation: Int; var title: String?; mutating func accept(_ value: String, generation candidate: Int) { guard candidate == generation else { return }; title = value } }",
    notes="The [JourneyApp project notes](../fixtures/JourneyApp/README.md) provide the exact seam for a separately prepared network adapter. The default app and pad remain offline.",
    source="https://developer.apple.com/documentation/foundation/urlsession",
)

lesson(
    "Accessibility, localization and inclusive interaction",
    """An app is not complete when it looks correct in one screenshot. Users navigate with keyboards, screen readers, large text, reduced motion and different language conventions. A meaningful control needs an accessible name and state. Color alone cannot communicate completion or error.

Localization separates user-facing text from program identity. Keep stable IDs independent of translated titles, and avoid assembling sentences from fragments whose order may differ across languages. The app fixture uses semantic buttons, text labels, accessibility identifiers for tests and a clear completion label. Real VoiceOver, keyboard and Dynamic Type verification remains an Apple-platform task.""",
    "In SwiftUI, accessibilityLabel and accessibilityValue describe semantics; accessibilityIdentifier is a testing hook, not a spoken label substitute. Localized strings and format styles should preserve plural and locale rules.",
    [
        ("Accessible name", "The label assistive technology uses for a control."),
        ("Dynamic Type", "User-selected text sizing supported by Apple UI systems."),
        ("Localization", "Adapting text and presentation to a language and region."),
    ],
    (
        "Describe state with words",
        'func accessibilityText(title: String, complete: Bool) -> String { "\\(title), \\(complete ? "complete" : "incomplete")" }\nprecondition(accessibilityText(title: "Read", complete: true) == "Read, complete")',
        "The label communicates completion without relying on color.",
        "A textual state remains meaningful when a visual marker is unavailable.",
    ),
    (
        "Keep identity separate from translation",
        'let identity = "lesson-one"\nlet titles = ["en": "Read", "fr": "Lire"]\nprecondition(titles["en"] != titles["fr"])\nprecondition(identity == "lesson-one")',
        "Display text changes while identity remains stable.",
        "Saved work and navigation should not break when a learner changes language.",
    ),
    [
        "Identify which information would be lost without color.",
        "Write an accessible label for an incomplete item and its action.",
        "Run JourneyApp using keyboard navigation and VoiceOver on macOS.",
        "Diagnose using a testing identifier as the only meaningful accessibility label.",
        "Check large text, empty content and long translated titles in the Apple project.",
        "Create a manual accessibility acceptance checklist with concrete observations and retained defects.",
    ],
    "A label should not duplicate an entire surrounding screen. Fixed heights can clip large text. The portable string checks do not establish screen-reader order or keyboard focus behavior.",
    notes="The [JourneyApp acceptance guide](../fixtures/JourneyApp/README.md) includes keyboard, VoiceOver, large-text and reduced-motion observations to record.",
    source="https://developer.apple.com/documentation/swiftui/accessibility",
)

lesson(
    "UIKit and AppKit integration boundaries",
    """SwiftUI can host platform-native views through representable adapters. UIKit serves iOS-family interfaces, while AppKit serves macOS. These frameworks do not exist inside the Linux worker. The adapter translates value-driven SwiftUI updates into an imperative view lifecycle and translates callbacks back into application actions.

A coordinator commonly owns delegate behavior. It must avoid feedback loops where a programmatic update triggers the same callback as a user edit and repeatedly writes state. Keep identity and lifetime explicit, and release delegates or observers when the view is dismantled. The fixture includes actual conditional UIKit and AppKit bridge source for a selectable text view.""",
    "UIViewRepresentable uses makeUIView and updateUIView. NSViewRepresentable has corresponding AppKit methods. A Coordinator bridges delegate callbacks. Compile-time canImport guards select the appropriate platform source.",
    [
        ("Representable adapter", "A SwiftUI bridge to an imperative platform view."),
        ("Coordinator", "An object owning delegate or callback integration."),
        (
            "Feedback loop",
            "An update triggering a callback that repeats the same update indefinitely.",
        ),
    ],
    (
        "Avoid redundant imperative updates",
        'var bridge = TextBridgeState(text: "old", assignments: 0)\nbridge.update("new")\nbridge.update("new")\nprecondition(bridge.text == "new" && bridge.assignments == 1)',
        "The same value is not assigned twice.",
        "A value comparison can prevent unnecessary callback or layout churn at the bridge boundary.",
    ),
    (
        "Retain user changes as actions",
        'var bridge = TextBridgeState(text: "start", assignments: 0)\nbridge.update("edited")\nprecondition(bridge.text == "edited")\nprecondition(bridge.assignments == 1)',
        "The portable kernel exposes a deliberate state transition.",
        "The actual platform delegate must route its edit through the same single-source policy.",
    ),
    [
        "Identify the value-driven and imperative sides of the bridge.",
        "Add a no-op case and verify no extra assignment.",
        "Inspect and build SelectableText.swift in the Apple project.",
        "Diagnose an update callback that writes the same binding recursively.",
        "Test empty text, large text and repeated updates in the platform view.",
        "Document coordinator ownership, delegate cleanup and platform-specific API availability.",
    ],
    "A canImport branch is not evidence that both platforms were tested. UIKit and AppKit lifecycles differ. Avoid retaining transient SwiftUI view values as permanent controller state.",
    helpers="struct TextBridgeState { var text: String; var assignments: Int; mutating func update(_ incoming: String) { guard text != incoming else { return }; text = incoming; assignments += 1 } }",
    notes="The complete [JourneyApp fixture](../fixtures/JourneyApp/README.md) contains `SelectableText.swift` with real UIKit and AppKit representable implementations.",
    source="https://developer.apple.com/documentation/swiftui/uiviewrepresentable",
)

lesson(
    "App tests, simulator evidence and signing",
    """App verification has several layers. Domain tests establish rules. Package builds establish module compilation. UI tests establish navigation and interaction in a selected simulator or device configuration. Signing establishes an installable identity under an Apple development team. None of these steps substitutes for the others.

A simulator build can run without provisioning a physical device, while distribution and device installation introduce team, certificate and entitlement requirements. Keep personal signing identifiers out of the shared fixture. The app project is generated locally from an exact reviewed specification, then the learner selects a team only in their own Xcode environment. Record the scheme, destination and observed tests rather than claiming universal platform acceptance.""",
    "Xcode schemes choose build/test actions and destinations. xcodebuild -list and -showdestinations reveal actual available options. The fixture provides domain tests plus a UI smoke source to add to the generated project targets.",
    [
        ("Scheme", "A named set of Xcode build, test and run actions."),
        ("Simulator", "A prepared Apple-platform execution environment for testing."),
        ("Signing", "Associating an app artifact with a development or distribution identity."),
    ],
    (
        "Separate acceptance categories",
        'let evidence: Set<String> = ["domain-tests", "package-build"]\nprecondition(!evidence.contains("ui-tested"))\nprecondition(!evidence.contains("device-signed"))',
        "Domain and package evidence do not imply UI or device qualification.",
        "A release checklist should retain missing evidence instead of inferring it from a lower layer.",
    ),
    (
        "Require every declared release gate",
        'let required: Set<String> = ["domain-tests", "ui-smoke", "save-reload"]\nlet observed: Set<String> = ["domain-tests", "ui-smoke"]\nprecondition(required.subtracting(observed) == ["save-reload"])',
        "Save/reload remains an explicit incomplete gate.",
        "Set difference is a simple portable model of honest acceptance accounting.",
    ),
    [
        "Explain what each evidence category proves.",
        "Add save/reload evidence only after actually performing it.",
        "Generate JourneyApp, list destinations and run its provided test scheme on an available simulator or macOS destination.",
        "Diagnose using a successful archive build as proof of screen-reader usability.",
        "Test fresh launch, saved-state reload and malformed saved-state recovery.",
        "Prepare a release note listing platform, SDK, destination, test results and remaining device/signing limitations.",
    ],
    "Never commit a personal development team, certificate or provisioning profile. A simulator is not a physical device. Keep test-state cleanup scoped to the app-owned test location.",
    notes="Follow [JourneyApp build and test commands](../fixtures/JourneyApp/README.md). The repository does not claim those Apple-platform commands have run merely because Linux references pass.",
    source="https://developer.apple.com/documentation/xcode/running-your-app-in-simulator-or-on-a-device",
)

lesson(
    "Multiplatform design and deployment contracts",
    """Sharing Swift code does not mean every platform has the same frameworks or user expectations. A domain package can compile on Linux and Apple platforms, while UI adapters differ. Conditional compilation is useful at a narrow boundary; scattering platform checks throughout domain logic makes the core harder to reason about.

Deployment targets state the oldest platform APIs an app promises to support. Runtime availability checks can gate newer functionality, but the fallback must still be useful. Resource paths, permissions and application lifecycle also vary. Treat cross-platform support as a matrix of actual builds and runs, not a claim inferred from the language name.""",
    "#if canImport selects compile-time framework availability. #available guards runtime API availability on Apple platforms. Package platform declarations and Xcode deployment settings are related project contracts.",
    [
        ("Deployment target", "The oldest platform version an artifact intends to support."),
        ("Conditional compilation", "Selecting source at compile time under explicit conditions."),
        ("Platform adapter", "A layer isolating platform-specific mechanisms."),
    ],
    (
        "Keep portable policy independent",
        'func summary(completed: Int, total: Int) -> String { "\\(completed)/\\(total) complete" }\nprecondition(summary(completed: 2, total: 3) == "2/3 complete")',
        "The same domain summary works without a UI framework.",
        "A portable core should not import a platform framework merely to format its basic domain outcome.",
    ),
    (
        "Declare a capability rather than guess",
        'let capabilities = Set(["portable-core", "foundation-files"])\nprecondition(capabilities.contains("portable-core"))\nprecondition(!capabilities.contains("swiftui-linux"))',
        "The Linux capability set does not invent SwiftUI support.",
        "Capability descriptions should follow actual prepared runtime evidence.",
    ),
    [
        "Identify which code belongs in the portable core.",
        "Add a platform-neutral derived statistic.",
        "Build JourneyCore on a prepared Linux Swift environment and separately build JourneyApp on macOS.",
        "Diagnose importing UIKit in a shared domain target.",
        "Test unavailable capabilities with a clear message rather than a broken Run action.",
        "Create a platform support matrix listing compiled, executed and manually inspected surfaces separately.",
    ],
    "CanImport proves a module is available to the compiler, not that every API is available at the deployment target. Do not assume Foundation APIs have identical availability everywhere. Keep unsupported surfaces explicit.",
    notes="The portable [JourneyCore](../fixtures/JourneyCore/README.md) and Apple-only [JourneyApp](../fixtures/JourneyApp/README.md) establish the intended boundary.",
    source="https://www.swift.org/platform-support/",
)

lesson(
    "Capstone: an offline-first study planner",
    """The final project connects a portable domain package, a SwiftUI application, stable navigation, editable state and versioned persistence. It remains offline by default so a learner can inspect every meaningful behavior without credentials or a remote service. The architecture has deliberate extension points for networking and additional data models.

A complete capstone includes evidence and limits. Explain which invariants the Linux kernel establishes, which package tests ran, which Apple destination rendered the UI and how saved-state recovery was checked. Keep an unsuccessful observation visible until it is resolved. Expertise grows through independent extensions and diagnosis, not through copying the final source or declaring every possible app scenario covered.""",
    "A stable item identity connects domain actions, navigation and saved data. A reducer updates values; a MainActor presentation model owns view state; a persistence adapter encodes the versioned document. Each layer has its own test boundary.",
    [
        ("Offline-first", "Core behavior works without a network dependency."),
        ("Acceptance evidence", "Recorded observations establishing a declared requirement."),
        (
            "Extension boundary",
            "A documented place for adding behavior without duplicating core rules.",
        ),
    ],
    (
        "Produce a stable completion summary",
        'let items = [CapstoneItem(id: "a", complete: true), CapstoneItem(id: "b", complete: false)]\nprecondition(items.filter(\\.complete).count == 1)\nprecondition(Set(items.map(\\.id)).count == items.count)',
        "One of two uniquely identified items is complete.",
        "The report checks state and identity rather than only a formatted label.",
    ),
    (
        "Preserve identity across a value update",
        'let original = CapstoneItem(id: "a", complete: false)\nvar changed = original\nchanged.complete = true\nprecondition(changed.id == original.id && !original.complete && changed.complete)',
        "The update retains identity and the prior snapshot.",
        "These are the core semantics needed by undo, navigation and persistence.",
    ),
    [
        "Trace one user action from view through model to domain state.",
        "Add a derived progress summary without duplicating stored completion counts.",
        "Build and test JourneyCore, then run the complete JourneyApp on a prepared Apple destination.",
        "Introduce and repair a stale-binding, duplicate-identity or failed-save defect.",
        "Verify empty state, long titles, duplicate IDs, malformed storage and save/reload.",
        "Deliver a project README with architecture, actual platform evidence, accessibility observations, recovery policy and one independently implemented extension.",
    ],
    "A passing portable reference does not qualify simulator interaction or app signing. Preserve user data when testing failure recovery. Keep scope and evidence honest when adding new frameworks or deployment targets.",
    helpers="struct CapstoneItem: Equatable, Sendable { let id: String; var complete: Bool }",
    notes="Start from the actual [JourneyCore](../fixtures/JourneyCore/README.md) and [JourneyApp](../fixtures/JourneyApp/README.md) project files. The app project includes working list, detail editing, navigation, save/load and platform text-bridge code.",
)
