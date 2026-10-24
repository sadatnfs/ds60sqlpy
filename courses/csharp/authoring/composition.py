# ruff: noqa: E501
# Long original prose and embedded programs are content, not Python expression layout.
"""Original C# composition, data boundaries and asynchronous work."""

from render import lesson

lesson(
    "Interfaces and substitutable behavior",
    """An interface states what a consumer may ask a component to do. It does not promise that every implementation has the same internal representation. A useful interface captures a stable responsibility: calculating a price, reading a record or producing a time value. Interfaces invented for every class can add indirection without improving the design.

Substitution is behavioral. Two implementations with the same method signature can still disagree about nulls, errors or units. Write those contracts and test the consumer with more than one implementation. This is also the beginning of dependency injection: a caller supplies the collaborator instead of letting the consumer construct an invisible global dependency.""",
    "`interface IRate` declares a method contract. A class implements that interface and supplies the method body. A variable typed as the interface exposes the contract, while dynamic dispatch chooses the implementation.",
    [
        ("Interface", "A named behavioral contract."),
        ("Substitution", "Using an implementation without breaking consumer expectations."),
        ("Dependency injection", "Supplying a collaborator from outside the consumer."),
    ],
    (
        "Use a declared contract",
        'IRate rate = new FlatRate(3);\nCheck(rate.Cost(4) == 12, "flat rate");\nCheck(Total(rate, 0) == 0, "consumer uses contract");',
        "Four units cost 12 and zero units cost zero.",
        "The consumer depends on the interface rather than the concrete class.",
    ),
    (
        "Change policy without changing the consumer",
        'IRate rate = new CappedRate(3, 10);\nCheck(Total(rate, 4) == 10, "capped policy");\nCheck(Total(new FlatRate(3), 4) == 12, "same consumer, different policy");',
        "The same consumer applies a capped or uncapped policy.",
        "An implementation can change the pricing rule while preserving units and accepted inputs.",
    ),
    [
        "Trace the interface call to the selected implementation.",
        "Add a second flat rate and keep Total unchanged.",
        "Define a small interface for a deterministic label formatter.",
        "Diagnose an implementation returning cents where the contract requires whole currency units.",
        "Test zero and a value exactly at the cap.",
        "Choose one dependency worth injecting in the inventory importer and explain the testing benefit.",
    ],
    "Identical signatures do not imply compatible semantics. Avoid interfaces that expose every private implementation detail. Validate domain ranges consistently across implementations.",
    helpers="public interface IRate { int Cost(int units); }\npublic sealed record FlatRate(int Price) : IRate { public int Cost(int units) => checked(Price * units); }\npublic sealed record CappedRate(int Price, int Cap) : IRate { public int Cost(int units) => Math.Min(checked(Price * units), Cap); }\npublic static int Total(IRate rate, int units) => rate.Cost(units);",
)

lesson(
    "Generics and constraints that express capabilities",
    """Generics let an algorithm or container retain a type relationship without copying source for each element type. A List<int> cannot accidentally accept text because the element relationship is checked by the compiler. This differs from storing everything as object and discovering type mistakes later through casts.

An unconstrained type parameter supports only operations valid for every possible type. Constraints declare additional capabilities, such as comparison or a required interface. The constraint should express what the algorithm really needs. A comparable type supports ordering, but the algorithm must still specify what happens for an empty sequence and whether ties preserve the first value.""",
    "`T` names a type parameter. `where T : IComparable<T>` makes CompareTo available. The method call can infer T from its arguments. Return types preserve the relationship to the input type.",
    [
        ("Type parameter", "A placeholder for a compile-time type."),
        ("Constraint", "A requirement on admissible type arguments."),
        ("Type safety", "Rejecting incompatible operations before execution."),
    ],
    (
        "Retain the element type",
        'int larger = Max(4, 9);\nstring later = Max("apple", "pear");\nCheck(larger == 9 && later == "pear", "generic comparison");',
        "The same method returns an int or a string without object casts.",
        "The constraint guarantees comparison while the generic return preserves the concrete type.",
    ),
    (
        "Preserve a generic relationship",
        'var pair = new Pair<string>("left", "right");\nCheck(pair.Swap() == new Pair<string>("right", "left"), "swapped pair");\nCheck(Max(5, 5) == 5, "tie case");',
        "Swap preserves the element type, and a tie remains a valid value.",
        "A generic data model encodes relationships between fields independently of the values used.",
    ),
    [
        "Predict the inferred type at each Max call.",
        "Use Max with decimal values.",
        "Create a generic immutable three-element container.",
        "Explain why an unconstrained T cannot safely call Length.",
        "Test equal values and document whether the first or second object is returned on a tie.",
        "Design a generic helper with the smallest useful capability constraint.",
    ],
    "Adding a class constraint does not make arbitrary methods available. Avoid converting to object merely to escape a compiler error. String ordering may require a comparer for culture-independent business behavior.",
    helpers="public static T Max<T>(T left, T right) where T : IComparable<T> => left.CompareTo(right) >= 0 ? left : right;\npublic record Pair<T>(T First, T Second) { public Pair<T> Swap() => new(Second, First); }",
)

