# ruff: noqa: E501
# Long original prose and embedded programs are content, not Python expression layout.
"""Original Swift foundations with complete portable programs."""

from render import lesson

lesson(
    "A Swift source file and its explicit entrypoint",
    """Swift is a compiled language used for portable tools and for applications built with platform frameworks. The language, its standard library and Apple user-interface frameworks are separate layers. A Linux Swift compiler can execute language and portable Foundation code. It does not provide SwiftUI or an iPhone simulator.

The classroom stages one main.swift file and compiles it in Swift 6 mode. An explicit @main type tells the compiler where execution begins. The wrapper uses an asynchronous throwing main so later lessons can keep the same shape. For now, statements execute in order. A compiler error means the program never reached main; a failed precondition means execution reached a violated assumption.""",
    "`@main` marks the entrypoint type. `struct LessonMain` names that type. `static func main() async throws` declares its entry method; async and throws are explained in later chapters. `let` binds a value that cannot be reassigned. `print` produces visible output.",
    [
        ("Source", "The text submitted to a compiler."),
        ("Entrypoint", "The operation called to begin execution."),
        ("Precondition", "A required condition checked during execution."),
    ],
    (
        "Check before printing",
        'let greeting = "Hello, Swift"\nprecondition(greeting.count == 12)\nprint(greeting)',
        "Hello, Swift appears before the lesson marker.",
        "The check establishes a specific observation before the program claims completion.",
    ),
    (
        "Compute an observable result",
        "let rows = 4\nlet seatsPerRow = 6\nlet seats = rows * seatsPerRow\nprecondition(seats == 24)\nprecondition(seats != rows + seatsPerRow)",
        "The computed seat count is 24.",
        "The second condition rejects the plausible mistake of adding dimensions instead of multiplying them.",
    ),
    [
        "Predict the greeting count before execution.",
        "Change the greeting and independently recount its characters.",
        "Compute the capacity of three shelves holding eight books each.",
        "Remove a closing brace temporarily and classify the failure as compilation.",
        "Check zero shelves and one shelf.",
        "Model a three-level capacity calculation and explain every intermediate value.",
    ],
    "Do not delete a failed precondition to reach the marker. Preserve the first compiler diagnostic before interpreting later errors. The entrypoint wrapper is required by this classroom compile contract.",
)

lesson(
    "Constants, variables and static types",
    """Swift distinguishes a binding that may change from one that may not. `let` prevents reassignment; `var` permits it. Prefer let until a state transition is part of the design. The compiler infers types from context, but inference does not make values dynamically typed. A variable initialized with an Int cannot later become a String.

Conversions are explicit between many numeric types. This makes information-changing boundaries visible. A value being representable in one type does not prove it is valid for a domain. Keep units in names and validation at input boundaries. Later chapters introduce reference types, where a constant reference can still point to a mutable object.""",
    "`let count: Int = 3` gives an explicit type. `var total = 0` infers Int. `Double(count)` converts a numeric value. Swift source normally does not need semicolons at line ends.",
    [
        ("Binding", "A name associated with a value or reference."),
        ("Type inference", "Compiler deduction of a static type from context."),
        ("Conversion", "An explicit change of representation."),
    ],
    (
        "Reassign only mutable state",
        "let perBox = 4\nvar total = 0\ntotal += perBox\ntotal += perBox\nprecondition(total == 8 && perBox == 4)",
        "The accumulator becomes 8 while the fixed amount remains 4.",
        "The code exposes which part is state and which part is a stable input.",
    ),
    (
        "Convert before division",
        "let whole = 7 / 2\nlet fractional = Double(7) / Double(2)\nprecondition(whole == 3)\nprecondition(fractional == 3.5)",
        "Integer division yields 3; floating division yields 3.5.",
        "Converting after integer division would preserve the already truncated result.",
    ),
    [
        "Identify the inferred type of every binding.",
        "Replace an unnecessary var with let and explain why it still compiles.",
        "Compute a mean from an integer total and count using a deliberate conversion.",
        "Diagnose conversion performed after integer division.",
        "Test an exactly divisible and a non-divisible pair.",
        "Choose units and types for a small measurement model.",
    ],
    "Let protects the binding, not necessarily every object reachable from it. Avoid forced conversions at a boundary without validating range. A floating type is not automatically more appropriate for a count.",
)

