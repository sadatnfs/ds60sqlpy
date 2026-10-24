# ruff: noqa: E501
# Long original prose and embedded programs are content, not Python expression layout.
"""Advanced C# mechanisms and production design with bounded offline kernels."""

from render import lesson


def add(title, mental, anatomy, terms, a, b, tasks, pitfalls, **kwargs):
    lesson(title, mental, anatomy, terms, a, b, tasks, pitfalls, **kwargs)


add(
    "Threads, locks and compound invariants",
    """Concurrency permits operations to overlap. A data race occurs when unsynchronized access to shared mutable state violates the required memory and ordering rules. Even an apparently simple increment includes read, calculation and write, so it is not automatically atomic. Correctness requires protecting the entire invariant, not just individual fields.

A lock establishes mutual exclusion and ordering for code using the same lock object. Keep the protected region small and avoid awaiting while holding a synchronous lock. Never choose a publicly accessible object or a mutable value as the lock identity. Deadlock is a separate risk when multiple locks are acquired in conflicting orders; a single documented ordering can prevent that class of cycle.""",
    "`lock (gate)` enters a protected region and exits even on exceptions. All accesses participating in the invariant must use the same gate. Task.WhenAll observes the completion of the scheduled work.",
    [
        ("Atomicity", "An operation behaving as one indivisible state transition."),
        ("Mutual exclusion", "Only one participant enters a protected region at a time."),
        ("Deadlock", "A cycle of waiting that prevents progress."),
    ],
    (
        "Protect increments",
        'var counter = new LockedCounter();\nawait Task.WhenAll(Enumerable.Range(0, 4).Select(_ => Task.Run(() => { for (int i = 0; i < 100; i++) counter.Add(); })));\nCheck(counter.Value == 400, "all protected increments");',
        "Four tasks produce exactly 400 increments.",
        "The lock protects the read-modify-write transition, so the expected count does not depend on scheduling.",
    ),
    (
        "Protect a multi-field invariant",
        'var account = new LockedCounter();\naccount.Add(); account.Add();\nCheck(account.Value == 2, "consistent observation");\nCheck(account.Value >= 0, "valid state");',
        "The reader uses the same gate as mutation.",
        "A synchronized writer with an unsynchronized reader does not establish the same contract.",
    ),
    [
        "Decompose an increment into its logical steps.",
        "Increase task count while keeping the exact expected total.",
        "Implement a locked transfer preserving the sum of two balances.",
        "Describe a two-lock acquisition cycle and repair it with an ordering rule.",
        "Test zero operations and concurrent readers.",
        "Choose immutable snapshots or a lock for a shared report cache and justify the ownership model.",
    ],
    "A passing unsynchronized stress run does not prove absence of races. Locking a different object in the reader does not protect the writer invariant. Never await inside a synchronous lock.",
    helpers="public sealed class LockedCounter { private readonly object gate = new(); private int value; public void Add() { lock (gate) value++; } public int Value { get { lock (gate) return value; } } }",
)

add(
    "Atomic operations and concurrent collections",
    """Interlocked provides atomic operations on supported locations, such as increment and compare-exchange. These operations are useful for simple shared state, but several individually atomic operations do not automatically form one atomic transaction. Match the mechanism to the complete invariant.

Concurrent collections make their documented operations thread-safe. Delegates passed to GetOrAdd or AddOrUpdate may execute more than once and outside internal locks. They should therefore avoid irreversible side effects. A dictionary value being safely published does not make a mutable object stored inside it automatically thread-safe.""",
    "`Interlocked.Increment(ref value)` atomically updates one location. ConcurrentDictionary manages concurrent lookup/update operations. A factory must tolerate repeated evaluation.",
    [
        ("Interlocked", "Atomic operations on supported shared locations."),
        ("Thread-safe operation", "An operation with a documented concurrency contract."),
        ("Factory purity", "Avoiding externally visible effects in value construction callbacks."),
    ],
    (
        "Count atomically",
        'int count = 0;\nawait Task.WhenAll(Enumerable.Range(0, 4).Select(_ => Task.Run(() => { for (int i = 0; i < 100; i++) Interlocked.Increment(ref count); })));\nCheck(count == 400, "atomic count");',
        "The atomic count is exactly 400.",
        "Each increment is one supported atomic operation rather than a compound unsynchronized expression.",
    ),
    (
        "Update one key safely",
        'var counts = new ConcurrentDictionary<string, int>();\nawait Task.WhenAll(Enumerable.Range(0, 20).Select(_ => Task.Run(() => counts.AddOrUpdate("a", 1, (_, previous) => previous + 1))));\nCheck(counts["a"] == 20, "concurrent key updates");',
        "Twenty admitted updates produce 20.",
        "The update delegate is a pure calculation, so repeated evaluation cannot duplicate an external effect.",
    ),
    [
        "Compare count++ with Interlocked.Increment.",
        "Add a second independently counted key.",
        "Build a concurrent frequency counter using pure update functions.",
        "Diagnose sending a message inside an AddOrUpdate delegate.",
        "Test absent and already-present keys.",
        "Explain why atomically updating two separate balances does not preserve a transfer invariant.",
    ],
    "Concurrent containers protect their own structure, not arbitrary objects stored inside them. Do not infer once-only callback execution. Use a higher-level lock or transaction for multi-location invariants.",
)