lesson(
    "Delegates, closures and events",
    """A delegate is a typed reference to callable behavior. Passing behavior lets a reusable algorithm vary one decision, such as filtering or transformation, while keeping traversal unchanged. A closure also carries access to variables from its surrounding scope. It captures the variable relationship, which can make later mutations visible when the function eventually executes.

Events build a publish-and-subscribe boundary. The publisher controls when to raise an event; subscribers supply reactions. Subscriptions also create reference relationships and lifetime obligations. A long-lived publisher can retain subscribers unless they unsubscribe. Start with short, deterministic delegate examples before adding event-driven application lifetime.""",
    "`Func<int,int>` represents a callable taking int and returning int. `x => x * factor` is a lambda. An event uses `+=` to subscribe and `-=` to remove the same handler instance.",
    [
        ("Delegate", "A typed callable reference."),
        ("Closure", "A function together with captured surrounding variables."),
        ("Subscription", "A registered callback relationship."),
    ],
    (
        "A closure observes its captured variable",
        'int factor = 2;\nFunc<int, int> scale = value => value * factor;\nCheck(scale(3) == 6, "initial capture");\nfactor = 4;\nCheck(scale(3) == 12, "capture is not frozen");',
        "Changing factor changes later calls through the closure.",
        "The closure refers to the variable, not a permanently copied value from creation time.",
    ),
    (
        "Manage an event subscription",
        'var source = new Signal();\nint calls = 0;\nEventHandler handler = (_, _) => calls++;\nsource.Raised += handler; source.Emit();\nsource.Raised -= handler; source.Emit();\nCheck(calls == 1, "unsubscribe ends observation");',
        "Only the first emission reaches the removed handler.",
        "Keeping the handler reference makes unsubscription precise and prevents a lingering callback.",
    ),
    [
        "Predict both scale results before running.",
        "Capture a separate local snapshot and compare its behavior after factor changes.",
        "Write a transformation method accepting Func<int,int>.",
        "Diagnose unsubscribing with a newly created lambda instead of the subscribed delegate.",
        "Test no subscribers and two subscribers.",
        "Design ownership for subscriptions in a screen or service that can be disposed.",
    ],
    "Closure capture can retain large objects or unexpected mutable state. Event handlers should avoid hiding failures. A new lambda with similar source is not necessarily the same delegate needed for unsubscription.",
    helpers="public sealed class Signal { public event EventHandler? Raised; public void Emit() => Raised?.Invoke(this, EventArgs.Empty); }",
)

lesson(
    "LINQ, deferred execution and materialization",
    """Language Integrated Query expresses sequence transformations such as filtering, projection and ordering. Many LINQ operators produce a recipe rather than immediately executing it. Enumeration runs that recipe. If the source changes before enumeration, the result can change too. This timing is part of the semantics, not an incidental optimization.

Materialization with ToArray or ToList executes a query and stores its current result. It consumes memory but creates a useful snapshot boundary. Repeatedly enumerating an expensive or stateful source can repeat work or observe different data. Decide whether the consumer needs a live recipe, a one-pass stream or a stable materialized result.""",
    "`Where` keeps matching elements; `Select` transforms each element. `OrderBy` chooses ordering. `ToArray` materializes. Lambdas used by deferred operators run during enumeration, so avoid hidden side effects.",
    [
        ("Deferred execution", "Work performed when a sequence is enumerated."),
        ("Projection", "Transforming each selected element."),
        ("Materialization", "Executing and storing a sequence result."),
    ],
    (
        "Observe query timing",
        'var values = new List<int> { 1, 2 };\nvar query = values.Where(value => value > 1);\nvalues.Add(3);\nCheck(query.SequenceEqual(new[] { 2, 3 }), "query sees later source state");',
        "The deferred query sees the subsequently appended 3.",
        "Constructing Where does not copy the source values.",
    ),
    (
        "Capture a stable result",
        'var values = new List<int> { 1, 2 };\nint[] snapshot = values.Where(value => value > 1).ToArray();\nvalues.Add(3);\nCheck(snapshot.SequenceEqual(new[] { 2 }), "snapshot remains stable");\nCheck(values.Select(value => value * 10).ToArray().Length == 3, "projection count");',
        "The earlier snapshot contains only 2 while a new projection sees three values.",
        "Materialization creates a deliberate temporal boundary while preserving the original list separately.",
    ),
    [
        "Predict whether adding an item before enumeration affects query and snapshot.",
        "Add a projection from integers to labeled strings.",
        "Build a deterministic report selecting, transforming and ordering records.",
        "Diagnose a query with a side-effect counter enumerated twice.",
        "Test empty input and a filter matching no rows.",
        "Choose streaming or materialization for a large import and explain memory and repeatability tradeoffs.",
    ],
    "LINQ syntax does not imply database execution. IEnumerable and IQueryable have different providers and translation boundaries. A deferred query can also fail later than the line that constructed it.",
)