lesson(
    "Numeric limits and intentional arithmetic",
    """Integer values have bounded ranges. Ordinary overflowing integer arithmetic traps in Swift, while reporting-overflow operations return both a result and an overflow flag. Wrapping operators are explicit and useful for domains such as fixed-width bit arithmetic, but usually wrong for quantities or balances.

Floating-point values approximate many decimal fractions. Compare a result according to a numerical error contract rather than expecting every decimal identity to hold exactly. Decimal can represent base-ten financial quantities more naturally, but rounding and units still require a policy. A type choice does not replace domain reasoning.""",
    "`addingReportingOverflow` returns a tuple with partialValue and overflow. `&+` explicitly wraps. `abs(actual - expected) < tolerance` expresses a simple absolute error bound appropriate only to the stated scale.",
    [
        ("Overflow", "A result outside the representable range."),
        ("Tolerance", "An allowed numerical error under a stated scale."),
        ("Wrapping arithmetic", "Arithmetic modulo the fixed-width representation."),
    ],
    (
        "Observe overflow without crashing",
        "let result = UInt8.max.addingReportingOverflow(1)\nprecondition(result.overflow)\nprecondition(result.partialValue == 0)\nprecondition(UInt8(2).addingReportingOverflow(3).partialValue == 5)",
        "255 plus one reports overflow and a wrapped partial result of zero.",
        "The flag is essential: the partial result alone cannot identify the intended mathematical sum.",
    ),
    (
        "Use a numerical comparison policy",
        'let actual = 0.1 + 0.2\nprecondition(abs(actual - 0.3) < 1e-12)\nlet exact = Decimal(string: "0.1")! + Decimal(string: "0.2")!\nprecondition(exact == Decimal(string: "0.3")!)',
        "The floating result meets the stated tolerance and the decimal fixture retains decimal intent.",
        "The force unwrap is limited to authored literal fixtures known to parse; external text needs conditional handling.",
    ),
    [
        "Predict the overflow flag and partial result.",
        "Repeat the boundary with UInt8 zero minus one using the reporting operation.",
        "Write checked quantity addition that returns an explicit rejected outcome.",
        "Diagnose ignoring the overflow flag.",
        "Compare zero, normal and maximum-range inputs.",
        "Choose a numeric representation and rounding policy for a price calculation.",
    ],
    "A tolerance that hides a unit error is not a numerical policy. Avoid wrapping operators for business totals unless modulo behavior is intended. Never force-unwrap untrusted numeric text.",
)

lesson(
    "Strings, Unicode and collection indices",
    """Swift String models extended grapheme clusters as Characters. A visible character may contain several Unicode scalars or code units. This makes String.count different from UTF-8 byte count. It also explains why arbitrary integer indexing is not the general String interface: moving through variable-width text requires valid String.Index positions.

Text processing must choose its unit. A network payload limit is often measured in bytes, while a user-facing length may mean characters. Unicode normalization and case rules complicate identity. Use the explicit representation needed by the operation and keep machine identifiers separate from human-language display text.""",
    "`text.count` counts Characters. `text.utf8.count` counts bytes. `index(after:)` advances a valid String.Index. Slices produce Substring values that may retain the original storage until converted to String.",
    [
        ("Grapheme cluster", "A user-perceived character assembled from Unicode scalars."),
        ("String.Index", "A valid position in a particular string."),
        ("Substring", "A slice that may share storage with its source."),
    ],
    (
        "Count the right unit",
        'let text = "é"\nprecondition(text.count == 1)\nprecondition(text.utf8.count == 2)\nlet combined = "e\\u{301}"\nprecondition(combined.count == 1 && combined.utf8.count == 3)',
        "Both spellings contain one Character but differ in UTF-8 bytes.",
        "Character count follows grapheme boundaries instead of byte storage.",
    ),
    (
        "Slice with a valid index",
        'let text = "A😀B"\nlet firstEnd = text.index(after: text.startIndex)\nprecondition(String(text[..<firstEnd]) == "A")\nprecondition(String(text[firstEnd...]) == "😀B")',
        "The split preserves the emoji as a complete Character.",
        "A valid index belongs to the source string and respects its representation boundaries.",
    ),
    [
        "Predict Character and byte counts for both accent spellings.",
        "Add an emoji and compare counts again.",
        "Write a function returning the first Character as an optional value.",
        "Diagnose treating a byte offset as a String.Index.",
        "Test empty text and a multi-scalar grapheme.",
        "Design a text-field limit and document whether it counts bytes or visible characters.",
    ],
    "Indices from one string are not arbitrary positions in another. Keeping a small Substring can retain a large source buffer. Case conversion and identity comparison require deliberate language or machine-key policies.",
)

