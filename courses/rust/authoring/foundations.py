# ruff: noqa: E501
"""Original Rust foundations: ownership is taught through observable contracts."""

from render import lesson

lesson(
    "Source, compilation and the first Rust program",
    """Rust checks source before producing a native executable. A compiler diagnostic means the program has not reached its entrypoint. A panic during execution means an operation violated a checked assumption. Successful output means only the path that actually ran completed. Keep these forms of evidence separate when learning to diagnose a program.

The classroom supplies a pinned compiler and Arrow library inside Linux Docker. The browser sends a single source file, not a Cargo project or arbitrary shell command. Start by tracing a tiny calculation and independently checking its result. This builds the habit of distinguishing observed behavior from a printed success claim.""",
    "`fn main` declares the entry function. `let` introduces a binding. `println!` is a macro, indicated by the exclamation mark. `assert_eq!` compares actual and expected values and panics on disagreement. A semicolon turns an expression into a statement whose value is discarded.",
    [
        ("Compiler", "A tool checking source and producing executable code."),
        ("Macro", "Syntax expanded before ordinary compilation."),
        ("Panic", "An execution failure indicating an unrecovered violated assumption."),
    ],
    (
        "Check a greeting",
        'let greeting = "Hello, Rust";\nassert_eq!(greeting, "Hello, Rust");\nprintln!("{greeting}");',
        "Hello, Rust appears before the lesson marker.",
        "The explicit check connects a value to its expected observation.",
    ),
    (
        "Calculate instead of copying output",
        "let rows = 4;\nlet seats_per_row = 6;\nlet seats = rows * seats_per_row;\nassert_eq!(seats, 24);\nassert_ne!(seats, rows + seats_per_row);",
        "The calculated capacity is 24, while addition would give 10.",
        "A second check rejects a plausible wrong operator rather than merely confirming that printing works.",
    ),
    [
        "Predict the greeting and final marker order.",
        "Change the greeting and keep its expected value independent.",
        "Compute the capacity of three shelves with eight books each.",
        "Remove a closing brace temporarily and classify the compiler diagnostic.",
        "Check zero shelves and one shelf.",
        "Model a three-level capacity calculation and explain every intermediate value.",
    ],
    "A compiler success does not establish business correctness. Do not replace a failing assertion with a success print. The Result-returning main wrapper is scaffolding for later error propagation; its full meaning is taught in the error chapters.",
)

lesson(
    "Bindings, mutability and type inference",
    """Rust bindings are immutable by default. `mut` grants permission to change a binding\'s value. Immutability reduces the number of state transitions a reader must consider, but it is not a substitute for understanding ownership and interior mutability introduced later. Prefer a new derived value when that expresses the operation clearly.

Type inference remains static: the compiler determines a concrete type from context. Shadowing introduces a new binding with the same name and can deliberately change its type. Reassignment instead changes the value of an existing mutable binding and must preserve its type. Use either technique to expose meaning rather than obscure where a value came from.""",
    "`let count: i32 = 3` annotates a type. `let mut total = 0` allows reassignment. `let text = text.len()` shadows the earlier name with a new binding. Integer suffixes such as `3_u64` constrain inference.",
    [
        ("Binding", "A name associated with a value."),
        ("Mutability", "Permission to change a value through a particular binding or reference."),
        ("Shadowing", "Introducing a new binding with an existing name."),
    ],
    (
        "Expose an accumulator",
        "let per_box = 4;\nlet mut total = 0;\ntotal += per_box;\ntotal += per_box;\nassert_eq!(total, 8);",
        "The mutable total changes while the fixed input remains 4.",
        "Only the value requiring state transitions is declared mutable.",
    ),
    (
        "Shadow after a representation change",
        'let count = "12";\nlet count: usize = count.len();\nassert_eq!(count, 2);\nlet explicit = 3_u64;\nassert_eq!(explicit + 1, 4);',
        "The new count is the text length, not the number twelve.",
        "Shadowing can change type, but names must still explain whether a value is text, length or parsed quantity.",
    ),
    [
        "Identify the static type and mutability of each binding.",
        "Remove unnecessary mut declarations in a small program.",
        "Write a running total with fixed input and mutable accumulator.",
        "Diagnose assigning a String to a mutable integer binding.",
        "Test an empty input string and a zero accumulator.",
        "Choose shadowing or distinct names for parsing stages and justify readability.",
    ],
    "Immutable does not mean every object reachable through a type is deeply frozen. Shadowing can conceal a units change. Type inference is not dynamic typing.",
)