lesson(
    "Grouping, joins and data grain",
    """Aggregation changes the grain of data. A row-per-event input can become a row-per-category result. State that grain before writing GroupBy so the result keys and totals have a meaning. Joining two sequences can multiply rows when keys are duplicated. This is a modeling issue that appears in LINQ just as it does in SQL.

An inner join drops keys with no partner. A left join needs an explicit absence policy. Before trusting a total after a join, inspect key uniqueness and count the expected matches. A tiny fixture with duplicate keys reveals accidental multiplication far more clearly than a large realistic dataset.""",
    "`GroupBy(keySelector)` returns groups with Key and enumerable members. `Join` uses one key selector per side. A grouped lookup such as ToLookup preserves all matches, while ToDictionary requires unique keys.",
    [
        ("Grain", "What one row or result item represents."),
        ("Cardinality", "The number of records or matches."),
        ("Join key", "The identity relating two datasets."),
    ],
    (
        "Aggregate at a declared grain",
        'var rows = new[] { (Kind: "a", Amount: 2), (Kind: "a", Amount: 3), (Kind: "b", Amount: 4) };\nvar totals = rows.GroupBy(row => row.Kind).ToDictionary(group => group.Key, group => group.Sum(row => row.Amount));\nCheck(totals["a"] == 5 && totals["b"] == 4, "one total per kind");',
        "Three event rows become two category totals.",
        "Grouping changes grain while preserving the sum across all groups.",
    ),
    (
        "Expose duplicate-key multiplication",
        'var left = new[] { (Key: 1, Label: "L") };\nvar right = new[] { (Key: 1, Value: "x"), (Key: 1, Value: "y") };\nvar joined = left.Join(right, item => item.Key, item => item.Key, (a, b) => a.Label + b.Value).ToArray();\nCheck(joined.SequenceEqual(new[] { "Lx", "Ly" }), "two right matches");',
        "One left row becomes two joined rows.",
        "A key relationship does not imply one-to-one cardinality. Validate uniqueness if the domain requires exactly one match.",
    ),
    [
        "State the input and output grain for each example.",
        "Add a third category and verify total conservation.",
        "Build a report joining unique item metadata to item totals.",
        "Diagnose a doubled total caused by duplicate metadata keys.",
        "Test an unmatched key and choose an explicit handling policy.",
        "Design checks that distinguish one-to-one, one-to-many and many-to-many joins before aggregation.",
    ],
    "Aggregating after an unintended many-to-many join can inflate totals. ToDictionary throws on duplicate keys rather than choosing a winner. Sorting is needed when presentation order is part of the contract.",
)

lesson(
    "Iterators and lazy sequence contracts",
    """An iterator describes a sequence whose values are produced as the consumer asks for them. It can avoid materializing a large collection and can stop work when the consumer stops early. `yield return` pauses the iterator with its local state retained; the next request resumes it. This is different from returning a fully constructed list.

Lazy code shifts both work and some errors into enumeration. If argument validation must happen at the call site, place it outside the iterator body and return a nested iterator. Resource-owning iterators must also release resources when enumeration is abandoned. Consumers using foreach receive disposal behavior; custom enumerator handling must preserve it.""",
    "`IEnumerable<int>` exposes an iterable sequence. `yield return value` supplies one element and suspends. A nested local iterator separates immediate argument validation from delayed generation.",
    [
        ("Iterator", "A stateful producer of successive values."),
        ("Enumeration", "Repeatedly requesting the next element."),
        ("Laziness", "Deferring work until a consumer demands it."),
    ],
    (
        "Consume only a prefix",
        'Check(RangeFrom(5, 4).Take(2).SequenceEqual(new[] { 5, 6 }), "bounded prefix");\nCheck(!RangeFrom(5, 0).Any(), "empty range");',
        "The consumer receives 5 and 6 and can stop before the full range.",
        "The producer does not need to allocate all four outputs before serving the first one.",
    ),
    (
        "Validate before returning the sequence",
        'bool rejected = false;\ntry { _ = RangeFrom(0, -1); } catch (ArgumentOutOfRangeException) { rejected = true; }\nCheck(rejected, "validation occurs at call boundary");\nCheck(RangeFrom(2, 3).Sum() == 9, "complete enumeration");',
        "Negative count is rejected immediately, without enumeration.",
        "The outer method validates first; the local iterator performs only the admitted traversal.",
    ),
    [
        "Trace how many values Take(2) requests.",
        "Generate every second integer with a bounded count.",
        "Implement a lazy sequence of cumulative totals.",
        "Diagnose validation inside an iterator body that callers expect to run immediately.",
        "Test count zero, one and negative.",
        "Choose a sequence API for a large file and document repeated-enumeration and resource-lifetime behavior.",
    ],
    "A sequence is not necessarily repeatable or cheap to enumerate. Do not assume calling an iterator method executes its body. Overflow remains possible even in a lazy generator.",
    helpers="public static IEnumerable<int> RangeFrom(int start, int count) { if (count < 0) throw new ArgumentOutOfRangeException(nameof(count)); return Iterate(); IEnumerable<int> Iterate() { for (int i = 0; i < count; i++) yield return checked(start + i); } }",
)