lesson(
    "Optionals and honest absence",
    """An optional represents either a wrapped value or no value. This makes absence part of the type rather than an undocumented sentinel. Int zero can be a real measurement, so it should not also mean missing. Optional binding introduces a nonoptional value only inside the branch where presence has been established.

A force unwrap asserts that absence is impossible and traps if that assertion is wrong. It is suitable for tightly controlled fixture literals but is usually a poor external-input policy. Prefer if let for branching and guard let for an early-exit precondition. A fallback with ?? is valid only when the domain really assigns that replacement meaning.""",
    "`Int?` abbreviates Optional<Int>. `if let value = optional` unwraps on the present branch. `guard let` requires an early exit on failure. `??` selects a fallback only when the optional is nil.",
    [
        ("Optional", "A value that may be present or absent."),
        ("Unwrapping", "Accessing a wrapped value after establishing presence."),
        ("Nil", "The absent optional case."),
    ],
    (
        "Preserve zero as a value",
        'let measured: Int? = 0\nlet missing: Int? = nil\nprecondition(measured != nil && missing == nil)\nif let value = measured { precondition(value == 0) } else { preconditionFailure("present zero") }',
        "A present zero remains distinct from nil.",
        "The branch proves presence before the wrapped integer is used.",
    ),
    (
        "Parse with an absence policy",
        'let valid = Int("42")\nlet invalid = Int("forty-two")\nprecondition(valid == 42 && invalid == nil)\nprecondition((invalid ?? -1) == -1)',
        "Parsing produces an optional and malformed text is absent.",
        "The fallback is an explicit display sentinel in this fixture, not a valid quantity.",
    ),
    [
        "Explain the difference between nil and a wrapped zero.",
        "Replace the display sentinel with an unknown label.",
        "Write a parser accepting only present nonnegative integers.",
        "Diagnose force-unwrapping malformed external text.",
        "Test empty, zero, negative and out-of-range input.",
        "Model an optional measurement whose absence must survive serialization and reporting.",
    ],
    "Optional chaining preserves absence; it does not validate the remaining value. A default chosen too early can erase meaningful missingness. Never silence absence merely to satisfy a compiler diagnostic.",
)

lesson(
    "Branches, switch and exhaustive reasoning",
    """Control flow selects which operations execute. A branch should correspond to a domain distinction that can be explained before reading the code. Swift switch does not implicitly fall through to the next case, and the compiler requires coverage of possible inputs. This helps make state handling deliberate.

Range boundaries remain a source of mistakes. A closed range includes both ends; a half-open range excludes its upper end. Use fixtures exactly at transitions and outside the valid domain. A broad default can satisfy exhaustiveness while still hiding a new state, so prefer explicit enum cases when the domain is finite.""",
    "`if` requires a Bool. `switch` matches cases without implicit fallthrough. `0..<10` excludes ten; `0...10` includes it. A where clause narrows a matched case.",
    [
        ("Exhaustiveness", "Handling every possible input category."),
        ("Closed range", "A range including both endpoints."),
        ("Half-open range", "A range excluding its upper endpoint."),
    ],
    (
        "Classify thresholds",
        'func classify(_ score: Int) -> String { switch score { case 0..<60: return "retry"; case 60...100: return "pass"; default: return "invalid" } }\nprecondition(classify(59) == "retry")\nprecondition(classify(60) == "pass" && classify(101) == "invalid")',
        "59 retries, 60 passes and 101 is invalid.",
        "The ranges express the inclusive boundary and keep out-of-domain values separate.",
    ),
    (
        "Use a guard for a required value",
        'func describe(_ text: String?) -> String { guard let text, !text.isEmpty else { return "missing" }; return "value:\\(text)" }\nprecondition(describe(nil) == "missing")\nprecondition(describe("") == "missing" && describe("x") == "value:x")',
        "The early exit excludes missing and empty values before the valid path.",
        "The unwrapped binding is available after the guard because every failing path has returned.",
    ),
    [
        "Predict each threshold case before running.",
        "Move the pass boundary to 70 and update adjacent tests.",
        "Write a three-way classifier for negative, zero and positive quantities.",
        "Diagnose a closed range used where an exclusive upper bound was intended.",
        "Test both ends of the valid domain and one value beyond each.",
        "Replace a broad default in an enum switch with explicit cases and explain the maintenance benefit.",
    ],
    "A default can hide future cases. Guard must actually exit on failure. Avoid treating every invalid value as the normal else category without a stated policy.",
)