lesson(
    "Integer range, checked arithmetic and numerical intent",
    """Fixed-width integers have finite ranges. Rust provides explicit checked, wrapping, saturating and overflowing arithmetic so an API can state what happens at a boundary. Do not rely on differences between debug and optimized overflow settings for business correctness. Choose the intended policy directly.

Floating-point arithmetic approximates many decimal fractions. A tolerance should reflect scale and numerical error, not hide a unit mismatch. Money often needs an integer smallest-unit representation or a separately prepared decimal library with a documented rounding policy. The standard library does not make every numerical domain exact automatically.""",
    "`checked_add` returns Option and reports overflow as None. `wrapping_add` performs modular arithmetic. `saturating_add` stays at the limit. An explicit integer type makes the tested range unambiguous.",
    [
        ("Overflow", "A mathematical result outside the representation range."),
        ("Checked arithmetic", "Arithmetic reporting an unrepresentable result explicitly."),
        ("Saturation", "Clamping an overflowing result to a type boundary."),
    ],
    (
        "Choose a visible overflow policy",
        "assert_eq!(255_u8.checked_add(1), None);\nassert_eq!(255_u8.wrapping_add(1), 0);\nassert_eq!(255_u8.saturating_add(1), 255);\nassert_eq!(2_u8.checked_add(3), Some(5));",
        "The same boundary produces absence, zero or 255 under three distinct policies.",
        "The choice is semantic and should not depend on a compiler optimization setting.",
    ),
    (
        "Keep numeric units explicit",
        "let cents_per_item: u64 = 125;\nlet quantity: u64 = 3;\nassert_eq!(cents_per_item.checked_mul(quantity), Some(375));\nlet approximate = 0.1_f64 + 0.2;\nassert!((approximate - 0.3).abs() < 1e-12);",
        "Three items cost 375 cents, while the floating fixture uses an explicit tolerance.",
        "Integer smallest units avoid accidental decimal approximation in this bounded pricing example.",
    ),
    [
        "Predict the three overflow policies.",
        "Repeat the investigation with subtraction at zero.",
        "Write a checked quantity-total calculation returning an explicit failure.",
        "Diagnose relying on debug-mode overflow behavior in production logic.",
        "Test zero, maximum and one beyond an accepted application range.",
        "Choose numeric representation, units and rounding rules for a pricing contract.",
    ],
    "Wrapping is usually wrong for counts even when it avoids a panic. A tolerance does not repair unit conversion errors. Converting with as can truncate or reinterpret values; use checked conversion when range matters.",
)

lesson(
    "String ownership, UTF-8 and text boundaries",
    """String owns a growable UTF-8 buffer; str is a string slice, commonly borrowed as &str. A text literal has static storage and can be borrowed without allocating an owned String. This distinction lets APIs accept text without unnecessarily copying it.

UTF-8 byte length differs from Unicode scalar count and user-perceived grapheme count. Rust\'s standard chars iterator visits Unicode scalar values, not full grapheme clusters. Byte slicing must use valid UTF-8 boundaries or it panics. Choose the unit required by a task before counting, slicing or limiting input.""",
    '`String::from("text")` creates owned text. `&text` can borrow it as &str. `len()` counts UTF-8 bytes, `chars().count()` counts scalars, and `get(range)` returns an optional slice if boundaries are valid.',
    [
        ("String", "An owned growable UTF-8 string."),
        ("str slice", "A borrowed view of valid UTF-8 text."),
        (
            "Unicode scalar",
            "A code point excluding surrogate values, distinct from a grapheme cluster.",
        ),
    ],
    (
        "Borrow without consuming ownership",
        'let owned = String::from("pear");\nlet borrowed: &str = &owned;\nassert_eq!(borrowed, "pear");\nassert_eq!(owned.len(), 4);',
        "Both views observe pear while the owner remains usable.",
        "Borrowing reads the existing storage without transferring its lifetime responsibility.",
    ),
    (
        "Respect byte boundaries",
        'let text = "é";\nassert_eq!(text.len(), 2);\nassert_eq!(text.chars().count(), 1);\nassert_eq!(text.get(0..1), None);\nassert_eq!(text.get(0..2), Some("é"));',
        "The scalar uses two bytes, and its first byte alone is not a valid string slice.",
        "The optional slicing API makes invalid boundaries observable without panicking.",
    ),
    [
        "Predict byte and scalar counts for the accented character.",
        "Compare an emoji and a combining-mark sequence.",
        "Write a function accepting &str and returning its byte length.",
        "Diagnose indexing a string as if every character were one byte.",
        "Test empty text and an invalid byte boundary through get.",
        "Design a text limit and state whether it counts bytes, scalars or graphemes requiring an external library.",
    ],
    "Chars are not always user-visible characters. A borrowed slice cannot outlive its owner. Use a Unicode segmentation crate only in a separately prepared project, not an undeclared pad dependency.",
)