lesson(
    "Exceptions and preserving failure meaning",
    """Exceptions carry an abnormal control-flow result across method boundaries. Catch an exception where the program can make a meaningful recovery decision, add context or translate it into a public error contract. Catching everything at every layer often destroys the reason the operation failed.

A normal absence can be represented without an exception when it is expected. A malformed argument or failed invariant should remain visible. When rethrowing in a catch block, use `throw;` to preserve the original stack relationship. When adding a domain exception, retain the original as InnerException. Logging the same exception at every layer can multiply noise without adding evidence.""",
    "`try` encloses an operation; typed catch selects a failure category; finally runs cleanup when control leaves the protected region. `throw;` rethrows the current exception. A catch filter with `when` narrows recovery policy.",
    [
        ("Exception", "An object describing abnormal completion."),
        ("Stack trace", "The recorded call path associated with failure."),
        ("Translation", "Mapping an internal failure to a public contract."),
    ],
    (
        "Catch only the expected invalid format",
        'int ParseCount(string text) { int value = int.Parse(text, CultureInfo.InvariantCulture); if (value < 0) throw new ArgumentOutOfRangeException(nameof(text)); return value; }\nbool format = false;\ntry { ParseCount("oops"); } catch (FormatException) { format = true; }\nCheck(format && ParseCount("3") == 3, "format and success are distinct");',
        "Malformed numeric text is caught as a format error.",
        "The catch does not accidentally classify every possible programming error as bad user text.",
    ),
    (
        "Retain an inner cause",
        'Exception? observed = null;\ntry { try { throw new IOException("synthetic read failure"); } catch (IOException cause) { throw new InvalidOperationException("import failed", cause); } }\ncatch (InvalidOperationException error) { observed = error; }\nCheck(observed?.InnerException is IOException, "cause retained");',
        "The outer domain failure still contains the I/O cause.",
        "A public description can add context without erasing the lower-level failure category.",
    ),
    [
        "Identify which failure category each catch handles.",
        "Add a separate negative-count case without classifying it as FormatException.",
        "Define an import API with distinct invalid-input and storage-failure outcomes.",
        "Diagnose catch-all code that returns an empty successful report.",
        "Test success, expected rejection and an unexpected exception separately.",
        "Decide which layer owns user-facing error translation and which details should remain private diagnostics.",
    ],
    "A catch-all that returns a default can turn data loss into apparent success. Throwing the caught variable instead of using bare throw changes stack-trace behavior. Cleanup should not accidentally replace the original failure.",
)

lesson(
    "Disposable resources and deterministic cleanup",
    """Managed memory collection does not mean every resource can wait for garbage collection. Files, sockets and handles need a clear owner that releases them promptly. IDisposable expresses synchronous cleanup. A using declaration or statement arranges Dispose when control leaves the scope, including exceptions.

Ownership is a contract between caller and callee. If a function receives a stream, it should not close a caller-owned stream unless documented. Multiple wrappers can share an underlying resource, so leave-open options matter. Deterministic cleanup prevents resource exhaustion and also makes tests independent: a later operation should not inherit a locked file from an earlier failure.""",
    "`using (var resource = ...) { ... }` scopes lifetime. `using var resource = ...` disposes at the end of the containing scope. `await using` supports IAsyncDisposable when cleanup itself is asynchronous.",
    [
        ("Resource owner", "The component responsible for release."),
        ("IDisposable", "A contract for deterministic synchronous cleanup."),
        ("Scope", "The region that bounds a local lifetime."),
    ],
    (
        "Dispose on ordinary scope exit",
        'var resource = new Probe();\nusing (resource) { Check(!resource.Closed, "open inside scope"); }\nCheck(resource.Closed, "closed after scope");',
        "The resource is open inside and closed afterward.",
        "Scope exit is the ownership boundary; no garbage-collector timing is needed.",
    ),
    (
        "Dispose after failure",
        'var resource = new Probe();\ntry { using (resource) { throw new InvalidOperationException("fixture"); } }\ncatch (InvalidOperationException) { }\nCheck(resource.Closed, "exception still cleans up");',
        "The controlled exception still triggers cleanup.",
        "The same cleanup contract applies to abnormal control flow, which is where manual release is often forgotten.",
    ),
    [
        "Trace the point at which Dispose runs in each example.",
        "Nest two resources and predict reverse disposal order.",
        "Write a helper that reads from a caller-owned stream without closing it.",
        "Diagnose returning a stream from inside a using scope.",
        "Test cleanup after an exception before normal completion.",
        "Document ownership and leave-open behavior for a parser that wraps a stream reader.",
    ],
    "Dispose does not automatically make an object safe for concurrent callers. Never rely on finalizer timing for a lock or file release. Releasing a borrowed resource violates its caller ownership.",
    helpers="public sealed class Probe : IDisposable { public bool Closed { get; private set; } public void Dispose() { Closed = true; } }",
)