add(
    "Span, slices and memory lifetime",
    """Span<T> is a view over contiguous memory. A slice describes a region without copying its elements, so writes through a mutable span change the underlying storage. ReadOnlySpan prevents mutation through that view but does not freeze other aliases. This makes ownership and lifetime central to correct use.

Span is a ref struct with restrictions that prevent it from escaping into ordinary heap objects. It cannot be retained across an await boundary. Memory<T> can represent a heap-storable region for asynchronous APIs, but its owner still controls lifetime. Optimize allocations only after measuring; a span does not improve an algorithm whose complexity is the real bottleneck.""",
    "`array.AsSpan(start, length)` creates a view. `Slice` changes the viewed interval. `ReadOnlySpan<T>` narrows write capability. Keep synchronous span logic in a helper separate from async orchestration.",
    [
        ("Span", "A bounded view over contiguous memory."),
        ("Slice", "A subregion sharing the same backing storage."),
        ("Lifetime", "The period during which referenced storage remains valid."),
    ],
    (
        "Mutate through a view",
        'int[] values = { 1, 2, 3 };\nDoubleMiddle(values);\nCheck(values.SequenceEqual(new[] { 1, 4, 3 }), "slice aliases array");',
        "Only the middle element changes.",
        "A span slice is a view, not a copy of the selected element.",
    ),
    (
        "Parse without allocating substrings",
        'Check(SumDigits("123".AsSpan()) == 6, "digit total");\nCheck(SumDigits(ReadOnlySpan<char>.Empty) == 0, "empty identity");',
        "The digit total is 6 and empty input totals zero.",
        "The helper reads directly from the character view and validates each admitted character.",
    ),
    [
        "Draw the backing array and slice boundaries.",
        "Change the slice to cover two elements.",
        "Write a synchronous span helper counting separators.",
        "Diagnose retaining a span across await.",
        "Test empty and out-of-range slices and distinguish valid empty from invalid bounds.",
        "Choose Span or Memory for a synchronous parser and an asynchronous buffer owner.",
    ],
    "ReadOnlySpan restricts this view, not every alias. A rented buffer must not be returned while a view is still in use. Bounds checking protects indices, not logical parsing rules.",
    helpers="public static void DoubleMiddle(int[] values) { Span<int> middle = values.AsSpan(1, 1); middle[0] *= 2; }\npublic static int SumDigits(ReadOnlySpan<char> text) { int total = 0; foreach (char ch in text) { if (ch < '0' || ch > '9') throw new ArgumentException(\"digits required\"); total += ch - '0'; } return total; }",
    source="https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/",
)

add(
    "Garbage collection, pooling and retained memory",
    """The garbage collector reclaims unreachable managed objects. Reachability is not the same as usefulness: a global list or event subscription can keep an otherwise unwanted object alive. Resource cleanup still belongs to IDisposable rather than collection timing. Measure retained references before assuming the collector is malfunctioning.

ArrayPool reuses buffers to reduce allocation pressure. A rented array may be larger than requested and may contain prior data. Use only the logical length, initialize what will be read, and return exactly the borrowed array once. Clearing sensitive contents is a deliberate policy. Pooling adds ownership complexity, so it should solve a measured allocation problem.""",
    "`ArrayPool<T>.Shared.Rent(n)` grants temporary use of at least n elements. `Return` ends ownership. A try/finally protects return on failure; never expose a view after return.",
    [
        ("Reachability", "Whether a live reference path can still reach an object."),
        ("Pool", "A reusable store of resources."),
        ("Logical length", "The meaningful region distinct from physical capacity."),
    ],
    (
        "Use only admitted buffer contents",
        'int[] rented = ArrayPool<int>.Shared.Rent(3);\ntry { rented[0] = 2; rented[1] = 3; rented[2] = 4; Check(rented.AsSpan(0, 3).ToArray().Sum() == 9, "logical range"); Check(rented.Length >= 3, "minimum capacity"); }\nfinally { ArrayPool<int>.Shared.Return(rented, clearArray: true); }',
        "Only three initialized elements contribute to the total.",
        "The pool guarantees minimum capacity, not exact size or zeroed contents.",
    ),
    (
        "Release retained references deliberately",
        'var retained = new List<byte[]> { new byte[32], new byte[32] };\nCheck(retained.Count == 2, "references retained");\nretained.Clear();\nCheck(retained.Count == 0, "application releases references");',
        "Clearing removes the application references without promising collection timing.",
        "The test checks controllable ownership, avoiding a flaky assumption about when garbage collection occurs.",
    ),
    [
        "Separate logical length from rented array length.",
        "Use a different requested length while initializing exactly that region.",
        "Write a pooled-buffer helper with finally-based return.",
        "Diagnose reading uninitialized pooled capacity or returning the same buffer twice.",
        "Test cleanup when the computation throws.",
        "Decide whether pooling is justified using allocation measurements and a stated lifetime contract.",
    ],
    "Never assert that a weak reference must disappear immediately after a collection request. Returning a buffer while asynchronous work still uses it causes data corruption. Pooling is not inherently a performance win.",
)

