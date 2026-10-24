# ruff: noqa: E501
"""Rust composition, tests, ownership across threads and a complete project core."""

from render import lesson

lesson(
    "Traits and behavioral contracts",
    """A trait describes capabilities a type provides. A consumer can depend on the capability instead of one representation. A trait implementation must preserve units, valid inputs and failure meaning, not merely compile with the right method names. This makes substitution a behavioral question.

Static dispatch through generics can retain concrete type information, while a trait object supports runtime substitution behind a pointer. Choose based on the API relationship and storage needs. Start with a small pricing capability whose implementations share one clear contract; avoid inventing a trait for every trivial function.""",
    "`trait Pricer` declares a method. `impl Pricer for FlatPrice` supplies behavior. `&dyn Pricer` borrows a trait object and uses dynamic dispatch. The receiver &self permits inspection without consuming the implementation.",
    [
        ("Trait", "A named capability contract."),
        ("Implementation", "A type-specific realization of a trait."),
        ("Dynamic dispatch", "Selecting behavior through a trait object at runtime."),
    ],
    (
        "Use a declared capability",
        "let price = FlatPrice(3);\nlet view: &dyn Pricer = &price;\nassert_eq!(view.cost(4), 12);",
        "The borrowed trait object exposes pricing behavior.",
        "The consumer needs the capability rather than the concrete field layout.",
    ),
    (
        "Substitute a second policy",
        "let flat = FlatPrice(3);\nlet capped = CappedPrice(3, 10);\nlet prices: [&dyn Pricer; 2] = [&flat, &capped];\nassert_eq!(prices.map(|price| price.cost(4)), [12, 10]);",
        "The same interface admits an uncapped and capped policy.",
        "Both implementations preserve input and output units while varying the rule.",
    ),
    [
        "Trace the method call to each implementation.",
        "Add another flat-price value without changing the consumer.",
        "Define a small trait for a deterministic formatter.",
        "Diagnose conforming implementations that disagree about units.",
        "Test zero units and the exact cap.",
        "Choose a trait boundary for a file adapter while keeping the domain core pure.",
    ],
    "A matching signature does not establish compatible semantics. Traits and inheritance are different mechanisms. Avoid exposing implementation details merely to make a trait larger.",
    helpers="trait Pricer { fn cost(&self, units: u32) -> u32; }\nstruct FlatPrice(u32); impl Pricer for FlatPrice { fn cost(&self, units: u32) -> u32 { self.0 * units } }\nstruct CappedPrice(u32, u32); impl Pricer for CappedPrice { fn cost(&self, units: u32) -> u32 { (self.0 * units).min(self.1) } }",
)

lesson(
    "Generics, bounds and associated types",
    """Generics retain relationships between input and output types without duplicating source. A trait bound states which operations are available on the parameter. A maximum function needs ordering; a container may need no capability beyond storing its element. Excessive bounds make an API harder to reuse.

Associated types express a type chosen by an implementation, as Iterator does with Item. A generic parameter instead lets a caller choose a type for a use. These are complementary tools. Preserve meaningful relationships rather than erasing everything to a trait object and recovering types through runtime checks.""",
    "`T: Ord` constrains a type parameter. Returning T preserves the selected type. `type Item = i32` defines an associated type in an implementation. where clauses can make complex bounds easier to read.",
    [
        ("Generic parameter", "A type selected for a generic use."),
        ("Trait bound", "A capability required of an admissible type."),
        ("Associated type", "A type selected by a trait implementation."),
    ],
    (
        "Retain the result type",
        'assert_eq!(larger(3, 8), 8);\nassert_eq!(larger(String::from("apple"), String::from("pear")), "pear");',
        "The same function returns an integer or owned String.",
        "The function moves its chosen result, preserving the concrete type rather than returning an untyped object.",
    ),
    (
        "Use an associated iterator item",
        "let values = [2, 3, 4];\nlet total: i32 = values.into_iter().sum();\nassert_eq!(total, 9);\nassert_eq!(larger(5, 5), 5);",
        "The iterator's item relationship supports a typed sum.",
        "The consumer knows which values the iterator yields and chooses a compatible aggregation.",
    ),
    [
        "Identify each inferred type and required bound.",
        "Use larger with a custom ordered value type.",
        "Create a generic pair that swaps owned elements.",
        "Diagnose calling an unavailable method on an unconstrained T.",
        "State tie behavior and test equal values.",
        "Choose a generic parameter or associated type for a producer relationship and explain who selects it.",
    ],
    "Generic code still has ownership and failure contracts. Deriving Ord chooses a field-order policy that may not match domain meaning. A broad bound should not replace an explicit comparator when multiple orderings are useful.",
    helpers="fn larger<T: Ord>(left: T, right: T) -> T { if left >= right { left } else { right } }",
)