lesson(
    "Files, paths and local data ownership",
    """A path is a name in a filesystem, not the data itself. Relative paths are interpreted against a working directory, which may differ between an editor, test runner and container. Construct owned paths explicitly and avoid assuming the repository is writable from learner code. The classroom retains saved pads separately from temporary worker files.

Writing a file creates a side effect with a lifetime. Tiny examples should create a unique temporary directory, operate only inside it, and remove it in finally. Production persistence requires more decisions: atomic replacement, backups, permissions and recovery after interruption. An in-memory assertion proves content logic but cannot establish durable storage behavior after a crash.""",
    "`Path.Combine` constructs a platform path. `File.WriteAllText` encodes text; `ReadAllText` decodes it. A try/finally protects cleanup, while recursive removal is safe only for a directory this operation uniquely owns.",
    [
        ("Working directory", "The base for resolving relative paths."),
        ("Encoding", "The rule converting text to bytes."),
        ("Owned temporary directory", "A uniquely created area this operation may clean up."),
    ],
    (
        "Round-trip an owned text file",
        'string root = Path.Combine(Path.GetTempPath(), "lesson-" + Guid.NewGuid().ToString("N"));\nDirectory.CreateDirectory(root);\ntry { string path = Path.Combine(root, "note.txt"); File.WriteAllText(path, "café", Encoding.UTF8); Check(File.ReadAllText(path, Encoding.UTF8) == "café", "UTF-8 round trip"); }\nfinally { Directory.Delete(root, true); }\nCheck(!Directory.Exists(root), "owned cleanup");',
        "The Unicode text round-trips and the owned directory is removed.",
        "The random name prevents collisions while the observable content remains deterministic.",
    ),
    (
        "Separate logical and filesystem names",
        'string fileName = "report.csv";\nCheck(Path.GetFileName(fileName) == fileName, "simple leaf name");\nCheck(Path.GetFileName("nested/report.csv") != "nested/report.csv", "nested name is not a leaf");\nCheck(Path.GetExtension(fileName) == ".csv", "extension classification");',
        "A simple leaf name and a nested path are recognized as different shapes.",
        "These lexical checks teach path structure; they are not a complete traversal or symlink security boundary.",
    ),
    [
        "Trace directory creation, write, read and cleanup ownership.",
        "Write two lines and preserve their explicit newline policy.",
        "Build a temporary-file round trip for a small inventory report.",
        "Diagnose resolving a relative path against an unexpected working directory.",
        "Test empty content and non-ASCII text.",
        "Explain what must change to make a persistent report update crash-recoverable.",
    ],
    "Path normalization alone does not solve symlink attacks or concurrent replacement. Do not delete arbitrary user-provided directories. Worker temporary files are not the durable learner progress store.",
)

lesson(
    "JSON contracts and schema evolution",
    """JSON provides a portable syntax for values, arrays and objects; it does not define the business schema. Deserializing into a type supplies a structural mapping, but required domain rules still need validation. A missing property can become a default value, and a syntactically valid object can still be meaningless for the application.

Schema evolution requires deciding what happens when fields are added, removed or renamed. A version field and explicit migration can preserve meaning. Do not equate a successful deserialize call with a safe external object. Validate ranges and identities before admitting the object into domain logic, and avoid serializing internal secrets merely because a public property exists.""",
    "`JsonSerializer.Serialize` creates JSON text. `Deserialize<T>` maps it into T and can return null. Records provide compact transport shapes. Serialization options control naming and formatting but do not replace domain validation.",
    [
        ("Serialization", "Encoding an object representation into data."),
        ("Schema", "The expected structure and meaning of fields."),
        ("Migration", "A deliberate conversion between schema versions."),
    ],
    (
        "Round-trip a small transport record",
        'var original = new ItemDto("pear", 3);\nstring json = JsonSerializer.Serialize(original);\nvar restored = JsonSerializer.Deserialize<ItemDto>(json);\nCheck(restored == original, "record round trip");',
        "The restored name and quantity match the original record.",
        "Equality checks the modeled data rather than incidental property ordering in JSON text.",
    ),
    (
        "Validate after structural decoding",
        'var invalid = JsonSerializer.Deserialize<ItemDto>("{\\"Name\\":\\"pear\\",\\"Quantity\\":-2}");\nCheck(invalid is not null && !Valid(invalid), "domain rejection after decoding");\nCheck(!Valid(new ItemDto("", 2)), "empty identity rejected");',
        "Valid JSON can decode into a rejected domain value.",
        "Parsing answers whether the representation is understood. Validation answers whether the application may use it.",
    ),
    [
        "Predict what round-trip equality establishes and what it does not.",
        "Add a clearly versioned optional description field.",
        "Write a decoder returning explicit validation errors for missing name and negative quantity.",
        "Diagnose trusting default values from missing JSON fields.",
        "Test malformed JSON, JSON null and an extra unknown field.",
        "Design a migration from a renamed quantity field while retaining old saved records.",
    ],
    "JSON text equality is sensitive to formatting and property ordering. Structural decoding does not enforce every domain invariant. Keep public transport models separate from internal objects carrying credentials or resources.",
    helpers="public record ItemDto(string Name, int Quantity);\npublic static bool Valid(ItemDto item) => !string.IsNullOrWhiteSpace(item.Name) && item.Quantity >= 0;",
)