lesson(
    "Loops, invariants and safe traversal",
    """A loop repeats a state transformation. Its invariant explains what remains true before and after every iteration. A termination argument explains why the loop eventually stops. These two ideas make a loop easier to reason about than simply reading each statement repeatedly.

For-in traversal expresses iteration over a sequence. Use enumerated when the traversal offset is useful, but do not assume that an enumerated offset is a valid index for every collection or slice. Arrays use integer indices; other collections may not. Empty input should leave the initial accumulator in a meaningful state.""",
    "`for value in values` traverses elements. `for (offset, value) in values.enumerated()` adds a traversal counter. `break` stops the loop; `continue` skips the remaining body. A while loop needs an explicit progress step.",
    [
        ("Invariant", "A property preserved by every iteration."),
        ("Accumulator", "State summarizing processed input."),
        ("Termination argument", "A reason the loop cannot continue indefinitely."),
    ],
    (
        "Accumulate a total",
        "let values = [2, 4, 6]\nvar total = 0\nfor value in values { total += value }\nprecondition(total == 12)\nprecondition([Int]().reduce(0, +) == 0)",
        "The total is 12 and the empty total is zero.",
        "Before each iteration, total summarizes exactly the values already visited.",
    ),
    (
        "Stop at the first match",
        "let values = [3, 8, 8]\nvar found: Int? = nil\nfor (offset, value) in values.enumerated() { if value == 8 { found = offset; break } }\nprecondition(found == 1)\nprecondition(values.firstIndex(of: 9) == nil)",
        "The first 8 appears at offset 1 and 9 is absent.",
        "The break encodes first-match semantics rather than accidentally returning the last match.",
    ),
    [
        "Write the accumulator trace for every iteration.",
        "Ignore negative values while preserving a stated invariant.",
        "Implement a first-match search with an optional result.",
        "Diagnose a while loop whose progress variable never changes.",
        "Test empty, singleton and repeated-match inputs.",
        "Design a bounded retry loop and explain both its invariant and its stop condition.",
    ],
    "An enumerated offset is not universally a collection index. A not-found sentinel should never be used as an index. Mutating traversal state in several places makes termination difficult to establish.",
)

lesson(
    "Functions, argument labels and value contracts",
    """A function groups a computation behind a contract. Swift distinguishes the argument label read at the call site from the parameter name used inside the body. Labels can make an API read as a clear operation rather than an unexplained list of positional values. Use the underscore label only when the surrounding context already makes the meaning clear.

Ordinary value arguments are passed with value semantics. An inout parameter explicitly grants temporary mutation of the caller value under Swift exclusivity rules. Prefer returned values for pure transformations and use inout when mutation is the actual interface. A function contract should state invalid-input behavior and whether any state changes before failure.""",
    "`func area(width: Int, height: Int) -> Int` exposes labels. `_ value` removes the external label. `inout` in a declaration pairs with `&` at the call site. `return` supplies the result and exits.",
    [
        ("Argument label", "The name used at the call site."),
        ("Parameter", "The local name of an input inside a function."),
        ("Inout", "Explicit temporary mutable access to a caller value."),
    ],
    (
        "Name the dimensions",
        "func area(width: Int, height: Int) -> Int { width * height }\nprecondition(area(width: 3, height: 4) == 12)\nprecondition(area(width: 0, height: 4) == 0)",
        "Labels show which dimension each argument supplies.",
        "Readable call sites reduce accidental parameter swaps and reveal the function purpose.",
    ),
    (
        "Make mutation explicit",
        "func increment(_ value: inout Int) { value += 1 }\nvar count = 4\nincrement(&count)\nprecondition(count == 5)",
        "The caller explicitly grants mutation and observes 5.",
        "The ampersand makes the mutation boundary visible instead of hiding it behind a normal-looking value call.",
    ),
    [
        "Explain each argument label and local parameter name.",
        "Add a depth label for a volume function.",
        "Write a pure function normalizing a quantity without mutating its caller.",
        "Diagnose an inout call missing the ampersand and explain the compiler rule.",
        "Test zero and negative dimensions under a documented validation policy.",
        "Choose return values or inout for an API and justify who owns state changes.",
    ],
    "Labels are part of API usability. Inout access cannot overlap conflicting access to the same storage. Do not use mutation merely to avoid returning a small value.",
)