add(
    "Algorithmic complexity and measured performance",
    """Performance begins with an explicit workload and cost model. A nested search can perform quadratically many comparisons, while an indexed lookup may trade memory for near-constant expected lookup cost. Big-O describes growth, not an exact elapsed time or a universal ranking. Constant factors, data layout and input size matter.

Measure correctness separately from speed. A benchmark that computes a different result is irrelevant. Warmup, allocation, runtime optimization and background load can distort tiny timings. The classroom counts deterministic operations to explain growth; a prepared external benchmark project is the right place for statistically meaningful elapsed-time comparisons.""",
    "HashSet membership can avoid repeated linear scans. Distinct and grouping have equality-policy assumptions. Count comparisons in a fixture instead of asserting a fragile timing threshold.",
    [
        ("Complexity", "How a resource requirement grows with input size."),
        ("Cost model", "The operations or resources being counted."),
        ("Benchmark", "A controlled measurement of implementation behavior."),
    ],
    (
        "Count a linear search",
        'int[] values = { 2, 4, 6, 8 };\nint comparisons = 0;\nbool found = false;\nforeach (int value in values) { comparisons++; if (value == 8) { found = true; break; } }\nCheck(found && comparisons == 4, "last-element linear search");',
        "Finding the last element needs four comparisons.",
        "The deterministic count illustrates the algorithm independently of machine speed.",
    ),
    (
        "Trade memory for repeated membership",
        'var index = new HashSet<int>(new[] { 2, 4, 6, 8 });\nCheck(index.Contains(8) && !index.Contains(9), "indexed membership");\nCheck(index.Count == 4, "index has stored identities");',
        "The index answers membership while storing four identities.",
        "Building and retaining the index has a cost that should be amortized across enough queries.",
    ),
    [
        "Count comparisons for first, last and absent targets.",
        "Double the input size and predict worst-case linear comparisons.",
        "Compare repeated list scans with one built index while preserving equality policy.",
        "Diagnose a benchmark that excludes index construction from a one-shot workload.",
        "Test duplicate inputs and empty queries.",
        "Write a benchmark plan specifying workload, correctness checks, warmup and allocation measurements.",
    ],
    "A single stopwatch sample is not reliable evidence. Expected hash lookup cost depends on hashing behavior. Do not optimize a micro-operation before identifying the dominant algorithm or I/O cost.",
)

add(
    "Validation, regular expressions and bounded input",
    """Validation defines what an input means and which representations are accepted. A regular expression can recognize a textual shape, but it does not enforce every semantic rule. A date-shaped string can still name an impossible date. Keep size, syntax and domain validation as separate steps.

Backtracking expressions can require excessive work on adversarial inputs. Use a bounded input length, a timeout and an appropriate engine mode. Prefer simple parsers when they make the contract clearer. Never construct a regex from untrusted text without deciding whether that text is literal or syntax.""",
    "`RegexOptions.NonBacktracking` supports a bounded engine for compatible patterns. Anchors constrain the entire input. Regex.Escape treats input as literal pattern text. Domain validation follows a successful shape match.",
    [
        ("Syntax validation", "Checking representational structure."),
        ("Semantic validation", "Checking whether represented values make sense."),
        ("ReDoS", "Resource exhaustion caused by costly regular-expression behavior."),
    ],
    (
        "Validate a bounded identifier",
        'var pattern = new Regex(@"\\A[a-z][a-z0-9_]{0,15}\\z", RegexOptions.NonBacktracking, TimeSpan.FromSeconds(1));\nCheck(pattern.IsMatch("report_2"), "accepted identifier");\nCheck(!pattern.IsMatch("2report") && !pattern.IsMatch("report!"), "rejected shapes");',
        "The identifier begins with a lowercase letter and uses only admitted characters.",
        "Whole-input anchors prevent a valid substring from disguising an invalid full value.",
    ),
    (
        "Keep literal user text literal",
        'string literal = "a+b";\nvar pattern = new Regex(@"\\A" + Regex.Escape(literal) + @"\\z", RegexOptions.NonBacktracking, TimeSpan.FromSeconds(1));\nCheck(pattern.IsMatch("a+b") && !pattern.IsMatch("aaab"), "escaped literal");',
        "The plus sign is matched literally.",
        "Escaping preserves data meaning instead of accidentally granting regex syntax authority.",
    ),
    [
        "Explain every part of the identifier pattern.",
        "Change the maximum identifier length and test the exact boundary.",
        "Validate a structured identifier and then check its domain-specific reserved words.",
        "Diagnose matching a valid substring inside an invalid full input.",
        "Test newline, empty input and one character beyond the limit.",
        "Choose a parser or regex for a nested format and justify complexity and error reporting.",
    ],
    "A timeout is a fallback, not a substitute for a simple pattern and bounded input. Regex does not make a path, SQL query or HTML context safe. Validate according to the destination meaning.",
)