lesson(
    "Dates, durations and culture-independent data",
    """An instant, a local wall-clock time and a duration are different concepts. DateTimeOffset combines a date-time with an offset, making an instant comparison explicit. A time-zone identifier carries additional historical daylight-saving rules that a fixed offset does not. Do not infer a region from its offset alone.

A duration measures elapsed time; a calendar rule such as next month follows calendar boundaries. Persist machine-readable data using a stable format and parse with an explicit culture. User-facing formatting may intentionally vary by locale. Tests should fix their clock inputs rather than depend on the date or local zone of the machine running them.""",
    "`DateTimeOffset.Parse` with an explicit round-trip string creates a known instant. `ToUniversalTime` changes its display offset while retaining the instant. Subtraction produces TimeSpan. InvariantCulture avoids environment-dependent machine-data parsing.",
    [
        ("Instant", "A point on the time line."),
        ("Offset", "A displacement from UTC at one observation."),
        ("Duration", "An elapsed interval between instants."),
    ],
    (
        "Different offsets, same instant",
        'var a = DateTimeOffset.Parse("2025-01-01T12:00:00+02:00", CultureInfo.InvariantCulture);\nvar b = DateTimeOffset.Parse("2025-01-01T10:00:00Z", CultureInfo.InvariantCulture);\nCheck(a == b, "same instant");\nCheck(a.Offset != b.Offset, "different representations");',
        "The values denote the same instant despite different offsets.",
        "Comparing wall-clock components would miss the offset information.",
    ),
    (
        "Measure a fixed duration",
        'var start = new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero);\nvar end = start.AddMinutes(90);\nCheck((end - start).TotalMinutes == 90, "elapsed duration");\nstring encoded = start.ToString("O", CultureInfo.InvariantCulture);\nCheck(DateTimeOffset.Parse(encoded, CultureInfo.InvariantCulture) == start, "round-trip format");',
        "The elapsed duration is 90 minutes and the timestamp round-trips.",
        "A fixed fixture keeps evidence independent of the host clock and locale.",
    ),
    [
        "Explain why the two offset timestamps compare equal.",
        "Change one instant by one minute and predict the comparison.",
        "Build a duration report using fixed UTC timestamps.",
        "Diagnose treating an offset as a complete time-zone identity.",
        "Test intervals across midnight and reject an end before its start when the domain forbids it.",
        "Design storage and display policies for appointments in a named time zone.",
    ],
    "DateTime kind and unspecified local values can introduce ambiguity. Daylight-saving transitions can produce invalid or repeated local times. Use elapsed-time clocks for performance measurement, not wall-clock timestamps.",
)

lesson(
    "Testing contracts with meaningful counterexamples",
    """A test is useful when a plausible wrong implementation would fail it. Repeating the implementation expression on both sides of an assertion provides weak independence. Start from a contract, choose a normal case, a boundary case and a known misconception, then derive expected outcomes separately.

The classroom uses framework-free throwing checks so the default route needs no package download. A separate prepared project can use a test framework and a test runner. Keep deterministic unit tests focused on pure behavior, and label integration tests that exercise files, databases or networks. A passing unit test does not prove a dependency is configured correctly.""",
    "A table of inputs and expected values separates cases from the loop executing them. An exception assertion should check the intended category. Avoid sleep-based timing tests; coordinate concurrent states with explicit signals.",
    [
        ("Test oracle", "The independent rule deciding whether behavior is correct."),
        ("Regression case", "A case preserving evidence of a previous defect."),
        ("Boundary test", "A test at a transition or limit of the contract."),
    ],
    (
        "Use independently derived cases",
        'var cases = new[] { (Input: -2, Expected: 0), (Input: 0, Expected: 0), (Input: 3, Expected: 3) };\nforeach (var test in cases) Check(ClampNonnegative(test.Input) == test.Expected, "clamp contract");',
        "Negative, zero and positive cases preserve their intended categories.",
        "The literal expectations come from the stated clamp rule, not a duplicated implementation.",
    ),
    (
        "Detect a plausible wrong function",
        'int Wrong(int value) => value <= 0 ? 1 : value;\nCheck(Wrong(0) != ClampNonnegative(0), "boundary catches wrong default");\nCheck(ClampNonnegative(ClampNonnegative(-4)) == ClampNonnegative(-4), "idempotence");',
        "The zero case catches the incorrect default, and clamping twice changes nothing further.",
        "A property complements examples but does not replace the domain-specific expected values.",
    ),
    [
        "Explain which wrong implementations each case would reject.",
        "Add an extreme integer case without overflow.",
        "Write table-driven checks for your inventory quantity validator.",
        "Diagnose an assertion comparing a function call with the same call.",
        "Test idempotence and an independently derived boundary value.",
        "Separate unit and integration evidence for a JSON file importer.",
    ],
    "Tests that always print success or catch their own assertion failures provide misleading evidence. A flaky test weakens trust even when production code is correct. Random generation requires a reproducible seed and a clear oracle.",
    helpers="public static int ClampNonnegative(int value) => value < 0 ? 0 : value;",
)