lesson(
    "Arrays and copy-on-write value semantics",
    """Swift arrays are value types. Assigning an array produces a value that behaves independently when later mutated. The implementation can share backing storage until a write requires separation, a strategy called copy-on-write. The semantic promise is independent values, not a guarantee that every assignment immediately copies all bytes.

An array of class references still contains references as its element values. Copying the array separates its sequence structure but does not clone every referenced object. Keep that distinction in mind when building snapshots or undo history. Capacity is storage preparation and does not change the count of present elements.""",
    "`[Int]` is an array type. append grows logical count; an index replaces an existing element. reserveCapacity prepares storage. ArraySlice may preserve original indices, so use its indices rather than assuming zero.",
    [
        ("Value semantics", "Independent observable values after assignment and mutation."),
        ("Copy-on-write", "Storage sharing until a mutation requires separation."),
        ("Capacity", "Reserved storage distinct from logical count."),
    ],
    (
        "Mutate an independent array value",
        "let original = [1, 2]\nvar changed = original\nchanged.append(3)\nprecondition(original == [1, 2])\nprecondition(changed == [1, 2, 3])",
        "Appending to the copy leaves the original unchanged.",
        "The language contract concerns observable behavior even if storage was initially shared.",
    ),
    (
        "Do not confuse capacity and count",
        "var values: [Int] = []\nvalues.reserveCapacity(20)\nprecondition(values.count == 0)\nvalues.append(7)\nprecondition(values.count == 1 && values[0] == 7)",
        "Reserving twenty slots creates no logical elements.",
        "Capacity is a performance hint, not an index range.",
    ),
    [
        "Predict original and changed arrays after append.",
        "Replace an element in the copy and retain the original.",
        "Build a filtered array without changing the source.",
        "Diagnose indexing a reserved but still empty array.",
        "Test an empty slice and a slice whose startIndex is not zero.",
        "Explain what changes when array elements are mutable class instances.",
    ],
    "Array value semantics do not recursively clone objects. Never assume ArraySlice starts at index zero. Repeated insertions at the front can create quadratic work.",
)

lesson(
    "Dictionaries, sets and stable hashing",
    """A Dictionary associates unique keys with values; a Set stores unique members. Both use Hashable to narrow equality lookup. Equal values must hash consistently. A hash value is not a persistent identifier and should not be saved as an enduring key, since hashing can vary across process runs.

Dictionary lookup returns an optional, preserving the distinction between a missing key and a present zero. Output order is not a business sorting policy. Sort keys explicitly for stable presentation. When designing a custom key, use stable identity fields and avoid changing a key after it has been inserted into hashed storage.""",
    "`[String: Int]` declares a dictionary. `counts[key, default: 0] += 1` inserts a default only for that mutation. Set.insert returns whether an element was newly inserted. sorted establishes presentation order.",
    [
        ("Hashable", "A type providing equality-compatible hashing."),
        ("Key", "The identity used for lookup."),
        ("Set membership", "Presence of an equivalent element without duplicates."),
    ],
    (
        "Preserve absence and zero",
        'let counts = ["pear": 0]\nprecondition(counts["pear"] == 0)\nprecondition(counts["apple"] == nil)',
        "Pear is present with zero and apple is absent.",
        "Optional lookup prevents missing information from being confused with a stored value.",
    ),
    (
        "Deduplicate and order deliberately",
        'var tags: Set<String> = ["red"]\nprecondition(!tags.insert("red").inserted)\nprecondition(tags.insert("blue").inserted)\nprecondition(tags.sorted() == ["blue", "red"])',
        "Duplicate red is not inserted and sorted output is deterministic.",
        "Set semantics establish uniqueness while sorting separately establishes order.",
    ),
    [
        "Explain the optional result of each dictionary lookup.",
        "Count repeated tags using the default-value subscript.",
        "Build a unique sorted list of accepted inventory names.",
        "Diagnose persisting hashValue as a cross-run identifier.",
        "Test missing, present-zero and duplicate keys.",
        "Design a custom Hashable key using only stable identity fields.",
    ],
    "Hash collisions do not mean values are equal; equality resolves them. Dictionary order should not be treated as a report contract. A default subscript can insert values during mutation, so inspect side effects.",
)