add(
    "HTTP clients, status contracts and offline transport tests",
    """HTTP separates transport completion from application success. Receiving a response does not imply a 2xx status, and a 2xx response does not guarantee a valid application payload. Inspect status, bound the response, decode it and validate its schema. Cancellation should flow through the request and body processing.

HttpClient is intended for reuse under a deliberate lifetime policy. Repeatedly creating clients for every request can waste connection resources. The classroom uses a custom HttpMessageHandler, so it exercises real request/response APIs without contacting a network. This proves application handling, not DNS, TLS or remote availability.""",
    "A message handler is the transport boundary beneath HttpClient. A fake handler returns HttpResponseMessage deterministically. EnsureSuccessStatusCode throws for unsuccessful status; validate the body afterward.",
    [
        ("Transport", "The mechanism carrying a request and response."),
        ("Status code", "The protocol-level response category."),
        ("Test double", "A controlled dependency used to exercise a consumer contract."),
    ],
    (
        "Decode a successful offline response",
        'using var client = new HttpClient(new FixtureHandler(HttpStatusCode.OK, "{\\"count\\":3}"));\nusing var response = await client.GetAsync("https://example.invalid/count");\nresponse.EnsureSuccessStatusCode();\nusing var json = JsonDocument.Parse(await response.Content.ReadAsStringAsync());\nCheck(json.RootElement.GetProperty("count").GetInt32() == 3, "validated fixture response");',
        "The handler supplies count 3 without network access.",
        "A reserved invalid domain makes the fixture identity clear, while the custom handler prevents any actual connection.",
    ),
    (
        "Preserve unsuccessful status",
        'using var client = new HttpClient(new FixtureHandler(HttpStatusCode.ServiceUnavailable, "unavailable"));\nusing var response = await client.GetAsync("https://example.invalid/count");\nbool rejected = false;\ntry { response.EnsureSuccessStatusCode(); } catch (HttpRequestException) { rejected = true; }\nCheck(rejected, "503 is not success");',
        "503 remains an observable failure rather than a default successful count.",
        "Response arrival and application success are separate facts.",
    ),
    [
        "Trace transport, status, decoding and schema validation boundaries.",
        "Return valid JSON with a missing count property and classify the failure.",
        "Write a client method accepting a supplied HttpClient and CancellationToken.",
        "Diagnose converting every non-2xx response into an empty success result.",
        "Test malformed JSON and an unexpected count type.",
        "Design a retry policy that distinguishes safe reads from writes with unknown outcomes.",
    ],
    "A fake transport does not validate certificates or server availability. Do not retry all status codes blindly. Bound request and response lifetimes and redact credentials from diagnostic logs.",
    helpers="public sealed class FixtureHandler(HttpStatusCode status, string body) : HttpMessageHandler { protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken token) { token.ThrowIfCancellationRequested(); return Task.FromResult(new HttpResponseMessage(status) { Content = new StringContent(body) }); } }",
)

add(
    "Domain architecture and dependency direction",
    """Domain logic expresses the rules that make an operation valid. Transport and storage adapters translate external representations into those rules. If the domain directly opens a database or reads environment variables, its behavior becomes difficult to reproduce. Dependency direction should let outer adapters depend on the core contract while the core remains independent of a specific transport.

Dependency injection is a construction technique, not a requirement to install a container library. Explicit constructors are often enough. Supply clocks, identifiers and repositories where variation matters. Avoid an interface for every trivial value; use abstraction where it separates policy from an unstable or expensive mechanism.""",
    "A service constructor accepts an interface. A small in-memory implementation supports deterministic tests. A clock abstraction returns a fixed instant in tests while a real adapter would obtain current time.",
    [
        ("Domain core", "Rules independent of storage and transport details."),
        ("Adapter", "A translation between an external mechanism and a core contract."),
        ("Dependency direction", "Which layer knows the details of another layer."),
    ],
    (
        "Inject a deterministic clock",
        'var service = new StampService(new FixedClock(new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero)));\nCheck(service.Stamp("a").StartsWith("2025-01-01", StringComparison.Ordinal), "fixed time");',
        "The result uses the supplied instant.",
        "The domain behavior does not depend on the machine clock during the test.",
    ),
    (
        "Preserve a core validation rule",
        'var service = new StampService(new FixedClock(DateTimeOffset.UnixEpoch));\nbool rejected = false;\ntry { service.Stamp(""); } catch (ArgumentException) { rejected = true; }\nCheck(rejected, "domain rejects empty identity");',
        "A different clock does not bypass identity validation.",
        "Dependency variation should not weaken the invariant owned by the domain.",
    ),
    [
        "Identify policy and mechanism in the service.",
        "Supply a second fixed clock and predict the changed timestamp.",
        "Extract the inventory aggregation into a transport-independent core.",
        "Diagnose a domain method reading the system clock internally despite accepting a clock.",
        "Test empty identity and a fixed instant around a date boundary.",
        "Draw dependency direction for a command-line adapter, HTTP adapter and shared domain library.",
    ],
    "A dependency container can conceal construction errors if overused. Do not inject mutable global services merely to rename global state. Keep core invariants in the core rather than duplicating them in every adapter.",
    helpers='public interface IClock { DateTimeOffset Now { get; } }\npublic sealed record FixedClock(DateTimeOffset Now) : IClock;\npublic sealed class StampService(IClock clock) { public string Stamp(string id) { if (string.IsNullOrWhiteSpace(id)) throw new ArgumentException("identity required"); return clock.Now.ToString("O", CultureInfo.InvariantCulture) + ":" + id; } }',
)