lesson(
    "Async, await and task completion",
    """A Task represents eventual completion, failure or cancellation. Async methods let control return to a caller while an awaited operation is incomplete. Async does not automatically mean a new thread, and awaiting a task does not block a thread in the same way as calling Wait or Result. For I/O, the goal is to avoid holding a thread idle while another system works.

Keep task ownership visible: the caller should await work whose result or failure matters. Fire-and-forget work can outlive its owner and lose exceptions. CPU-heavy work has different scheduling needs from asynchronous I/O. This chapter uses already completed and explicitly coordinated tasks so results do not depend on network access or arbitrary delays.""",
    "`async Task<int>` declares an asynchronous result. `await` obtains the completed result or rethrows the task failure. Task.WhenAll combines completion of several tasks; its result order follows the input task order, not completion order.",
    [
        ("Task", "A handle for eventual completion and its outcome."),
        ("Await", "An asynchronous wait that observes the task result."),
        ("Composition", "Combining smaller asynchronous operations into an owned result."),
    ],
    (
        "Await values explicitly",
        'Task<int> pending = Task.FromResult(7);\nint value = await pending;\nCheck(value == 7 && pending.IsCompletedSuccessfully, "observed completion");',
        "Await yields 7 and confirms successful completion.",
        "The task handle and the eventual integer are distinct values even when this fixture completes immediately.",
    ),
    (
        "Compose and observe failure",
        'int[] values = await Task.WhenAll(Task.FromResult(2), Task.FromResult(3));\nCheck(values.SequenceEqual(new[] { 2, 3 }), "input order retained");\nbool observed = false;\ntry { await Task.FromException<int>(new InvalidOperationException("fixture")); } catch (InvalidOperationException) { observed = true; }\nCheck(observed, "failure propagated through await");',
        "WhenAll retains input order and await exposes the task exception.",
        "Awaiting establishes ownership of both success and failure instead of losing an unobserved background result.",
    ),
    [
        "Distinguish the Task<int> handle from its awaited integer.",
        "Combine three completed tasks and predict output ordering.",
        "Write an async method returning a validated total.",
        "Diagnose forgetting to await an operation whose failure matters.",
        "Test successful, failed and empty WhenAll inputs.",
        "Explain when CPU work might need scheduling separately from an asynchronous I/O API.",
    ],
    "Async void is mainly for required event-handler signatures, not general composable methods. Blocking with Result can deadlock in synchronization contexts. Task.Run does not make a blocking external API inherently scalable.",
)

lesson(
    "Cooperative cancellation and bounded waiting",
    """Cancellation is a request for cooperation. A CancellationTokenSource owns the request; its token lets operations observe it. An operation that never checks or passes the token can continue after cancellation is requested. A timeout on the caller waiting is also distinct from termination of the underlying work.

Correct ownership includes awaiting or otherwise accounting for admitted work after a timeout. Do not retry a state-changing operation merely because the result is unknown. The first operation may still complete. Use operation identity and recovery evidence for such systems. Here, a TaskCompletionSource establishes exact states without guessing how long a background task takes.""",
    "`ThrowIfCancellationRequested` reports acknowledged cancellation. `WaitAsync(token)` cancels the wait without necessarily canceling the source task. TaskCompletionSource with RunContinuationsAsynchronously avoids executing arbitrary continuations inline inside a signal setter.",
    [
        ("Cancellation token", "A cooperative notification of requested cancellation."),
        ("Wait cancellation", "Stopping observation without proving work stopped."),
        ("Unknown result", "An operation whose final effect has not yet been observed."),
    ],
    (
        "Observe a requested cancellation",
        'using var source = new CancellationTokenSource();\nsource.Cancel();\nbool observed = false;\ntry { source.Token.ThrowIfCancellationRequested(); } catch (OperationCanceledException) { observed = true; }\nCheck(observed, "cooperative observation");',
        "The token check acknowledges cancellation.",
        "Calling Cancel changes request state; the explicit observation is what changes the operation control flow.",
    ),
    (
        "Cancel waiting while work remains live",
        'var completion = new TaskCompletionSource<int>(TaskCreationOptions.RunContinuationsAsynchronously);\nusing var source = new CancellationTokenSource(); source.Cancel();\nbool cancelled = false;\ntry { await completion.Task.WaitAsync(source.Token); } catch (OperationCanceledException) { cancelled = true; }\nCheck(cancelled && !completion.Task.IsCompleted, "only the wait ended");\ncompletion.SetResult(9);\nCheck(await completion.Task == 9, "underlying result still arrives");',
        "The wait cancels, then the original task later completes with 9.",
        "This deterministic distinction prevents treating an interrupted observer as proof that an operation never happened.",
    ),
    [
        "Identify the request, observation and completion events.",
        "Pass a token through a helper and check it before a state change.",
        "Write an operation that stops cooperatively and preserves already committed work.",
        "Diagnose automatically replaying a write after its waiter times out.",
        "Test cancellation requested before start and after successful completion.",
        "Design an operation receipt distinguishing cancelled waiting, confirmed cancellation and unknown outcome.",
    ],
    "A catch for OperationCanceledException should match the intended cancellation policy. Cancelling a waiter does not dispose all resources owned by the operation. Retain and observe tasks that may still complete.",
    source="https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-cancellation",
)