lesson(
    "Lifetime parameters and borrowed API design",
    """A lifetime parameter expresses a relationship between references. It does not allocate storage or extend an owner\'s life. A function returning one of two borrowed inputs must describe that the output is valid only where both candidate input borrows are valid. The caller and compiler then check actual uses against that relationship.

Prefer simple ownership first. Lifetime annotations become useful when an API deliberately returns views or stores borrowed data. Returning an owned value can simplify a boundary when independent lifetime is required, at an explicit copying cost. Do not force static lifetime onto data merely to suppress a diagnostic.""",
    "`fn choose<'a>(left: &'a str, right: &'a str) -> &'a str` relates the output borrow to both inputs. Elision handles common simple cases automatically. A struct field containing a reference also needs its lifetime relationship.",
    [
        ("Lifetime parameter", "A name for a reference-validity relationship."),
        ("Elision", "Compiler rules inferring common lifetime relationships."),
        ("Borrowed result", "A result whose storage remains owned by another value."),
    ],
    (
        "Return one input view",
        'let left = String::from("pear");\nlet right = String::from("watermelon");\nassert_eq!(longer(&left, &right), "watermelon");',
        "The output is a borrowed view of the longer input.",
        "The annotation prevents a caller from using the view after a required owner is gone.",
    ),
    (
        "Own a result when lifetime must separate",
        'let result = { let temporary = String::from("retained"); temporary.to_owned() };\nassert_eq!(result, "retained");',
        "The independent owned result survives the temporary scope.",
        "A deliberate owned copy changes the lifetime contract rather than pretending the borrow is static.",
    ),
    [
        "Draw the valid-use regions of both inputs and the output.",
        "Test the tie policy of longer.",
        "Write a borrowed prefix parser with the narrowest lifetime relationship.",
        "Try returning a local reference and explain why annotations cannot make it valid.",
        "Test empty inputs and use after one candidate owner leaves scope.",
        "Choose a borrowed or owned result for a cache boundary and justify cost and lifetime.",
    ],
    "Lifetime names describe relationships, not durations in seconds. Static is not a universal fix. A lifetime annotation cannot rescue a reference to destroyed local storage.",
    helpers="fn longer<'a>(left: &'a str, right: &'a str) -> &'a str { if left.len() >= right.len() { left } else { right } }",
)

lesson(
    "Iterators, laziness and consumption",
    """Iterator adapters describe transformations that execute when consumed. Map and filter generally build a recipe; collect, sum or a loop drives it. Repeated iteration is possible only if the source can be recreated or borrowed appropriately. An iterator itself holds progress and may be exhausted.

The three common vector forms make ownership visible: iter yields shared references, iter_mut yields exclusive references, and into_iter consumes owned elements. Choose the form matching the work. A lazily executed closure with side effects is harder to reason about, so keep transformations pure unless the side effect is explicitly the lesson.""",
    "`iter().filter(...).map(...)` chains borrowed transformations. collect needs an inferred or annotated target. next advances one iterator instance. into_iter consumes the collection when the collection owns non-Copy elements.",
    [
        ("Adapter", "An iterator transformation producing another iterator."),
        ("Consumer", "An operation driving iteration to obtain a result."),
        ("Exhaustion", "The state where an iterator returns no more values."),
    ],
    (
        "Consume a transformation recipe",
        "let values = vec![1, 2, 3, 4];\nlet result: Vec<_> = values.iter().copied().filter(|value| value % 2 == 0).map(|value| value * 10).collect();\nassert_eq!(result, vec![20, 40]);\nassert_eq!(values.len(), 4);",
        "The recipe selects and transforms while retaining the borrowed source.",
        "Copied turns referenced integers into independent small values before filtering and mapping.",
    ),
    (
        "Observe iterator progress",
        "let mut iterator = [2, 3].into_iter();\nassert_eq!(iterator.next(), Some(2));\nassert_eq!(iterator.next(), Some(3));\nassert_eq!(iterator.next(), None);",
        "The iterator advances and eventually exhausts.",
        "Calling next again does not restart the source automatically.",
    ),
    [
        "Identify adapters and the final consumer.",
        "Add a take limit and predict how much work is demanded.",
        "Write a borrowed transformation returning a collected result.",
        "Diagnose constructing a lazy map and expecting it to execute immediately.",
        "Test empty input and a partially consumed iterator.",
        "Choose iter, iter_mut or into_iter for three operations and justify ownership.",
    ],
    "Laziness does not mean no allocation if a later consumer collects. Reusing an exhausted iterator does not recreate it. A chain with hidden effects can execute at an unexpected boundary.",
)