lesson(
    "Expressions, branches and exhaustive matches",
    """Rust treats many control-flow constructs as expressions producing values. An if expression must return compatible types from its branches. This encourages deriving one result instead of initializing a mutable variable and assigning it inconsistently on several paths.

Match handles patterns and requires coverage of possibilities. A broad wildcard can be useful for invalid numeric ranges but can hide newly added enum cases. Make boundaries explicit and test adjacent inputs. A correct normal example does not prove that an inclusive versus exclusive threshold is right.""",
    '`let label = if condition { "yes" } else { "no" };` uses a branch result. The final expression in a block has no semicolon when it supplies the value. `0..=59` is an inclusive pattern range.',
    [
        ("Expression", "Code that produces a value."),
        ("Pattern", "A rule matching a value shape or category."),
        ("Exhaustiveness", "Coverage of every possible input category."),
    ],
    (
        "Choose a value with if",
        'let count = 3;\nlet label = if count > 0 { "present" } else { "empty" };\nassert_eq!(label, "present");',
        "The branch expression supplies one immutable label.",
        "Both branches return the same kind of value, so the result has one static type.",
    ),
    (
        "Classify explicit boundaries",
        'let classify = |score| match score { 0..=59 => "retry", 60..=100 => "pass", _ => "invalid" };\nassert_eq!(classify(59), "retry");\nassert_eq!(classify(60), "pass");\nassert_eq!(classify(101), "invalid");',
        "The transition at sixty and the invalid upper range are distinct.",
        "A tiny boundary fixture rejects an off-by-one policy error.",
    ),
    [
        "Identify the value produced by each branch.",
        "Change the threshold and update neighboring tests.",
        "Write a negative, zero and positive classifier.",
        "Diagnose a semicolon that changes a branch result into unit.",
        "Test both valid endpoints and one value beyond each.",
        "Choose explicit enum matches or a wildcard for a finite application state model.",
    ],
    "A semicolon can change a block value. Match arm order matters when patterns overlap. A wildcard that hides an unhandled domain state weakens maintenance feedback.",
)

lesson(
    "Loops, iterators and termination evidence",
    """A loop repeats a state transition. An invariant explains what remains true, and a termination argument explains why repetition stops. For a sum, the accumulator equals the values already processed. For a search, the inspected prefix contains no earlier match before the chosen result.

For-in consumes an iterable, so ownership of the sequence or its borrowed view matters. Iterating an array of small Copy values can look similar to borrowing a vector, but the types determine what remains available. Use iterator adapters when they expose intent, and use an explicit loop when intermediate state or early exits need explanation.""",
    "`for value in &values` borrows elements. `enumerate` supplies traversal positions. `break` exits a loop, and loop itself can return a value through break value. An exclusive range uses `0..n`.",
    [
        ("Invariant", "A property preserved by every iteration."),
        ("Iterator", "A producer of successive values."),
        ("Termination", "A reason the repeated process eventually stops."),
    ],
    (
        "Maintain a sum invariant",
        "let values = vec![2, 4, 6];\nlet mut total = 0;\nfor value in &values { total += value; }\nassert_eq!(total, 12);\nassert_eq!(values.len(), 3);",
        "The borrowed traversal totals twelve and retains the vector.",
        "The loop changes only its accumulator, not the source ownership.",
    ),
    (
        "Find the first position",
        "let values = [3, 8, 8];\nassert_eq!(values.iter().position(|value| *value == 8), Some(1));\nassert_eq!(values.iter().position(|value| *value == 9), None);",
        "The first match is position one and absence stays explicit.",
        "Position stops at the first matching element rather than returning the last repeated match.",
    ),
    [
        "Write the accumulator before and after every iteration.",
        "Skip negative values while preserving a clear invariant.",
        "Implement a first-match search with Option output.",
        "Diagnose an inclusive loop bound used as an array index.",
        "Test empty, singleton and repeated-match sequences.",
        "Design a bounded retry loop and state both its progress measure and its effect policy.",
    ],
    "An iterator can consume values or borrow them depending on its construction. A position is not automatically a valid index in a different collection. Avoid unbounded loops without a deliberate stop and cancellation policy.",
)