lesson(
    "Bounded channels and producer-consumer ownership",
    """A channel connects producers and consumers through an asynchronous queue. Capacity is a resource policy: an unbounded queue can retain more work than memory or downstream systems can handle. A bounded channel makes overload visible through waiting, rejection or an explicit drop policy. Choose that policy from the value of the work, not from convenience.

Completion means no more writes will be admitted, while readers can still drain buffered items. A consumer should distinguish an empty-but-open channel from a completed channel. Cancellation and failure also need owners: somebody must complete the writer and account for admitted items. The single-process fixture teaches these states without depending on thread timing.""",
    "`Channel.CreateBounded<T>` creates a capacity-limited channel. TryWrite reports immediate admission. ReadAsync removes an item; Writer.Complete closes admission. Reader.Completion finishes after buffered work is drained.",
    [
        ("Backpressure", "Limiting admitted work when capacity is exhausted."),
        ("Admission", "Acceptance of a work item into owned processing."),
        ("Drain", "Processing already admitted items after writes stop."),
    ],
    (
        "Reject immediate excess admission",
        'var channel = Channel.CreateBounded<int>(1);\nCheck(channel.Writer.TryWrite(4), "first item admitted");\nCheck(!channel.Writer.TryWrite(5), "capacity reached");\nCheck(await channel.Reader.ReadAsync() == 4, "admitted value retained");',
        "The first item is accepted and the second immediate write is refused.",
        "Bounded capacity is observable before work is lost or memory grows without limit.",
    ),
    (
        "Drain after completion",
        'var channel = Channel.CreateBounded<int>(2);\nchannel.Writer.TryWrite(2); channel.Writer.TryWrite(3); channel.Writer.Complete();\nint sum = 0;\nawait foreach (int value in channel.Reader.ReadAllAsync()) sum += value;\nawait channel.Reader.Completion;\nCheck(sum == 5 && !channel.Writer.TryWrite(9), "drained and closed");',
        "Both admitted items are read after completion, and later writes fail.",
        "Closing admission does not discard buffered work. Completion becomes final after the reader drains it.",
    ),
    [
        "Trace channel occupancy after each operation.",
        "Increase capacity and predict which immediate writes succeed.",
        "Build a bounded producer-consumer pipeline with explicit writer completion.",
        "Diagnose treating an empty open channel as permanently finished.",
        "Test completion with zero buffered items and with a full buffer.",
        "Choose wait, reject or drop behavior for a workload and explain what evidence the producer receives.",
    ],
    "An ignored false TryWrite result loses work. Blocking a producer while holding a lock needed by the consumer can deadlock. Completion and cancellation need a deliberate ownership policy.",
)

lesson(
    "Composition project: a deterministic import service",
    """The intermediate project separates a transport representation, validation, a pure aggregation and an asynchronous service boundary. This makes failure location visible. JSON syntax errors belong to decoding; invalid records belong to domain validation; a cancelled operation must not be presented as an empty successful import.

A complete service also owns its dependency lifetime and result shape. The classroom version uses an in-memory JSON payload, avoiding external I/O while preserving the same boundary decisions. A production adapter can load bytes from a file or HTTP response, then call the same pure core. Keep the core deterministic so integration failures do not obscure calculation errors.""",
    "An async method can validate cancellation before admitting work and return a record describing accepted totals and rejected counts. Immutable result fields make it easier to store a receipt without later mutation.",
    [
        ("Transport model", "A representation of data crossing a boundary."),
        ("Domain validation", "Checking whether represented data is admissible."),
        ("Service result", "A stable description of completed work."),
    ],
    (
        "Import valid and invalid records",
        'var result = await ImportAsync("[{\\"Name\\":\\"pear\\",\\"Quantity\\":2},{\\"Name\\":\\"\\",\\"Quantity\\":3}]", CancellationToken.None);\nCheck(result.Total == 2 && result.Rejected == 1, "validated aggregate");',
        "The service returns total 2 and one rejected record.",
        "Validation remains visible in the result instead of silently converting bad records into ordinary data.",
    ),
    (
        "Cancellation is not an empty report",
        'using var source = new CancellationTokenSource(); source.Cancel();\nbool cancelled = false;\ntry { await ImportAsync("[]", source.Token); } catch (OperationCanceledException) { cancelled = true; }\nCheck(cancelled, "cancelled request preserved");\nCheck((await ImportAsync("[]", CancellationToken.None)).Total == 0, "successful empty report");',
        "A cancelled request and a successful empty import have different outcomes.",
        "The result category carries meaning beyond a numeric total.",
    ),
    [
        "Trace syntax, validation and aggregation as separate stages.",
        "Add a duplicate valid name and document whether total quantity or distinct count is reported.",
        "Build a per-item result while preserving the rejected count.",
        "Diagnose catch-all logic returning an empty report after cancellation.",
        "Test malformed JSON, JSON null, an empty list and invalid quantities.",
        "Design an adapter boundary for a file or HTTP source without putting I/O inside the pure aggregation.",
    ],
    "A transport DTO is not automatically a trusted domain object. Do not merge cancelled, invalid and successfully empty results into one representation. An async signature alone does not make CPU work asynchronous.",
    helpers="""public record ImportItem(string Name, int Quantity);
public record ImportResult(int Total, int Rejected);
public static async Task<ImportResult> ImportAsync(string json, CancellationToken token) { token.ThrowIfCancellationRequested(); var items = JsonSerializer.Deserialize<ImportItem[]>(json) ?? throw new ArgumentException("array required"); int total = 0, rejected = 0; foreach (var item in items) { token.ThrowIfCancellationRequested(); if (string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0) { rejected++; continue; } total = checked(total + item.Quantity); } await Task.CompletedTask; return new ImportResult(total, rejected); }""",
)