lesson(
    "Closures and Fn capability bounds",
    """A closure captures surrounding values according to what its body needs. It may borrow, mutate captured state or take ownership. Fn, FnMut and FnOnce describe calling capabilities: shared repeatable calls, mutable repeatable calls and at least one consuming call respectively. These traits form a relationship, not three arbitrary spellings to try until compilation succeeds.

A move closure takes ownership of captured values, useful when work outlives the creating scope. Moving a reference still moves only that reference and does not make its borrowed target live forever. Choose capture and call contracts from the intended lifetime and mutation behavior.""",
    "`|value| value * factor` declares a closure. `move || ...` transfers captures into it. A closure mutating a captured accumulator needs mutable calling access. A function accepting FnOnce can invoke consuming behavior once.",
    [
        ("Capture", "A surrounding value or reference retained by a closure."),
        ("FnMut", "A closure capability permitting mutation during repeated calls."),
        ("FnOnce", "A capability allowing a potentially consuming call."),
    ],
    (
        "Observe mutable capture",
        "let mut count = 0;\n{ let mut add = |value| { count += value; }; add(2); add(3); }\nassert_eq!(count, 5);",
        "The closure updates its borrowed accumulator before the borrow ends.",
        "The scope makes the exclusive captured access visible.",
    ),
    (
        "Move owned data into a closure",
        'let text = String::from("owned");\nlet consume = move || text;\nlet result = consume();\nassert_eq!(result, "owned");',
        "The closure transfers its captured String to the caller once.",
        "Returning the owned capture makes this closure consuming rather than indefinitely repeatable.",
    ),
    [
        "Identify capture mode and calling capability in each example.",
        "Write a pure repeatable closure capturing an immutable factor.",
        "Implement a helper accepting FnMut for repeated transformations.",
        "Diagnose attempting to call a consuming closure twice.",
        "Test a closure with no captures and one capturing a borrowed reference.",
        "Choose capture ownership for work that will run on another thread.",
    ],
    "Move does not imply deep copy. A moved reference still has a borrowed lifetime. Avoid adding static bounds when the real solution is scoped execution or owned data.",
)

lesson(
    "Custom errors and preserving causes",
    """A public error type should expose categories a caller can act on. A string alone may be readable but makes structured recovery brittle. An enum can distinguish malformed input, missing resources and storage failure. Implementing Display supplies a human description while Error can preserve an underlying cause.

Translate errors at a meaningful boundary and avoid logging or wrapping the same failure at every layer. The question-mark operator can use From conversions to preserve composition. Never expose credentials or full private payloads merely to make an error verbose. Keep a small safe context such as a field name or operation stage.""",
    "Implement std::fmt::Display and std::error::Error for a domain error. map_err can translate a lower-level category. A match over the enum preserves structured decisions without parsing an error string.",
    [
        ("Error enum", "A closed set of meaningful failure categories."),
        ("Display", "A trait producing a human-readable representation."),
        ("Cause chain", "The relationship between a domain failure and an underlying error."),
    ],
    (
        "Preserve a domain category",
        'assert!(matches!(validated("-1"), Err(InputError::Negative)));\nassert!(matches!(validated("bad"), Err(InputError::Malformed)));',
        "Negative and malformed inputs remain separate variants.",
        "A caller can decide from the type rather than inspect a fragile message substring.",
    ),
    (
        "Render a safe message",
        'let error = InputError::Negative;\nassert_eq!(error.to_string(), "quantity must be nonnegative");\nassert_eq!(validated("3").unwrap(), 3);',
        "The message explains the rule without repeating raw input.",
        "Useful diagnostics can describe the contract while avoiding unnecessary payload disclosure.",
    ),
    [
        "Match each failure to its domain variant.",
        "Add a maximum-quantity category.",
        "Define a custom error for an importer with syntax and storage boundaries.",
        "Diagnose branching on a translated message string.",
        "Test zero, malformed and out-of-range text.",
        "Choose which layer translates an internal error into a public response and what context it may expose.",
    ],
    "A generic string loses structured recovery information. Unwrap belongs only where a nearby fixture invariant establishes success. Do not map cancellation or unknown outcomes into an ordinary empty result.",
    helpers='#[derive(Debug)] enum InputError { Malformed, Negative }\nimpl std::fmt::Display for InputError { fn fmt(&self, f: &mut std::fmt::Formatter<\'_>) -> std::fmt::Result { write!(f, "{}", match self { Self::Malformed => "quantity is not an integer", Self::Negative => "quantity must be nonnegative" }) } }\nimpl std::error::Error for InputError {}\nfn validated(text: &str) -> Result<i32, InputError> { let value = text.parse().map_err(|_| InputError::Malformed)?; if value < 0 { Err(InputError::Negative) } else { Ok(value) } }',
)