lesson(
    "Tuples, enums and associated values",
    """A tuple groups a fixed set of values without introducing a new nominal type. It is useful for local multi-value results, but a named type is clearer when the same concept crosses several APIs. An enum represents one case from a finite set. Associated values attach data relevant only to that case.

Explicit cases prevent impossible combinations such as success=true with an error message and no result. A switch must handle the alternatives. This is a strong foundation for application state machines, parsing results and asynchronous loading state. Add a new case only when it represents a real domain distinction, then review every consumer.""",
    "`(count: Int, rejected: Int)` names tuple components. `enum Outcome { case value(Int); case invalid(String) }` binds case-specific payloads. `case .value(let count)` extracts only the matching payload.",
    [
        ("Tuple", "A fixed grouping of component values."),
        ("Enum", "A type whose value is one declared case."),
        ("Associated value", "Data carried by a particular enum case."),
    ],
    (
        "Return two related counts",
        "let summary = (accepted: 3, rejected: 2)\nprecondition(summary.accepted + summary.rejected == 5)",
        "Named tuple fields expose the accounting relationship.",
        "The grouping is useful locally without requiring an entire class hierarchy.",
    ),
    (
        "Model distinct outcomes",
        'let outcomes: [Outcome] = [.value(4), .invalid("negative")]\nlet rendered = outcomes.map { outcome in switch outcome { case .value(let count): return "count:\\(count)"; case .invalid(let reason): return "error:\\(reason)" } }\nprecondition(rendered == ["count:4", "error:negative"])',
        "Each outcome exposes only its own meaningful payload.",
        "The switch extracts data after establishing the state case.",
    ),
    [
        "Name the meaning of each tuple field.",
        "Add a third accounting field only if its meaning is independent.",
        "Model loading, ready and failed states with an enum.",
        "Diagnose several optional fields that permit contradictory state combinations.",
        "Add a new enum case and inspect the compiler-reported consumers requiring updates.",
        "Choose tuple or named enum/struct for a reusable public API and explain the tradeoff.",
    ],
    "An enum raw value and an associated value solve different problems. A catch-all default can conceal a newly added state. Avoid using tuples so large that their positional relationship becomes obscure.",
    helpers="enum Outcome { case value(Int); case invalid(String) }",
)

lesson(
    "Structures and controlled value mutation",
    """A struct models a value with named properties and operations. Assignment follows value semantics, making independent state snapshots straightforward when its stored members also have appropriate semantics. A mutating method explicitly changes self or its stored properties. Methods without mutating cannot silently alter a value-type instance.

Constructors should establish valid state, and operations should preserve it. Do not expose unrestricted writable fields if they allow callers to bypass the rule. A small value type can be a strong domain boundary, but wrapping a primitive without adding meaning or validation is only extra syntax.""",
    "`struct Inventory` defines a value type. `private(set)` exposes reading but restricts assignment. A `mutating func` may update stored state. An initializer can reject invalid input with a throwing or failable contract in later chapters.",
    [
        ("Struct", "A nominal value type."),
        ("Mutating method", "An operation explicitly allowed to modify a value."),
        ("Encapsulation", "Controlling changes through a meaningful interface."),
    ],
    (
        "Keep copied value state independent",
        "var first = Inventory(stock: 5)\nvar second = first\nprecondition(second.reserve(2))\nprecondition(first.stock == 5 && second.stock == 3)\nprecondition(first.reserve(0))",
        "Reserving from the copied inventory does not change the original.",
        "The struct contains value state and its mutation is explicit.",
    ),
    (
        "Reject without partial mutation",
        "var inventory = Inventory(stock: 3)\nprecondition(!inventory.reserve(4))\nprecondition(!inventory.reserve(-1))\nprecondition(inventory.stock == 3)",
        "Rejected requests retain the previous valid stock.",
        "Checking every rejection condition before subtraction preserves failure atomicity.",
    ),
    [
        "Trace both inventory copies through reservation.",
        "Add a validated restock operation.",
        "Build a bounded counter with private mutation.",
        "Diagnose subtracting stock before checking the requested amount.",
        "Test zero, exact-stock and excess reservations.",
        "Choose a value model for an editable form and explain how cancel can restore an earlier snapshot.",
    ],
    "A struct can contain shared class references. Private setters are useful only when methods enforce invariants. The public memberwise initializer in a small fixture is not a substitute for validating external state.",
    helpers="struct Inventory { private(set) var stock: Int; mutating func reserve(_ amount: Int) -> Bool { guard amount >= 0, amount <= stock else { return false }; stock -= amount; return true } }",
)