add(
    "API design and the prepared ASP.NET project",
    """An API exposes a contract over a transport. A useful endpoint specifies resource identity, accepted input, status outcomes and response schema. Domain validation must run before a successful status is returned. HTTP method names also communicate semantics: a safe read should not unexpectedly mutate server state.

The browser pad exercises a pure endpoint decision kernel. The checked-in ApiLab fixture supplies a real ASP.NET Core minimal API project using only the shared framework, with an in-memory catalog and explicit validation. It is a separately prepared multi-file workflow, not source accepted by the single Program.cs pad. Running its web host is deliberate and should bind loopback for local learning.""",
    "A pure mapping can return a status and body record. In the external project, MapGet and MapPost connect routes to handlers. Results.Ok, BadRequest and NotFound make transport outcomes explicit.",
    [
        ("Endpoint", "A named request contract exposed by a service."),
        ("Status mapping", "Translation of a domain outcome into HTTP semantics."),
        ("Idempotency", "Repeating a request has the same intended effect as one request."),
    ],
    (
        "Map a valid request",
        'var result = ValidateCreate("pear", 3);\nCheck(result.Status == 201 && result.Message == "accepted", "created contract");',
        "Valid input maps to the created outcome.",
        "The kernel isolates validation and status selection from host configuration.",
    ),
    (
        "Reject before claiming success",
        'Check(ValidateCreate("", 3).Status == 400, "empty identity");\nCheck(ValidateCreate("pear", -1).Status == 400, "negative quantity");',
        "Invalid requests produce 400 decisions.",
        "The response category is part of the public contract and must not disagree with domain acceptance.",
    ),
    [
        "Describe the valid request and its status/body contract.",
        "Add a maximum quantity rule and document its rejection.",
        "Run the separately prepared ApiLab project and inspect GET and POST responses.",
        "Diagnose returning 200 before input validation finishes.",
        "Test missing identity, zero quantity and unknown resource lookup.",
        "Design idempotent update behavior and explain how duplicate creation differs.",
    ],
    "An offline kernel test does not prove endpoint routing, serialization or host startup. The external project intentionally uses in-memory state, so restarting loses its sample inventory. It is not a persistence claim.",
    helpers='public record ApiDecision(int Status, string Message);\npublic static ApiDecision ValidateCreate(string name, int quantity) => string.IsNullOrWhiteSpace(name) || quantity < 0 ? new(400, "invalid") : new(201, "accepted");',
    notes="Continue with [ApiLab preparation and commands](../fixtures/ApiLab/README.md). Its complete project is separate from the classroom pad and needs a prepared .NET 10 SDK.",
)

add(
    "Security boundaries, secrets and untrusted data",
    """A security boundary is where less-trusted input receives authority: a path reaches a filesystem, text becomes SQL, or a request chooses a resource. Validation must match that destination. A string being valid JSON does not make it a safe file path or a safe authorization decision. Keep data and instructions separate.

Authentication answers who the caller is; authorization answers what that caller may do to this resource. Neither should depend on a client-supplied role string. Secrets belong in a deliberate secret source, not committed examples or logs. The offline fixture teaches an explicit allowlist policy without pretending to implement a complete identity system.""",
    "Use exact identity comparisons and explicit permission mappings. A default-deny decision rejects absent policy entries. Parsing and authorization should remain separate methods with separately testable outcomes.",
    [
        ("Authentication", "Establishing caller identity."),
        ("Authorization", "Deciding permitted actions for an established identity."),
        ("Default deny", "Rejecting access unless an explicit policy permits it."),
    ],
    (
        "Evaluate an explicit permission policy",
        'var rights = new HashSet<string>(StringComparer.Ordinal) { "report:read" };\nCheck(rights.Contains("report:read"), "allowed action");\nCheck(!rights.Contains("report:delete"), "unlisted action denied");',
        "Read is allowed and delete is denied.",
        "Absence of an entry does not become implicit permission.",
    ),
    (
        "Redact before producing diagnostics",
        'string Redact(string key, string value) => key.Equals("token", StringComparison.OrdinalIgnoreCase) ? "[redacted]" : value;\nCheck(Redact("TOKEN", "synthetic-secret") == "[redacted]", "secret omitted");\nCheck(Redact("status", "failed") == "failed", "useful nonsecret context retained");',
        "The token is replaced while a status remains visible.",
        "A minimal example makes the diagnostic contract explicit; production structured logging should use an allowlist of safe fields.",
    ),
    [
        "Separate identity from permission in a request trace.",
        "Add a second permitted read action without granting write access.",
        "Design an allowlist of fields safe to include in an import error.",
        "Diagnose trusting an isAdmin value supplied in a request body.",
        "Test missing permission and case variants according to the documented identity policy.",
        "Describe authorization checks for a resource owned by another user and the evidence each check needs.",
    ],
    "This fixture is policy reasoning, not a complete authentication system. Do not invent cryptography or store passwords in reversible form. Parameter binding and destination-specific APIs are preferable to manual escaping.",
)