lesson(
    "Functions, return values and contracts",
    """A function should expose accepted inputs, result meaning, mutation and failure. A compact signature cannot tell the whole story, so write the domain contract beside it. Begin with pure computations that return a value; their behavior is easy to test because they do not depend on hidden state.

Rust makes ownership transfer part of an argument type. Passing an integer copies it, while passing an owned String normally moves it. Borrowing can let a function inspect text while leaving ownership with the caller. Choose the signature from the needed capability rather than adding clones until the compiler is quiet.""",
    "`fn double(value: i32) -> i32` declares input and output types. A final expression returns its value without a semicolon. `&str` accepts borrowed text, including literals and owned String views.",
    [
        ("Parameter", "A typed input in a function declaration."),
        ("Return type", "The type of a function result."),
        ("Borrowed interface", "An interface accepting temporary access rather than ownership."),
    ],
    (
        "Return a derived integer",
        "fn double(value: i32) -> i32 { value * 2 }\nlet original = 7;\nassert_eq!(double(original), 14);\nassert_eq!(original, 7);",
        "The integer remains available after the call.",
        "The Copy semantics of this small value permit reuse without transferring an owned allocation.",
    ),
    (
        "Accept different text owners",
        'fn starts_with_p(text: &str) -> bool { text.starts_with(\'p\') }\nlet owned = String::from("pear");\nassert!(starts_with_p(&owned));\nassert!(!starts_with_p("apple"));\nassert_eq!(owned, "pear");',
        "One borrowed interface accepts owned text and a literal.",
        "The function needs only a read-only text view, so taking String would impose unnecessary ownership transfer.",
    ),
    [
        "Identify which arguments are copied and which are borrowed.",
        "Add a function computing a labeled length from &str.",
        "Write a pure rectangle-area function with a documented valid range.",
        "Diagnose an accidental semicolon on the final return expression.",
        "Test empty text and zero dimensions.",
        "Choose owned or borrowed inputs for an API that stores data after the call.",
    ],
    "A reference is not permission to retain data beyond its lifetime. Pure-looking names can hide side effects. Do not clone an entire buffer when a borrow expresses the actual requirement.",
)

lesson(
    "Ownership, moves and explicit cloning",
    """Every owned value has a responsibility for releasing its resources. Moving a non-Copy value transfers that responsibility to another binding or operation. The old binding can no longer be used as though it still owns the value. This prevents accidental double release and many use-after-free errors before execution.

Clone explicitly asks for a value-level duplication defined by the type. Cloning a String duplicates its text storage; cloning an Arc later duplicates shared ownership rather than deep-copying its contents. Copy is a stricter implicit duplication capability used by suitable simple types. Learn the semantic distinction instead of assuming every assignment copies everything.""",
    "Assignment of String moves ownership. `.clone()` requests the type's duplication behavior. A function taking String owns its argument and may retain or release it. Returning the String transfers ownership back.",
    [
        ("Owner", "The value responsible for a resource lifetime."),
        ("Move", "Transfer of ownership that invalidates the prior use path."),
        ("Clone", "An explicit type-defined duplication operation."),
    ],
    (
        "Move ownership to a new binding",
        'let first = String::from("pear");\nlet second = first;\nassert_eq!(second, "pear");\n// Using first here would be a compile error: ownership moved.',
        "The new binding owns the text.",
        "The reference intentionally does not compile an invalid old-binding access; the practice task asks the learner to inspect that diagnostic separately.",
    ),
    (
        "Clone only when two owners are needed",
        'let first = String::from("pear");\nlet mut second = first.clone();\nsecond.push(\'s\');\nassert_eq!(first, "pear");\nassert_eq!(second, "pears");',
        "The cloned String can change independently.",
        "The explicit clone makes the allocation and independent ownership decision visible.",
    ),
    [
        "Draw ownership before and after the move.",
        "Temporarily read first after its move and preserve the compiler diagnostic.",
        "Write a function taking and returning an owned String.",
        "Diagnose adding clones everywhere instead of choosing a borrowed interface.",
        "Compare String movement with copying an i32.",
        "Explain whether a function should borrow, clone or take ownership when retaining data for later use.",
    ],
    "Clone does not universally mean deep copy. A move can be optimized without changing its ownership semantics. Compiler rejection of a use-after-move is useful evidence, not an obstacle to suppress.",
)