lesson(
    "Modules, visibility and a stable public surface",
    """Modules organize names and control visibility. A private implementation can change without forcing every consumer to understand it. Public items form a compatibility boundary and should expose domain meaning rather than internal representation. A crate is a compilation unit; a package can contain a library crate and executable crates.

The classroom can demonstrate modules inside one source file. A real multi-file Cargo project has separate preparation and is not uploaded through the pad. Keep that distinction explicit when a lesson introduces src/lib.rs and integration tests. Good module boundaries follow responsibilities and dependency direction, not a fixed rule that every type needs its own file.""",
    "`mod domain { ... }` declares a module. pub exposes an item to permitted external paths. use imports a name into scope without copying its implementation. pub(crate) limits visibility to the current crate.",
    [
        ("Module", "A namespace and visibility boundary."),
        ("Crate", "A Rust compilation unit."),
        ("Public API", "The surface consumers may depend on."),
    ],
    (
        "Call a reviewed public function",
        "assert_eq!(domain::double(4), 8);\nassert_eq!(domain::double(0), 0);",
        "The consumer uses the domain module interface.",
        "The implementation details remain behind its named boundary.",
    ),
    (
        "Import a name without changing ownership",
        "use domain::double;\nassert_eq!(double(3), 6);",
        "The shorter imported name refers to the same function.",
        "Use changes name resolution, not execution or data ownership.",
    ),
    [
        "Identify the public and private items.",
        "Add a private helper used by the public function.",
        "Move a pure domain operation into an inline module.",
        "Diagnose a consumer accessing a private representation field.",
        "Test the public contract without relying on internal helper names.",
        "Split a future library and executable crate by responsibility and document dependency direction.",
    ],
    "Modules are not runtime services. Excessive pub can freeze accidental implementation details into an API. A use declaration does not install a dependency.",
    helpers="mod domain { pub fn double(value: i32) -> i32 { value * 2 } }",
    notes="The later [InventoryLab Cargo project](../fixtures/InventoryLab/README.md) supplies actual multi-file source and integration tests outside the single-file pad.",
)

lesson(
    "Tests, assertions and useful counterexamples",
    """A test is strong when a plausible wrong implementation fails it. Derive expected results from the contract rather than copying the same formula into the assertion. Normal, boundary and invalid cases expose different assumptions. Properties such as idempotence can cover a wider relationship but do not replace concrete expected values.

Rust\'s built-in test harness runs functions marked test when compiling a test target. The classroom ordinary reference instead invokes always-active assertions through main. This keeps code execution distinct from a Cargo test workflow. A clean unit test does not prove filesystem configuration, network availability or deployment correctness.""",
    "assert and assert_eq remain active in ordinary builds, unlike debug_assert. A cfg(test) module belongs to a test compilation. Cargo test discovers unit, integration and documentation tests under their own contracts.",
    [
        ("Test oracle", "An independent rule deciding whether behavior is correct."),
        ("Regression case", "A fixture preserving a previously observed defect."),
        ("Property", "A relationship expected across a family of values."),
    ],
    (
        "Use independent expected cases",
        "let cases = [(-2, 0), (0, 0), (3, 3)];\nfor (input, expected) in cases { assert_eq!(input.max(0), expected); }",
        "Negative, zero and positive cases satisfy the stated clamp rule.",
        "Literal expectations make the test independent of the implementation expression.",
    ),
    (
        "Reject a plausible wrong boundary",
        "let wrong = |value: i32| if value <= 0 { 1 } else { value };\nassert_ne!(wrong(0), 0);\nassert_eq!((-4_i32).max(0).max(0), (-4_i32).max(0));",
        "Zero rejects the incorrect default while idempotence adds a second property.",
        "The property alone would not necessarily distinguish every wrong constant implementation.",
    ),
    [
        "Name a wrong implementation each case catches.",
        "Add an extreme integer input without negating its minimum value.",
        "Write table-driven checks for a quantity validator.",
        "Diagnose an assertion comparing a function call with itself.",
        "Test idempotence alongside independent boundary expectations.",
        "Separate unit, integration, compile-fail and runtime evidence for a library change.",
    ],
    "A disabled debug_assert is not a release invariant. Random cases require reproducibility and an oracle. A test that catches and ignores its own failure is misleading.",
)