lesson(
    "Classes, identity and shared state",
    """A class models reference identity. Assigning a class instance copies a reference, so both names can observe the same mutation. This is useful for shared coordinators and resources whose identity matters, but it makes ownership and lifetime more demanding. A let binding prevents replacing the reference while still permitting mutations allowed by the object.

Inheritance lets a subclass reuse or refine behavior, but a subclass must preserve the expectations of callers using the base type. Prefer composition when the relationship is collaboration rather than a true substitutable specialization. Mark a class final when subclassing is not part of its intended contract.""",
    "`final class Counter` declares a reference type without subclasses. `===` compares object identity, while `==` requires an Equatable meaning. `let reference` can still call a mutating object method.",
    [
        ("Reference identity", "The identity of one shared object instance."),
        ("Final class", "A class that cannot be subclassed."),
        ("Composition", "Building behavior by collaborating with contained objects."),
    ],
    (
        "Observe shared identity",
        "let first = Counter()\nlet second = first\nsecond.increment()\nprecondition(first.value == 1)\nprecondition(first === second)",
        "Both names observe the same increment.",
        "The copied reference still identifies one object, even though both bindings are constant.",
    ),
    (
        "Equal state need not mean identity",
        "let first = Counter()\nlet second = Counter()\nprecondition(first.value == second.value)\nprecondition(first !== second)",
        "Two fresh counters have equal state but distinct identities.",
        "Object identity answers a different question from comparing a property value.",
    ),
    [
        "Draw references before and after assignment.",
        "Create a separate object and mutate only one.",
        "Choose class or struct for a shared connection coordinator and a coordinate value.",
        "Diagnose expecting class assignment to create an independent snapshot.",
        "Test equal property values on distinct objects.",
        "Explain whether a shared class needs synchronization before use from concurrent tasks.",
    ],
    "Let does not make a referenced object deeply immutable. Reference semantics do not imply thread safety. Inheritance is not a general-purpose code reuse requirement.",
    helpers="final class Counter { private(set) var value = 0; func increment() { value += 1 } }",
)

lesson(
    "Properties, observers and derived state",
    """A stored property retains data; a computed property derives a value from other state. Prefer deriving cheap dependent values instead of storing duplicates that can disagree. A property observer reacts to a stored-value change but should not become an invisible substitute for a clear domain operation.

Computed setters translate an external representation back into stored state. That translation may lose information, so document it. Access control can permit reading without external writing. Property wrappers later package reusable access behavior, but start by understanding the plain getter and setter contract.""",
    "`var area: Int { width * height }` computes a value. `get` and `set` define two-way access; newValue names the assigned value. didSet observes assignments after the new value is stored.",
    [
        ("Stored property", "A field retaining state."),
        ("Computed property", "A value derived on access."),
        ("Observer", "Code invoked around a stored-property change."),
    ],
    (
        "Derive instead of duplicating",
        "var rectangle = Rectangle(width: 3, height: 4)\nprecondition(rectangle.area == 12)\nrectangle.width = 5\nprecondition(rectangle.area == 20)",
        "Area changes with width without a separately updated area field.",
        "One source of truth prevents stale duplicated state.",
    ),
    (
        "Expose a conversion property",
        "var temperature = Temperature(celsius: 0)\nprecondition(temperature.fahrenheit == 32)\ntemperature.fahrenheit = 212\nprecondition(abs(temperature.celsius - 100) < 1e-9)",
        "The getter and setter translate between temperature scales.",
        "A computed property can expose a convenient representation while retaining one stored unit.",
    ),
    [
        "Trace which properties are stored and which are derived.",
        "Add a computed rectangle perimeter.",
        "Build a value model with one stored unit and a documented converted view.",
        "Diagnose a separately stored area that is not updated after width changes.",
        "Test zero and a non-integer conversion case.",
        "Choose an explicit method instead of a setter for a state change with validation and failure.",
    ],
    "Expensive computed properties can surprise callers who expect cheap access. Observers can hide cascading side effects. Avoid duplicating state unless there is a measured caching need and invalidation policy.",
    helpers="struct Rectangle { var width: Int; var height: Int; var area: Int { width * height } }\nstruct Temperature { var celsius: Double; var fahrenheit: Double { get { celsius * 9 / 5 + 32 } set { celsius = (newValue - 32) * 5 / 9 } } }",
)