lesson(
    "Shared borrowing and scope",
    """A shared reference grants temporary read access without taking ownership. Several shared borrows can coexist when no conflicting mutation occurs. The owner must remain alive while borrowed data can still be used. Rust\'s borrow checker tracks these relationships through control flow, often ending a borrow after its last use rather than the end of the entire lexical block.

A borrowed API is useful for inspection, searching and parsing views. It avoids unnecessary allocation while preserving caller ownership. The lifetime constraint is not a runtime timer: it is a compile-time relationship between valid uses. Returning a reference to a local value is invalid because the owner disappears when the function returns.""",
    "`&value` creates a shared reference. Dereferencing with `*reference` accesses a referenced scalar when needed. Auto-dereferencing makes many method calls convenient. A return type `&str` must refer to storage owned elsewhere for a sufficient lifetime.",
    [
        ("Shared borrow", "Temporary read access without ownership transfer."),
        ("Lifetime", "The region in which a reference remains valid."),
        ("Last use", "The final operation requiring a borrow to remain active."),
    ],
    (
        "Borrow more than once",
        'let text = String::from("pear");\nlet first = &text;\nlet second = &text;\nassert_eq!(first.len() + second.len(), 8);\nassert_eq!(text, "pear");',
        "Two readers coexist and the owner remains intact.",
        "Both references inspect the same allocation without taking release responsibility.",
    ),
    (
        "Return a borrowed view",
        'fn first_word(text: &str) -> &str { text.split_whitespace().next().unwrap_or("") }\nlet sentence = String::from("pear apple");\nassert_eq!(first_word(&sentence), "pear");\nassert_eq!(first_word(""), "");',
        "The result is a view into caller-owned text, with an explicit empty policy.",
        "The function returns a slice whose validity depends on the input owner.",
    ),
    [
        "Identify the owner and both readers.",
        "Add another read-only inspection without cloning.",
        "Write a last-word function returning a borrowed slice.",
        "Try returning a reference to a local String and explain the compiler rejection.",
        "Test empty text and a single word.",
        "Choose a borrowed view or owned result for a parser whose caller may discard the input immediately.",
    ],
    "A reference cannot make its owner live longer by declaration alone. Borrow duration follows actual use constraints. Avoid converting every slice to String unless independent ownership is needed.",
)

lesson(
    "Exclusive borrowing and mutation boundaries",
    """An exclusive reference grants mutation while preventing conflicting access to the same storage. The common rule is either shared readers or one exclusive borrower at a time. This is a capability rule about access, not a claim that the operating system has locked memory.

Small scopes make mutation ownership easier to see. After an exclusive borrow\'s last use, the owner can be used again. APIs such as split_at_mut safely produce disjoint mutable regions because they establish that the regions do not overlap. Do not reach for unsafe code merely because the compiler cannot infer a relationship you have not expressed.""",
    "`&mut value` creates exclusive access and the original binding must permit mutation. A function taking &mut T may update the borrowed value but does not own its eventual destruction. split_at_mut proves disjoint slices.",
    [
        ("Exclusive borrow", "Temporary access permitting mutation without conflicting aliases."),
        ("Aliasing", "Several paths referring to the same storage."),
        ("Disjoint regions", "Storage ranges that do not overlap."),
    ],
    (
        "Mutate through one explicit borrower",
        'fn append_mark(text: &mut String) { text.push(\'!\'); }\nlet mut text = String::from("ready");\nappend_mark(&mut text);\nassert_eq!(text, "ready!");',
        "The caller retains ownership and observes the deliberate mutation.",
        "The function receives mutation capability for the duration of the call.",
    ),
    (
        "Mutate two proven-disjoint regions",
        "let mut values = [1, 2, 3, 4];\nlet (left, right) = values.split_at_mut(2);\nleft[0] = 9;\nright[0] = 8;\nassert_eq!(values, [9, 2, 8, 4]);",
        "The two slices mutate separate halves safely.",
        "The standard library API establishes disjointness instead of relying on two potentially overlapping index borrows.",
    ),
    [
        "Trace who may access text during the mutable call.",
        "Add a second mutation after the first borrow ends.",
        "Write a function swapping the ends of a mutable slice safely.",
        "Create conflicting mutable borrows and explain the compiler diagnostic.",
        "Test an empty slice and a split at either endpoint.",
        "Design an API that exposes only the smallest mutable region needed by a transformation.",
    ],
    "An exclusive borrow is not a thread lock. More mut annotations do not solve aliasing conflicts. Prefer safe disjointness APIs to manually asserting pointer safety.",
)