lesson(
    "Files, bytes and owned cleanup",
    """A path names a filesystem location relative to a context. It is not the file data and is not permission to access arbitrary storage. A container\'s temporary worker files are distinct from durable classroom pads and progress. Use an owned temporary location for experiments and retain the user-owned data separately.

Rust resource ownership closes a File when its owner drops, but deleting a temporary pathname is a separate operation. The fixture uses create_new to avoid overwriting another file and removes only its own path. Production persistence adds atomic replacement, recovery and permission policies. A successful round trip does not establish crash durability.""",
    "OpenOptions::create_new rejects an existing path. Read and Write traits provide byte operations. write_all handles short writes, and read_to_string validates UTF-8. Drop ends handle ownership while remove_file changes the filesystem namespace.",
    [
        ("File handle", "An owned operating-system resource for open file access."),
        ("Path", "A name resolving to a filesystem location."),
        (
            "Cleanup ownership",
            "Responsibility to release only resources created or explicitly owned.",
        ),
    ],
    (
        "Round-trip owned text",
        'use std::io::{Read, Write};\nlet path = std::env::temp_dir().join(format!("rust-lesson-{}-a.txt", std::process::id()));\nlet mut file = std::fs::OpenOptions::new().write(true).read(true).create_new(true).open(&path)?;\nfile.write_all("café".as_bytes())?;\ndrop(file);\nlet mut actual = String::new();\nstd::fs::File::open(&path)?.read_to_string(&mut actual)?;\nstd::fs::remove_file(&path)?;\nassert_eq!(actual, "café");',
        "The Unicode text round-trips and the owned path is removed.",
        "The unique process-based fixture name and create_new avoid overwriting an existing file.",
    ),
    (
        "Distinguish bytes from valid text",
        'let valid = String::from_utf8(vec![0x63, 0x61, 0x66, 0xc3, 0xa9])?;\nassert_eq!(valid, "café");\nassert!(String::from_utf8(vec![0xff]).is_err());',
        "Valid UTF-8 decodes while an invalid byte sequence is rejected.",
        "A byte buffer is not automatically text, and lossy decoding is a separate policy.",
    ),
    [
        "Trace file-handle and pathname ownership separately.",
        "Write two lines with an explicit newline policy.",
        "Create an owned temporary-file round trip for a report.",
        "Diagnose assuming a relative path resolves against the repository root.",
        "Test empty bytes and invalid UTF-8.",
        "Design cleanup on every failure path using a small owned temporary-resource wrapper.",
    ],
    "This small example removes its file on the normal path; the transfer task adds RAII cleanup for early errors. Never delete arbitrary user-provided directories. Create_new avoids overwrite but is not a complete untrusted-path security model.",
)

lesson(
    "Maps, sets and algorithmic cost",
    """Collection choice follows operations and identity policy. HashMap supports expected efficient lookup; BTreeMap keeps keys ordered. HashSet represents unique membership. A list scan can be appropriate for tiny data, but repeated scans over growing inputs can dominate a workload.

Define the grain of the result and the equality rule before choosing a container. Duplicate keys may aggregate, reject or replace, and those are different contracts. Stable report order should be deliberate. Big-O explains growth under a cost model, not an exact time guarantee on every machine.""",
    "The entry API provides one lookup/update boundary. BTreeMap iteration is key-ordered. HashSet insert reports whether membership changed. Borrowed lookup can avoid allocating a new key.",
    [
        (
            "Identity policy",
            "The equality rule determining whether keys represent the same entity.",
        ),
        ("Complexity", "Growth of resource work with input size."),
        ("Ordered map", "A map whose traversal follows a key ordering."),
    ],
    (
        "Count repeated identities",
        'let mut counts = std::collections::BTreeMap::new();\nfor label in ["b", "a", "b"] { *counts.entry(label).or_insert(0) += 1; }\nassert_eq!(counts.get("b"), Some(&2));\nassert_eq!(counts.keys().copied().collect::<Vec<_>>(), vec!["a", "b"]);',
        "Duplicate b accumulates and output keys are sorted.",
        "Aggregation and presentation order are explicit parts of the chosen representation.",
    ),
    (
        "Distinguish first and duplicate insertion",
        'let mut seen = std::collections::HashSet::new();\nassert!(seen.insert("pear"));\nassert!(!seen.insert("pear"));\nassert!(!seen.contains("apple"));',
        "The set reports a duplicate without creating a second entry.",
        "Membership is a domain decision that can guide duplicate rejection or deduplication.",
    ),
    [
        "State the grain and identity policy of each result.",
        "Change duplicate handling from counting to rejection.",
        "Build a deterministic frequency report.",
        "Diagnose relying on HashMap iteration order for a saved report.",
        "Test empty input and repeated keys.",
        "Compare repeated linear membership checks with a built index, including construction and memory costs.",
    ],
    "Expected hash lookup cost is not a hard real-time guarantee. Do not persist hash values as stable identities. A collection choice does not by itself validate input or prevent overflow.",
)