add(
    "Projects, packages and reproducible builds",
    """A project file records the compilation target and build policy. Source that compiles against one framework can fail against another if it uses unavailable APIs. Pin a supported SDK policy and target framework deliberately. Package references add another versioned dependency surface, including transitive dependencies and restore behavior.

The classroom builds a fixed net10.0 project without arbitrary packages. External multi-file labs teach the project workflow explicitly: restore during preparation, build without changing dependencies, run tests, then publish a selected artifact. A portable build does not prove every architecture or operating system works. Keep actual build and runtime evidence separate.""",
    "`TargetFramework` selects net10.0. Nullable and ImplicitUsings are compile policies. `dotnet restore`, `dotnet build --no-restore`, `dotnet run --no-build` and `dotnet publish` have distinct responsibilities.",
    [
        ("Target framework", "The API/runtime contract selected by a project."),
        ("Restore", "Resolving dependency assets before build."),
        ("Publish", "Producing a deployment-oriented application output."),
    ],
    (
        "Expose environment facts without overclaiming",
        'Check(Environment.Version.Major >= 10, "declared runtime generation");\nCheck(typeof(List<int>).Assembly.GetName().Name is not null, "framework assembly identity");',
        "The running framework generation is compatible with the declared classroom target.",
        "Runtime facts are useful diagnostics but do not replace a source and project review.",
    ),
    (
        "Keep configuration explicit",
        'var configuration = new Dictionary<string, string> { ["target"] = "net10.0", ["nullable"] = "enable" };\nCheck(configuration["target"] == "net10.0" && configuration["nullable"] == "enable", "reviewed build contract");',
        "The example preserves the intended target and nullable policy.",
        "A real project fixture, rather than this metadata demonstration, is required to qualify multi-file build behavior.",
    ),
    [
        "Explain the distinct purpose of restore, build, run and publish.",
        "Build the checked-in DomainLab without adding a package.",
        "Move a pure domain type into the supplied class-library project and run its executable checks.",
        "Diagnose an API unavailable under a different target framework.",
        "Delete only the lab-owned output directories and verify a clean rebuild.",
        "Design a dependency update review including lock changes, license checks and runtime evidence.",
    ],
    "An SDK version and target framework are related but different. A successful restore is not a successful build. Do not present self-contained deployment as architecture-independent.",
    notes="Use [DomainLab](../fixtures/DomainLab/README.md) for the complete multi-project workflow. It has no third-party package dependencies.",
)

add(
    "Diagnostics, structured events and operational evidence",
    """Diagnostics should explain an operation without leaking its inputs or creating an overwhelming stream of unrelated messages. A structured event has stable fields such as operation identity, stage and outcome. These fields let a reader connect the beginning and end of one operation and distinguish a retry from a different request.

Latency, throughput and failure rate describe different aspects of a service. A low average latency can hide a bad tail. A successful process exit does not imply every record was accepted. Define observable counters from the domain contract, and ensure cancelled or unknown work is not misclassified as success. Deterministic fixtures can verify event structure while production measurements need real workloads.""",
    "Use a record for a stable event schema and serialize explicit safe fields. Stopwatch is appropriate for elapsed duration, but tests should not assert a narrow timing threshold. Keep correlation identity separate from user secrets.",
    [
        ("Structured event", "A diagnostic record with named stable fields."),
        ("Correlation identity", "A value linking observations of one operation."),
        ("Metric", "An aggregated numerical observation over a defined population."),
    ],
    (
        "Emit a safe result record",
        'var evt = new Event("fixture-1", "validate", "rejected", 2);\nstring json = JsonSerializer.Serialize(evt);\nusing var parsed = JsonDocument.Parse(json);\nCheck(parsed.RootElement.GetProperty("Outcome").GetString() == "rejected", "outcome retained");',
        "The serialized event contains an explicit rejected outcome.",
        "Named fields retain meaning without depending on a fragile formatted sentence.",
    ),
    (
        "Keep outcome counts consistent",
        'int accepted = 3, rejected = 2, submitted = 5;\nCheck(accepted + rejected == submitted, "accounted input");\nCheck((double)rejected / submitted == 0.4, "defined rejection rate");',
        "Five submitted records are fully accounted for and rejection rate is 0.4.",
        "The denominator is stated explicitly; changing it changes the metric meaning.",
    ),
    [
        "Identify safe fields and the event population.",
        "Add a stage value without adding raw input content.",
        "Instrument your import project with submitted, accepted and rejected counts.",
        "Diagnose a success metric incremented before persistence completes.",
        "Test zero submitted records and choose a no-data rate representation.",
        "Design a latency report that includes percentiles, sample count and measurement boundaries.",
    ],
    "Correlation identifiers should not contain credentials or private payloads. High-cardinality dimensions can overwhelm metric systems. Missing observations must not be silently counted as successful operations.",
    helpers="public record Event(string OperationId, string Stage, string Outcome, int Count);",
)