lesson(
    "Slices, arrays and vector growth",
    """An array has a compile-time length as part of its type. A Vec owns a growable allocation. A slice borrows a contiguous region and carries its length without owning that allocation. Accepting &[T] lets a function read arrays and vectors through one interface.

Vector growth can reallocate storage, which explains why a borrow into a vector cannot remain live while a conflicting push changes its allocation. Capacity reserves room but does not create initialized logical elements. Indexing panics outside the valid range; get returns Option when absence is a normal possibility.""",
    "`[i32; 3]` is an array of exactly three integers. `Vec<i32>` owns a variable-length sequence. `&[i32]` is a borrowed slice. len and capacity describe different properties.",
    [
        ("Array", "A fixed-length value whose type includes its length."),
        ("Vector", "An owned growable contiguous sequence."),
        ("Slice", "A borrowed contiguous view carrying a length."),
    ],
    (
        "Accept arrays and vectors uniformly",
        "fn total(values: &[i32]) -> i32 { values.iter().sum() }\nassert_eq!(total(&[2, 3, 4]), 9);\nassert_eq!(total(&vec![1, 2]), 3);\nassert_eq!(total(&[]), 0);",
        "One slice interface accepts several owning representations.",
        "The function requires read access, not a particular allocation strategy.",
    ),
    (
        "Separate capacity from logical elements",
        "let mut values: Vec<i32> = Vec::with_capacity(10);\nassert_eq!(values.len(), 0);\nassert!(values.capacity() >= 10);\nvalues.push(7);\nassert_eq!(values.get(0), Some(&7));\nassert_eq!(values.get(1), None);",
        "Reserved storage still contains zero logical elements until push.",
        "The optional lookup exposes absence instead of indexing uninitialized capacity.",
    ),
    [
        "Identify owner, length and borrowed view in each call.",
        "Use a subslice and predict its total.",
        "Implement a maximum function accepting a slice and returning Option.",
        "Diagnose keeping an element reference live across a conflicting vector push.",
        "Test empty, singleton and out-of-range get cases.",
        "Choose an array, Vec or slice for stored state, function input and fixed-size coordinates.",
    ],
    "Capacity is not a valid index limit. A slice does not extend its owner's lifetime. Avoid accepting &Vec when a slice expresses the actual requirement.",
)

lesson(
    "Structs, methods and validated state",
    """A struct groups named fields into a domain value. Methods express operations on that value, and their receiver states whether they borrow, mutate or consume it. A constructor function can validate inputs before creating a valid instance. Private fields prevent callers from bypassing that constructor or later invariants.

Failure atomicity means a rejected operation leaves the prior valid state unchanged. Check all rejection conditions before mutation or build a candidate value and commit it only after validation. Encapsulation is useful because it keeps this reasoning in one place rather than requiring every caller to remember the rule.""",
    "`impl Inventory` contains associated functions and methods. `&self` reads, `&mut self` mutates, and `self` consumes. An associated constructor such as new can return Option or Result.",
    [
        ("Struct", "A nominal type with named fields."),
        ("Receiver", "The self parameter describing access to an instance."),
        ("Invariant", "A rule maintained by every externally visible valid state."),
    ],
    (
        "Reserve within an invariant",
        "let mut inventory = Inventory::new(5);\nassert!(inventory.reserve(2));\nassert_eq!(inventory.stock(), 3);",
        "A successful reservation leaves three units.",
        "The method owns both the affordability check and the subtraction.",
    ),
    (
        "Reject without partial mutation",
        "let mut inventory = Inventory::new(3);\nassert!(!inventory.reserve(4));\nassert_eq!(inventory.stock(), 3);\nassert!(inventory.reserve(0));",
        "Excess demand is rejected and zero is an allowed no-op.",
        "Validation occurs before changing state, preserving the prior valid value.",
    ),
    [
        "Explain the capability expressed by each method receiver.",
        "Add a checked restock method.",
        "Create a bounded counter with private state and validated operations.",
        "Diagnose subtracting before checking available stock.",
        "Test zero, exact-stock and excess reservations.",
        "Choose a consuming method when an operation should make the prior state unavailable.",
    ],
    "Public writable fields can bypass invariants. Unsigned types prevent negative representation but do not prevent overflow. A method taking &mut self is not automatically safe for unsynchronized sharing across threads.",
    helpers="struct Inventory { stock: u32 }\nimpl Inventory { fn new(stock: u32) -> Self { Self { stock } } fn stock(&self) -> u32 { self.stock } fn reserve(&mut self, amount: u32) -> bool { if amount > self.stock { return false; } self.stock -= amount; true } }",
)