lesson(
    "Scoped threads and explicit joins",
    """A thread can run concurrently with its creator and must have a clear lifetime owner. Unscoped thread spawn requires captured references to satisfy the required lifetime, often leading to owned move captures. Scoped threads instead guarantee joining before the scope returns, allowing safe borrowing of suitable local data.

Joining observes completion and panic outcomes. Do not infer completion from a sleep. Independent tasks can compute values and return them to one owner, avoiding shared mutable state. Threads are an execution mechanism, not an automatic speedup for tiny workloads or blocked external systems.""",
    "std::thread::scope bounds child lifetimes. scope.spawn creates a scoped worker. join returns its result or panic information. Immutable borrowed inputs can be shared when their types satisfy the concurrency requirements.",
    [
        ("Thread", "An independently scheduled execution context."),
        ("Join", "Waiting for and observing a thread outcome."),
        ("Scoped thread", "A thread whose lifetime is bounded by its enclosing scope."),
    ],
    (
        "Borrow local input safely",
        'let values = vec![2, 3, 4];\nlet total = std::thread::scope(|scope| { let handle = scope.spawn(|| values.iter().sum::<i32>()); handle.join().expect("fixture worker") });\nassert_eq!(total, 9);\nassert_eq!(values.len(), 3);',
        "The borrowed input remains usable after the joined scope.",
        "The scope guarantees the worker cannot outlive the owner of the borrowed vector.",
    ),
    (
        "Return independent results",
        "let total = std::thread::scope(|scope| { let left = scope.spawn(|| 2 + 3); let right = scope.spawn(|| 4 + 5); left.join().unwrap() + right.join().unwrap() });\nassert_eq!(total, 14);",
        "The parent combines two completed results.",
        "No shared writable accumulator is needed for this decomposition.",
    ),
    [
        "Identify who owns input and each thread handle.",
        "Split an array into two borrowed halves and combine their totals.",
        "Build a scoped parallel computation returning values to the parent.",
        "Diagnose dropping a handle and assuming the work finished.",
        "Test empty partitions and an intentional worker panic in a controlled external test.",
        "Choose threads or sequential work using workload size and synchronization cost.",
    ],
    "Sleep is not a synchronization guarantee. A joined panic is a distinct failure that should not become a default successful result. More threads can increase overhead and resource pressure.",
)

lesson(
    "Arc, Mutex and compound shared invariants",
    """Arc provides atomically reference-counted shared ownership. It does not make the stored value safely mutable by itself. Mutex provides mutually exclusive access to a protected value, and its guard releases the lock when dropped. Put the whole invariant inside that protected transition.

Several separately protected fields can still violate a relationship if updated under different locks or at different times. Lock ordering matters when several locks are involved. Keep protected work small and avoid calling unknown code while holding a lock. Poisoning reports a panic while a lock was held and requires an explicit recovery policy.""",
    "Arc::clone shares ownership rather than deep-copying the value. Mutex::lock returns a result containing a guard. Dereferencing the mutable guard grants access until its scope ends.",
    [
        ("Arc", "Thread-safe reference-counted shared ownership."),
        ("Mutex", "A synchronization primitive granting exclusive protected access."),
        ("Poisoning", "A signal that a panic occurred while a lock was held."),
    ],
    (
        "Protect concurrent increments",
        "use std::sync::{Arc, Mutex};\nlet count = Arc::new(Mutex::new(0));\nstd::thread::scope(|scope| { for _ in 0..4 { let count = Arc::clone(&count); scope.spawn(move || { for _ in 0..100 { *count.lock().unwrap() += 1; } }); } });\nassert_eq!(*count.lock().unwrap(), 400);",
        "All four hundred increments are retained.",
        "The lock protects the complete read-modify-write transition, not merely its final assignment.",
    ),
    (
        "Protect a relationship in one value",
        "let balances = std::sync::Mutex::new((10, 0));\n{ let mut guard = balances.lock().unwrap(); guard.0 -= 3; guard.1 += 3; }\nlet guard = balances.lock().unwrap();\nassert_eq!(*guard, (7, 3));\nassert_eq!(guard.0 + guard.1, 10);",
        "The transfer preserves the total under one protected tuple.",
        "Grouping related state makes the invariant's synchronization boundary visible.",
    ),
    [
        "Draw shared ownership separately from mutable access.",
        "Add another worker while keeping the exact expected total.",
        "Implement a locked bounded reservation operation.",
        "Diagnose protecting each half of a transfer with unrelated locks.",
        "Test zero operations and an explicitly handled poisoned lock in a separate controlled case.",
        "Choose message passing or shared locking for a service and justify the invariant owner.",
    ],
    "Arc is not a lock and clone does not copy its inner state. Holding a guard longer than needed can block unrelated work. Do not ignore poisoning without understanding whether the invariant survived.",
)