lesson(
    "Closures, captures and transformation pipelines",
    """A closure is executable behavior that can be passed as a value. It can capture surrounding variables, which lets it remember context but can also create surprising mutation or lifetime relationships. Swift capture lists can copy a value at closure creation or weaken a reference, depending on the declared policy.

Map transforms each element while filter selects elements. These operations express intent when the closure remains small and clear. Avoid compressing a complex domain algorithm into a chain whose intermediate states nobody can inspect. Name important transformations and preserve a traceable failure boundary.""",
    "`{ value in value * 2 }` is a closure. `$0` abbreviates its first argument. A capture list such as `[factor]` captures the current value. Function types use `(Input) -> Output`.",
    [
        ("Closure", "Callable behavior that may carry surrounding context."),
        ("Capture list", "An explicit policy for captured values or references."),
        ("Higher-order function", "A function that accepts or returns functions."),
    ],
    (
        "Transform a sequence",
        "let values = [1, 2, 3]\nlet doubled = values.map { value in value * 2 }\nprecondition(doubled == [2, 4, 6])\nprecondition(values == [1, 2, 3])",
        "Map creates transformed values while retaining the original array.",
        "The transformation is pure and its element-to-element relationship is visible.",
    ),
    (
        "Freeze a captured value deliberately",
        "var factor = 2\nlet scale = { [factor] (value: Int) in value * factor }\nfactor = 5\nprecondition(scale(3) == 6 && factor == 5)",
        "The explicit capture list retains factor 2 for the closure.",
        "This differs from a closure observing a mutable captured variable later.",
    ),
    [
        "Predict the mapped result and unchanged source.",
        "Filter even numbers before mapping.",
        "Write a function accepting a transformation closure.",
        "Diagnose a closure whose captured mutable state changes before later execution.",
        "Test empty arrays and a closure that returns an optional.",
        "Choose a named function or closure for a reusable domain transformation and explain readability and capture policy.",
    ],
    "An escaping closure can outlive its creating scope. Capturing self strongly can create a retain cycle, covered in ARC. A short expression is not automatically clearer than a named intermediate.",
)

lesson(
    "Foundation project: an honest inventory importer",
    """A first useful Swift project combines optional parsing, value models, loops and deterministic reporting. The critical boundary is admission: malformed or negative quantities must not become accepted zero values. A report should separately account for valid quantities and rejected records.

The fixture uses in-memory lines and produces a value result, so it runs offline and is easy to test. External file loading can be added later as an adapter. Preserve a clear contract for duplicate names and ordering. The same small project will return in later lessons with Codable, async ownership and app presentation.""",
    "Split creates field substrings; convert them deliberately when storing long-lived names. Int parsing returns an optional. Dictionary default mutation accumulates admitted duplicates. sorted fixes presentation order.",
    [
        ("Admission", "The decision to accept a record into domain processing."),
        ("Aggregation", "Combining accepted values under shared keys."),
        ("Rejection evidence", "A retained description or count of excluded inputs."),
    ],
    (
        "Combine repeated valid names",
        'let result = importRows(["pear,2", "apple,3", "pear,4"])\nprecondition(result.counts == ["pear": 6, "apple": 3])\nprecondition(result.rejected == 0)',
        "Pear totals 6 and apple totals 3.",
        "Duplicate names are deliberately accumulated after validation.",
    ),
    (
        "Keep rejection separate from zero",
        'let result = importRows(["pear,0", "bad", "apple,-1", "pear,no"])\nprecondition(result.counts == ["pear": 0])\nprecondition(result.rejected == 3)\nprecondition(importRows([]).counts.isEmpty)',
        "The valid zero remains present while three records are rejected.",
        "This result preserves the difference between accepted zero, absence and invalid input.",
    ),
    [
        "Trace each line through field count, name and quantity checks.",
        "Add a valid duplicate and predict the new aggregate.",
        "Produce a sorted text report with accepted totals and rejected count.",
        "Diagnose replacing failed Int parsing with zero.",
        "Test empty names, extra fields, zero and an empty input list.",
        "Design a reusable result that retains safe line-specific reasons without storing raw sensitive input.",
    ],
    "Check field count before indexing. String splitting can omit empty fields unless configured, so this fixture preserves them deliberately. Production totals also need an overflow policy.",
    helpers='func importRows(_ lines: [String]) -> (counts: [String: Int], rejected: Int) { var counts: [String: Int] = [:]; var rejected = 0; for line in lines { let fields = line.split(separator: ",", omittingEmptySubsequences: false); guard fields.count == 2, !fields[0].isEmpty, let quantity = Int(fields[1]), quantity >= 0 else { rejected += 1; continue }; counts[String(fields[0]), default: 0] += quantity }; return (counts, rejected) }',
)