lesson(
    "Enums and state-specific payloads",
    """An enum represents one case from a declared set. Each case can carry the data relevant to that state. This prevents impossible combinations such as a success flag paired with an error message and no result. Match exposes the state distinction and binds the appropriate payload.

Use enums for meaningful alternatives, not merely to avoid strings. Adding a state requires reviewing transitions and consumers. Exhaustive matching helps the compiler identify affected code. A wildcard may be justified for intentionally open categories, but it weakens feedback when the domain is meant to be closed.""",
    "`enum Outcome { Ready(u32), Failed(String) }` declares alternatives. `match value` consumes or borrows according to the matched expression. Matching `&value` can inspect owned payloads without moving them.",
    [
        ("Enum variant", "One allowed alternative of an enum type."),
        ("Payload", "Data associated with a particular state."),
        ("Exhaustive match", "Handling every declared alternative."),
    ],
    (
        "Render a success payload",
        'let value = Outcome::Ready(4);\nassert_eq!(render(&value), "count:4");',
        "The ready state carries a count rather than an unrelated optional field.",
        "The rendering function borrows the state and extracts only the matching payload.",
    ),
    (
        "Render a distinct failure",
        'let value = Outcome::Failed(String::from("invalid"));\nassert_eq!(render(&value), "error:invalid");\nassert!(matches!(value, Outcome::Failed(_)));',
        "Failure preserves its reason and remains a distinct state.",
        "The model cannot simultaneously be both ready and failed.",
    ),
    [
        "Identify which payload is valid in each state.",
        "Add a Loading variant and update every exhaustive consumer.",
        "Model an import as pending, completed or rejected with state-specific information.",
        "Diagnose a collection of optional fields that permits contradictory states.",
        "Test every declared variant.",
        "Design valid transitions between states and explain which transitions should be rejected.",
    ],
    "Matching an owned enum can move its String payload. Use a borrowed match when retaining the original is intended. Avoid a wildcard that silently renders new domain states as success.",
    helpers='enum Outcome { Ready(u32), Failed(String) }\nfn render(value: &Outcome) -> String { match value { Outcome::Ready(count) => format!("count:{count}"), Outcome::Failed(reason) => format!("error:{reason}") } }',
)

lesson(
    "Option and preserving missing information",
    """Option represents either Some(value) or None. It is appropriate when absence is an expected outcome, such as a lookup finding no record. A real zero remains Some(0), keeping it distinct from missing information. This type-level distinction prevents sentinel values from leaking into valid calculations.

Unwrap asserts that absence is impossible and panics otherwise. Use it only when a nearby invariant or authored fixture makes that claim clear. Pattern matching, map and and_then let code retain absence through transformations until a boundary deliberately chooses a fallback. Choosing a default too early can erase information the caller needs.""",
    "`Option<T>` carries a present T or absence. `if let Some(value)` handles the present case. map transforms a present value; and_then chains an operation already returning Option. unwrap_or supplies a deliberate fallback.",
    [
        ("Option", "A type representing expected presence or absence."),
        ("Some", "The present case containing a value."),
        ("Fallback", "A deliberate replacement selected for absence."),
    ],
    (
        "Keep zero distinct from missing",
        "let measured = Some(0);\nlet missing: Option<i32> = None;\nassert_ne!(measured, missing);\nassert_eq!(measured.map(|value| value + 1), Some(1));",
        "A measured zero remains present and transforms to one.",
        "Absence is a separate case, not a special numeric value.",
    ),
    (
        "Propagate absence until a boundary",
        "let values = [2, 4];\nassert_eq!(values.get(9).map(|value| value * 2), None);\nassert_eq!(values.get(9).copied().unwrap_or(-1), -1);",
        "An absent lookup stays absent until the explicit display fallback.",
        "The fallback is not inserted into the collection and should not be mistaken for a valid measurement.",
    ),
    [
        "Predict mapping Some(0) and None.",
        "Render missing data as an unknown label instead of a numeric sentinel.",
        "Write a first-valid-item lookup returning Option.",
        "Diagnose unwrap on an ordinary not-found path.",
        "Test empty collections, present zero and out-of-range lookup.",
        "Choose when absence should remain optional and when it should become a domain error.",
    ],
    "None does not explain a failure reason; use Result when a reason matters. A default can hide missing data. Avoid converting every optional to a panic merely to shorten control flow.",
)