add(
    "Reflection, native boundaries and AOT tradeoffs",
    """Reflection inspects types and members at runtime. It is useful for tooling and frameworks, but unrestricted dynamic discovery makes deployment analysis harder. Trimming removes code that appears unused, and ahead-of-time compilation moves work from startup to build. Reflection-heavy paths may need annotations, generated metadata or a different design.

Calling native code adds an ABI boundary: layout, calling convention, string encoding, allocation ownership and error reporting must agree. This route deliberately avoids unsafe native calls in its ordinary pad. The portable examples compare reflection with explicit typed access; an external Native AOT publish remains a separate platform-specific build exercise.""",
    "`typeof(T)` gets type metadata; GetProperty returns a possibly absent member. Typed access is checked at compile time. Native AOT uses a publish property and platform toolchain requirements rather than a magic source keyword.",
    [
        ("Reflection", "Runtime inspection of program metadata."),
        ("AOT", "Ahead-of-time compilation before application execution."),
        ("ABI", "The binary-level agreement between compiled components."),
    ],
    (
        "Inspect declared metadata",
        'var property = typeof(Metric).GetProperty(nameof(Metric.Count));\nCheck(property is not null && property.PropertyType == typeof(int), "known metadata");\nCheck(typeof(Metric).GetProperty("Missing") is null, "absent member");',
        "The known property is an int and the missing property is absent.",
        "Runtime lookup needs an absence policy even when the programmer expects a member to exist.",
    ),
    (
        "Prefer typed access for a fixed contract",
        'var metric = new Metric(4);\nFunc<Metric, int> getCount = value => value.Count;\nCheck(getCount(metric) == 4, "typed projection");',
        "The fixed projection needs no string-based member lookup.",
        "A statically known relationship gives the compiler and deployment tools more information.",
    ),
    [
        "Compare compile-time and runtime checking in the two examples.",
        "Inspect a different known property and handle absence explicitly.",
        "Replace string-based access in a small report with a typed projection.",
        "Diagnose assuming dynamic reflection will remain available after trimming.",
        "Test an absent member and an unexpected member type.",
        "Plan an external Native AOT experiment stating target architecture, native prerequisites and runtime checks.",
    ],
    "Publishing AOT does not guarantee a smaller or faster application for every workload. Never guess native memory ownership. A successful ordinary managed run does not qualify an AOT or interop path.",
    helpers="public record Metric(int Count);",
    source="https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/",
)

add(
    "Modern C# features and version-aware readability",
    """Language evolution adds concise ways to express familiar contracts. Primary constructors, collection expressions and improved patterns can reduce noise, but unfamiliar syntax should be introduced by its meaning rather than used to make code look advanced. Version-aware code records the target language generation and avoids accidentally relying on a preview feature.

C# 14 accompanies .NET 10. This chapter uses established modern features supported by that target and explains the broader C# 14 release boundary through official documentation. New syntax does not relax nullability, ownership or equality rules. A code review should ask whether a feature makes the domain relationship easier to see and whether contributors can diagnose its errors.""",
    "A collection expression such as `[1, 2, 3]` is target-typed. A primary constructor supplies parameters used by members. `nameof` produces a symbol name while retaining compile-time refactoring support.",
    [
        ("Language version", "The set of syntax and semantic features accepted by the compiler."),
        ("Target typing", "Using context to determine an expression type."),
        ("Primary constructor", "Constructor parameters declared with a type definition."),
    ],
    (
        "Use a target-typed collection",
        'int[] values = [1, 2, 3];\nList<int> list = [.. values, 4];\nCheck(list.SequenceEqual(new[] { 1, 2, 3, 4 }), "collection spread");',
        "The target types select array and list representations.",
        "The compact syntax still creates concrete storage according to its target.",
    ),
    (
        "Keep constructor policy visible",
        'var scale = new Scale(3);\nCheck(scale.Apply(4) == 12, "primary constructor parameter");\nCheck(nameof(Scale.Apply) == "Apply", "symbol name");',
        "The supplied factor is used by the instance operation.",
        "Concise construction should preserve a clear relationship between input parameters and behavior.",
    ),
    [
        "Identify the target type of each collection expression.",
        "Use an empty collection expression with an explicit target.",
        "Refactor one simple class to a primary constructor without changing behavior.",
        "Diagnose copying new syntax into a project targeting an older language version.",
        "Test empty spread and zero scaling.",
        "Review a proposed new feature and justify adopting it using readability, compatibility and tooling evidence.",
    ],
    "Newer syntax is not inherently better. A collection expression is not universally lazy. Do not use latest or preview as an unexplained fix for a compiler error.",
    helpers="public sealed class Scale(int factor) { public int Apply(int value) => checked(value * factor); }",
    source="https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14",
)