lesson(
    "Channels, backpressure and completion",
    """A channel transfers values between producers and consumers. Sending can move ownership so the receiving side becomes responsible for the value. A bounded synchronous channel limits how much work can wait in memory. Its capacity is an admission policy, not merely a performance tuning number.

A receiver can finish when all senders are dropped and buffered items are drained. Keeping an unused sender clone alive can therefore keep a consumer waiting. Join producers and observe send/receive errors deliberately. Avoid deadlock by ensuring a blocked producer has a consumer that can still run.""",
    "sync_channel creates bounded storage. try_send reports immediate full or disconnected states. send may block until capacity exists. Receiver iteration drains until sender ownership ends.",
    [
        ("Channel", "An ownership-transfer communication mechanism."),
        ("Backpressure", "A bound limiting admitted work when consumers lag."),
        ("Disconnection", "The state where the opposite channel endpoint no longer exists."),
    ],
    (
        "Make full capacity observable",
        "use std::sync::mpsc::{sync_channel, TrySendError};\nlet (send, receive) = sync_channel(1);\nsend.try_send(4)?;\nassert!(matches!(send.try_send(5), Err(TrySendError::Full(5))));\nassert_eq!(receive.recv()?, 4);",
        "One item is admitted and the next immediate send reports full capacity.",
        "The rejected value remains visible in the error instead of disappearing silently.",
    ),
    (
        "Drain before declaring completion",
        "let (send, receive) = std::sync::mpsc::sync_channel(2);\nlet worker = std::thread::spawn(move || { send.send(2).unwrap(); send.send(3).unwrap(); });\nlet total: i32 = receive.iter().sum();\nworker.join().unwrap();\nassert_eq!(total, 5);",
        "The receiver drains both values and ends after the sender is dropped.",
        "Producer lifetime and channel completion are explicitly connected.",
    ),
    [
        "Trace queue occupancy and ownership after each send.",
        "Increase capacity and predict the accepted immediate sends.",
        "Build a bounded producer-consumer report pipeline.",
        "Diagnose a receiver waiting because an unused sender clone remains alive.",
        "Test no messages and a disconnected receiver.",
        "Choose blocking, rejection or intentional dropping for a workload and explain producer evidence.",
    ],
    "Joining a producer before draining a full bounded channel can deadlock. Ignoring a failed send loses work. Channel capacity does not bound work already started outside the channel.",
)

lesson(
    "Send, Sync and type-driven concurrency safety",
    """Send describes whether ownership of a value can cross thread boundaries. Sync describes whether shared references can be safely used across threads, with the relationship that a shared reference to T is Send when T is Sync. These marker traits express safety properties, not performance or automatic synchronization.

Rc is single-threaded shared ownership; Arc supports concurrent reference counts. Interior-mutability types have different synchronization rules. The compiler rejects unsafe combinations, but user-defined unsafe implementations can bypass that protection only under a rigorous invariant. Prefer composing known safe types before declaring manual marker implementations.""",
    "A generic bound `T: Send` requires cross-thread transfer capability. `T: Sync` requires safe shared access. Thread spawn also imposes a lifetime requirement; Send and static solve different constraints.",
    [
        ("Send", "A marker permitting ownership transfer across threads."),
        ("Sync", "A marker permitting safe shared-reference access across threads."),
        ("Marker trait", "A trait expressing a property without ordinary callable methods."),
    ],
    (
        "Transfer owned data",
        'let text = String::from("owned");\nlet worker = std::thread::spawn(move || text.len());\nassert_eq!(worker.join().unwrap(), 5);',
        "Owned text crosses the thread boundary and returns its length.",
        "String's ownership and Send contract make the transfer valid without shared mutation.",
    ),
    (
        "Check capabilities at compile time",
        "fn require_send<T: Send>() {}\nfn require_sync<T: Sync>() {}\nrequire_send::<String>();\nrequire_sync::<String>();\nrequire_send::<std::sync::Arc<std::sync::Mutex<i32>>>();\nassert_eq!(std::sync::Arc::strong_count(&std::sync::Arc::new(1)), 1);",
        "The compiler accepts the declared safe capability combinations.",
        "Compile-time capability evidence is different from a runtime stress test.",
    ),
    [
        "Separate ownership transfer from shared access.",
        "Move a Vec into a worker and return a derived value.",
        "Choose a safe shared-state type for a small concurrent counter.",
        "Try sending Rc across threads and explain the diagnostic rather than adding unsafe.",
        "Test a scoped borrowed input and compare its lifetime requirement with spawn.",
        "Document why a proposed custom type is or is not Send and Sync from its members.",
    ],
    "Send does not mean simultaneous mutation is safe. Static does not mean allocated forever; it constrains borrowed references in the value. Never add unsafe impl solely to silence a compiler error.",
)