lesson(
    "Result, error propagation and recoverable failure",
    """Result distinguishes Ok(value) from Err(error). It is appropriate when failure has a reason that a caller should inspect or propagate. Parsing text naturally returns a Result because malformed input is different from an ordinary missing lookup. A robust boundary should preserve the distinction between syntax failure and domain rejection.

The question-mark operator returns early with an error while continuing with the successful value. It is a control-flow shortcut with a clear type contract, not an instruction to ignore failure. The main wrapper used in this course can propagate errors to an unsuccessful process outcome. Production APIs should choose error types that expose useful categories without leaking sensitive raw input.""",
    "`Result<T,E>` carries a success type and an error type. `?` unwraps success or converts and returns an error. map_err translates an error deliberately. match handles both paths explicitly.",
    [
        ("Result", "A success-or-error value with typed payloads."),
        ("Propagation", "Returning a failure to a caller rather than hiding it."),
        ("Error category", "A meaningful classification for recovery or reporting."),
    ],
    (
        "Parse and validate separately",
        'assert_eq!(parse_quantity("3"), Ok(3));\nassert_eq!(parse_quantity("bad"), Err("not an integer"));\nassert_eq!(parse_quantity("-1"), Err("negative quantity"));',
        "Malformed text and negative quantity preserve different reasons.",
        "Parsing establishes a representation; the second check enforces the domain.",
    ),
    (
        "Collect only explicitly accepted values",
        'let inputs = ["2", "bad", "3"];\nlet accepted: Vec<_> = inputs.iter().filter_map(|text| parse_quantity(text).ok()).collect();\nassert_eq!(accepted, vec![2, 3]);\nassert_eq!(inputs.len() - accepted.len(), 1);',
        "Two accepted values and one rejection are accounted for.",
        "Converting to Option is deliberate here because the separate count retains rejection evidence; a real importer may need the full reasons.",
    ),
    [
        "Trace the success, parse-error and domain-error paths.",
        "Add an application maximum quantity with a separate error category.",
        "Write a function using ? to compose two fallible steps.",
        "Diagnose replacing every Err with zero.",
        "Test empty, zero, negative and overflowing textual input.",
        "Choose a public error enum and explain which internal details should remain private.",
    ],
    "Calling .ok discards the error reason. A catch-all fallback can turn data loss into success. Panic is generally the wrong interface for expected invalid external input.",
    helpers='fn parse_quantity(text: &str) -> Result<i32, &\'static str> { let value: i32 = text.parse().map_err(|_| "not an integer")?; if value < 0 { return Err("negative quantity"); } Ok(value) }',
)

lesson(
    "Foundation project: a validated inventory report",
    """The first project joins parsing, ownership, collection lookup and aggregation. Input validation decides which records enter the domain. Accepted duplicate names accumulate; rejected records are counted separately. A missing or malformed quantity must not become a valid zero merely because zero is convenient.

The fixture uses in-memory text and a sorted map so it remains deterministic and offline. BTreeMap provides ordered keys, while a HashMap would need explicit sorting for presentation. Keep parsing and calculation separate enough to diagnose the first incorrect state. Later chapters extend this kernel with files, concurrency and Arrow arrays.""",
    "split_once separates a simple two-field fixture. A second comma is rejected by integer parsing. BTreeMap entry gives one owned update point for a key. checked_add preserves overflow as a rejected record.",
    [
        ("Admission", "The decision to accept a record into domain processing."),
        ("Aggregation", "Combining accepted values by identity."),
        ("Deterministic report", "Output whose ordering and meaning are explicitly controlled."),
    ],
    (
        "Aggregate repeated valid items",
        'let (totals, rejected) = import_rows(&["pear,2", "apple,3", "pear,4"]);\nassert_eq!(totals.get("pear"), Some(&6));\nassert_eq!(totals.get("apple"), Some(&3));\nassert_eq!(rejected, 0);',
        "Pear totals six and apple totals three.",
        "Duplicate identities accumulate only after their values are admitted.",
    ),
    (
        "Retain valid zero and rejection counts",
        'let (totals, rejected) = import_rows(&["pear,0", "bad", "apple,-1", "pear,no"]);\nassert_eq!(totals.get("pear"), Some(&0));\nassert_eq!(rejected, 3);\nassert!(import_rows(&[]).0.is_empty());',
        "A valid zero remains present while three malformed records are excluded.",
        "This preserves absence, zero and rejection as different meanings.",
    ),
    [
        "Trace each record through parsing and accumulation.",
        "Add one duplicate and predict its new total.",
        "Render the sorted map with an explicit rejected count.",
        "Diagnose silently replacing a parse error with zero.",
        "Test empty names, extra separators, overflow and empty input.",
        "Design a structured import result retaining safe per-record failure categories.",
    ],
    "This is a deliberately simple comma-separated fixture, not a complete CSV parser with quoting. Do not advertise split_once as general CSV support. The later Arrow CSV chapter uses an actual parser.",
    helpers="fn import_rows(lines: &[&str]) -> (std::collections::BTreeMap<String, u32>, usize) { let mut totals = std::collections::BTreeMap::new(); let mut rejected = 0; for line in lines { let Some((name, quantity)) = line.split_once(',') else { rejected += 1; continue; }; let Ok(quantity) = quantity.parse::<u32>() else { rejected += 1; continue; }; if name.trim().is_empty() { rejected += 1; continue; } let previous: u32 = *totals.get(name).unwrap_or(&0); let Some(total) = previous.checked_add(quantity) else { rejected += 1; continue; }; totals.insert(name.to_owned(), total); } (totals, rejected) }",
)