add(
    "Resilience, idempotency and unknown outcomes",
    """A failed observation is not always a failed operation. A server may commit a write before the client loses its response. Retrying that write can duplicate an effect unless the protocol includes an idempotency key or another reconciliation mechanism. Exactly-once effects require careful scope and durable coordination; a retry loop alone cannot create that guarantee.

Bound retry attempts and use a failure policy that distinguishes transient, permanent and unknown outcomes. Backoff helps avoid overload but does not fix an invalid request. This offline state machine demonstrates once-per-key application under a single-threaded in-memory contract. Production durability and concurrency require additional storage and transaction evidence.""",
    "A dictionary of operation identities records prior results. Check identity before applying a side effect, and store the result with the effect under a single atomic boundary in a real durable implementation.",
    [
        ("Idempotency key", "An identity used to recognize repeated requests."),
        ("Transient failure", "A failure that may resolve without changing the request."),
        ("Reconciliation", "Determining the actual state after an uncertain observation."),
    ],
    (
        "Replay a recorded result without applying again",
        'var ledger = new Ledger();\nCheck(ledger.Apply("op-1", 3) == 3, "first effect");\nCheck(ledger.Apply("op-1", 3) == 3 && ledger.Total == 3, "replayed receipt");',
        "The repeated identity returns its prior result without increasing the total.",
        "Operation identity separates a replay from a genuinely new command.",
    ),
    (
        "Distinguish a new operation",
        'var ledger = new Ledger();\nledger.Apply("op-1", 3); ledger.Apply("op-2", 3);\nCheck(ledger.Total == 6, "distinct commands");\nbool rejected = false;\ntry { ledger.Apply("op-1", 4); } catch (InvalidOperationException) { rejected = true; }\nCheck(rejected, "same key cannot change payload");',
        "A new identity applies separately, while a changed payload under an old key is rejected.",
        "Idempotency keys need a payload consistency rule or they can hide conflicting requests.",
    ),
    [
        "Trace the effect and receipt for the repeated operation.",
        "Add a third unique operation and predict the total.",
        "Implement a result lookup that does not execute the command again.",
        "Diagnose retrying a write after an observer timeout with a fresh identity.",
        "Test repeated identity with identical and conflicting payloads.",
        "Design durable atomic storage for an effect and its receipt and state remaining failure modes.",
    ],
    "This in-memory ledger does not survive restart and is not concurrent. A production idempotency record needs retention and conflict policy. Do not describe retries as exactly-once delivery.",
    helpers='public sealed class Ledger { private readonly Dictionary<string, (int Amount, int Result)> results = new(); public int Total { get; private set; } public int Apply(string id, int amount) { if (results.TryGetValue(id, out var prior)) { if (prior.Amount != amount) throw new InvalidOperationException("payload conflict"); return prior.Result; } Total = checked(Total + amount); results.Add(id, (amount, Total)); return Total; } }',
)

add(
    "Capstone: a reviewable .NET data application",
    """The final project combines validated input, a pure domain core, deterministic reporting and explicit operational outcomes. A complete application is more than a successful algorithm: it needs a documented build, input contract, failure policy, resource ownership and evidence that its output remains meaningful after changes.

The classroom reference is the portable kernel, and the DomainLab and ApiLab fixtures provide actual multi-file boundaries. Extend them deliberately rather than pasting an entire server into the single source pad. Review normal, rejected and unknown outcomes separately. Expert practice means being able to explain the limits and diagnose an unfamiliar failure, not claiming that a finite tutorial covers every production circumstance.""",
    "Compose small functions around explicit record types. Keep parsing, validation, aggregation and presentation separate. Sort output when order is part of the contract; retain rejection evidence alongside accepted totals.",
    [
        ("Acceptance criteria", "Observable conditions defining a completed feature."),
        ("Evidence boundary", "The scope actually established by a test or run."),
        (
            "Maintainability",
            "The ability to change behavior without losing understandable contracts.",
        ),
    ],
    (
        "Build a stable valid report",
        'var report = Report(new[] { new Row("b", 2), new Row("a", 3), new Row("b", 4) });\nCheck(report.Text == "a=3;b=6" && report.Rejected == 0, "stable report");',
        "The sorted report is a=3;b=6.",
        "Sorting and aggregation have independent responsibilities and both are observable.",
    ),
    (
        "Preserve rejected data accounting",
        'var report = Report(new[] { new Row("", 2), new Row("a", -1), new Row("b", 0) });\nCheck(report.Text == "b=0" && report.Rejected == 2, "zero differs from rejected");\nCheck(Report(Array.Empty<Row>()).Text == "", "empty input");',
        "A valid zero remains in the report while two invalid rows are counted.",
        "A correct result preserves domain distinctions instead of hiding them behind a plausible total.",
    ),
    [
        "Trace every input to an accepted total or a rejection.",
        "Add an item and update only independently derived expected output.",
        "Build the external DomainLab and expose the domain contract through the ApiLab adapter.",
        "Introduce and diagnose a duplicate-aggregation, nullability or cancellation defect.",
        "Document and test empty, malformed, overflow and repeated-operation boundaries.",
        "Deliver a project README with build commands, architecture, failure policies, tests, operational limits and a proposed next extension.",
    ],
    "Do not equate a kernel assertion with API, persistence or deployment acceptance. Retain learner data and use owned temporary state for tests. A useful capstone documents what remains intentionally unsupported.",
    helpers='public record Row(string Name, int Quantity);\npublic static (string Text, int Rejected) Report(IEnumerable<Row> rows) { var valid = new List<Row>(); int rejected = 0; foreach (var row in rows) { if (string.IsNullOrWhiteSpace(row.Name) || row.Quantity < 0) rejected++; else valid.Add(row); } string text = string.Join(";", valid.GroupBy(row => row.Name).OrderBy(group => group.Key, StringComparer.Ordinal).Select(group => group.Key + "=" + group.Sum(row => row.Quantity).ToString(CultureInfo.InvariantCulture))); return (text, rejected); }',
    notes="The [DomainLab](../fixtures/DomainLab/README.md) and [ApiLab](../fixtures/ApiLab/README.md) are complete prepared project starting points. Their build and server acceptance are separate from the portable reference.",
)