lesson(
    "Box, Rc, Weak and recursive structures",
    """Box provides owned indirection, useful when a recursive structure needs a finite-sized outer representation. Rc provides shared ownership within one thread, while Weak provides a non-owning link that may no longer upgrade to a live owner. These pointers express different lifetime contracts and should not be chosen interchangeably.

Cycles of strong reference counts can leak resources even in memory-safe Rust. A parent-child structure often needs owning edges in one direction and weak back-references in the other. RefCell permits checked interior mutation in a single thread; violating its dynamic borrowing rules panics. It does not make Rc suitable for concurrent access.""",
    "Box::new stores an owned value behind a pointer. Rc::clone increments shared ownership. Rc::downgrade creates Weak, and upgrade returns Option because the owner may have disappeared.",
    [
        ("Box", "A uniquely owned heap allocation with a known pointer-sized handle."),
        ("Rc", "Single-threaded reference-counted shared ownership."),
        ("Weak", "A non-owning link whose target may no longer exist."),
    ],
    (
        "Represent recursion through indirection",
        "let list = Node::More(2, Box::new(Node::More(3, Box::new(Node::End))));\nassert_eq!(list.total(), 5);",
        "Box makes the recursive type have a finite outer size.",
        "Each node owns the next node and releases that chain through ordinary ownership.",
    ),
    (
        "Observe a weak target disappearing",
        'let owner = std::rc::Rc::new(String::from("value"));\nlet weak = std::rc::Rc::downgrade(&owner);\nassert!(weak.upgrade().is_some());\ndrop(owner);\nassert!(weak.upgrade().is_none());',
        "The weak reference does not keep the String alive.",
        "Upgrade makes absence explicit after the final strong owner is released.",
    ),
    [
        "Draw the owning edges of the recursive list.",
        "Add another node and predict its total.",
        "Model a parent-child relationship with a weak back-reference.",
        "Diagnose an Rc cycle that keeps both objects alive.",
        "Test an empty list and upgrading a dead weak reference.",
        "Choose Box, Rc or Arc for unique, local-shared and cross-thread ownership scenarios.",
    ],
    "Memory safety does not guarantee absence of leaks. Deep recursive drops can have stack costs. RefCell moves borrow checking to runtime and remains single-threaded.",
    helpers="enum Node { End, More(i32, Box<Node>) }\nimpl Node { fn total(&self) -> i32 { match self { Self::End => 0, Self::More(value, next) => value + next.total() } } }",
)

lesson(
    "Composition project: a reusable inventory library",
    """The intermediate project separates a pure domain library from an executable adapter and integration tests. A library can expose validated operations without knowing whether its caller is a command-line tool, a browser worker or a future service. The adapter owns presentation and process behavior.

The checked-in InventoryLab is a real Cargo package using only the standard library. The pad runs the same kind of portable kernel, while Cargo build and Cargo test are deliberately separate project commands. Preserve input accounting, deterministic output and overflow behavior when extracting modules. A successful library test is not a claim that an external service or deployment is configured.""",
    "A BTreeMap result preserves sorted identity. A report record carries accepted totals and rejected count. Integration tests use the library public API, which catches accidental exposure or missing exports.",
    [
        ("Library crate", "A reusable Rust compilation unit exposing a public API."),
        ("Adapter", "Code translating external input/output into core contracts."),
        ("Integration test", "A test exercising a public boundary as a consumer."),
    ],
    (
        "Create a stable report",
        'let report = summarize(&[("b", 2), ("a", 3), ("b", 4)]);\nassert_eq!(report.0.get("b"), Some(&6));\nassert_eq!(report.0.keys().copied().collect::<Vec<_>>(), vec!["a", "b"]);',
        "The report accumulates duplicates and orders keys.",
        "The core chooses data semantics while presentation can remain a separate adapter.",
    ),
    (
        "Retain rejected input evidence",
        'let report = summarize(&[("", 2), ("a", -1), ("b", 0)]);\nassert_eq!(report.1, 2);\nassert_eq!(report.0.get("b"), Some(&0));',
        "Two invalid rows are counted and a valid zero remains present.",
        "The library contract preserves information needed by every future adapter.",
    ),
    [
        "Trace validation and accumulation as separate responsibilities.",
        "Add a report-rendering function without changing the core representation.",
        "Build and test InventoryLab through its documented Cargo commands.",
        "Diagnose moving console output into a reusable domain method.",
        "Test empty, duplicate, invalid and overflow cases.",
        "Design a second adapter that reuses the same validated library without copying its implementation.",
    ],
    "A multi-file Cargo project is not accepted by the single-file pad. Keep generated target output out of source packaging. A dependency-free project still needs the prepared compiler and standard library.",
    helpers="fn summarize<'a>(rows: &[( &'a str, i32)]) -> (std::collections::BTreeMap<&'a str, i32>, usize) { let mut totals = std::collections::BTreeMap::new(); let mut rejected = 0; for &(name, value) in rows { if name.is_empty() || value < 0 { rejected += 1; continue; } let previous: i32 = *totals.get(name).unwrap_or(&0); if let Some(total) = previous.checked_add(value) { totals.insert(name, total); } else { rejected += 1; } } (totals, rejected) }",
    notes="Use the actual [InventoryLab](../fixtures/InventoryLab/README.md) for a library, executable and integration-test workflow. It requires no third-party crates.",
)
