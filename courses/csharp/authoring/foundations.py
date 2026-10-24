# ruff: noqa: E501
# Long original prose and embedded programs are content, not Python expression layout.
"""Original C# foundations: observations before abstractions."""

from render import lesson

lesson(
    "Source, compilation and the first observable result",
    """A program is text until a compiler translates it into a form the runtime can execute. In .NET, the SDK supplies build tools; the runtime loads managed code and supplies services such as allocation and exceptions. Installing only a runtime is insufficient for compiling new source. The classroom prepares the SDK inside Linux Docker, so the host browser does not need a C# compiler.

The first skill is distinguishing three outcomes: a compiler diagnostic means the program did not start; an exception means execution reached a failing operation; the expected printed result means a particular path completed. A message saying success proves nothing about an unchecked calculation. We therefore attach a small explicit condition to every reference and make false conditions terminate unsuccessfully.""",
    "`using System;` makes framework names available without their namespace prefix. `class Program` groups members. `static Main` is an entrypoint that needs no object instance. Braces delimit a body; a semicolon ends a statement. `Console.WriteLine` prints one line. The wrapper uses `async Task Main` to keep one entrypoint shape throughout the route; asynchronous work is explained later. For now, trace the statements from top to bottom.",
    [
        ("Source", "Human-readable program text."),
        ("Compiler", "A tool that checks language rules and emits runnable managed code."),
        ("Entrypoint", "The method the runtime calls to begin the program."),
    ],
    (
        "A checked greeting",
        'string greeting = "Hello, C#";\nCheck(greeting.Length == 9, "greeting length");\nConsole.WriteLine(greeting);',
        "Hello, C# appears before the lesson marker.",
        "The length check establishes a specific claim before printing. Spaces and punctuation count as characters in this ASCII fixture.",
    ),
    (
        "A calculation instead of a hardcoded message",
        'int boxes = 3;\nint itemsPerBox = 4;\nint total = boxes * itemsPerBox;\nCheck(total == 12, "computed total");\nCheck(total != boxes + itemsPerBox, "multiplication is not addition");',
        "The total is 12, while adding the two inputs gives 7.",
        "The second condition rejects a plausible wrong operator. This is stronger evidence than printing an unexplained success word.",
    ),
    [
        "Predict the greeting length, including its space and punctuation, before running Example A.",
        "Change the greeting and update its independently counted expected length.",
        "Write a program calculating the number of seats in four rows of six seats. Check 24 explicitly.",
        "Temporarily remove a semicolon and classify the diagnostic as compilation rather than runtime failure. Restore it.",
        "Compare zero rows with one row and explain why multiplication handles both without a branch.",
        "Model boxes containing packets containing items. Explain each intermediate value and check the final product.",
    ],
    "Printing a copied expected number skips the calculation. A missing brace can produce several later diagnostics, so repair the first structural problem before interpreting the rest. Do not treat the lesson marker as a replacement for inspecting the greeting or invariant.",
)

lesson(
    "Types, variables and explicit conversions",
    """A type describes the values an expression may hold and the operations available on those values. `int` represents a bounded whole number; `double` represents a binary floating-point approximation; `bool` represents a logical decision. A variable is a named storage location. Reassigning a variable changes its stored value, not its declared type.

`var` asks the compiler to infer a static type from the initializer. It does not make the variable dynamically typed. Conversions deserve attention because they can widen a range, lose fractional information, or fail. Put conversion at a visible boundary rather than scattering casts through a formula. First choose the meaning and units of the result, then choose its type.""",
    "`int count = 7` declares and initializes. `var inferred = 7` also produces an int. `(double)count` converts before an operator uses the value. `int.TryParse(text, out int parsed)` returns success separately from the output value; a failed parse must not silently mean a real zero.",
    [
        ("Static type", "The compile-time classification of an expression."),
        ("Conversion", "A change from one type representation to another."),
        ("Try pattern", "A Boolean success result paired with an output value."),
    ],
    (
        "Division depends on operand types",
        'int whole = 7 / 2;\ndouble fraction = (double)7 / 2;\nCheck(whole == 3, "integer division");\nCheck(fraction == 3.5, "floating division");',
        "The integer result is 3 and the floating result is 3.5.",
        "Converting after integer division would preserve the already truncated result. Operand conversion must happen before division.",
    ),
    (
        "Parse an external representation",
        'bool accepted = int.TryParse("42", out int value);\nbool rejected = int.TryParse("forty-two", out _);\nCheck(accepted && value == 42, "valid count");\nCheck(!rejected, "invalid count is not zero");',
        "42 parses successfully; words fail without an exception.",
        "The success flag carries information that a default integer cannot. Validation belongs where text becomes a typed value.",
    ),
    [
        "Predict the type and value of 7/2, 7/2.0 and (double)(7/2).",
        "Change the operands to 8 and 2 and explain why that input hides the truncation difference.",
        "Write a TryParse-based validator accepting only nonnegative whole-number quantities.",
        "Diagnose a conversion performed after integer division. Produce a fractional counterexample.",
        "Test empty text, zero, a negative number and a number outside the int range.",
        "Design an input boundary for a percentage and document its accepted textual and numeric ranges.",
    ],
    "An inferred type is still static. A cast is not a validation policy. `TryParse` alone accepts negative integers, so domain rules such as nonnegative quantities need a second condition.",
)

lesson(
    "Numeric range, checked overflow and decimal amounts",
    """Arithmetic has representation limits. An `int` has a finite range, so mathematically valid addition may overflow. C# supports checked contexts that reject integral overflow and unchecked contexts that wrap. Neither behavior should be chosen accidentally for business quantities. Floating-point arithmetic instead approximates most decimal fractions, so equality of independently calculated doubles often needs a scale-aware tolerance.

Use `decimal` when a decimal representation matches the domain, such as many monetary calculations. Decimal arithmetic still has finite precision and range. Specify rounding at a business boundary, including its midpoint rule, rather than rounding every intermediate operation. Keep currency and units explicit: a bare number does not identify what it measures.""",
    "`checked(expression)` asks for integral overflow detection in that expression. The `m` suffix selects decimal, while `0.1` defaults to double. `Math.Round(amount, 2, MidpointRounding.ToEven)` records both precision and tie policy.",
    [
        ("Overflow", "A result outside the representation range."),
        ("Decimal", "A base-ten-oriented finite precision numeric type."),
        ("Rounding policy", "A rule selecting a representable result at a stated precision."),
    ],
    (
        "Reject overflowing counts",
        'bool overflowed = false;\ntry { int large = int.MaxValue; _ = checked(large + 1); }\ncatch (OverflowException) { overflowed = true; }\nCheck(overflowed, "overflow must be visible");\nCheck(checked(100 + 20) == 120, "normal addition");',
        "The maximum int plus one is rejected; 100 plus 20 is accepted.",
        "The normal and failure paths separate an exceptional boundary from ordinary arithmetic.",
    ),
    (
        "Preserve decimal intent",
        'decimal amount = 0.1m + 0.2m;\nCheck(amount == 0.3m, "decimal tenths");\nCheck(Math.Round(2.345m, 2, MidpointRounding.ToEven) == 2.34m, "even midpoint");\nCheck(Math.Round(2.345m, 2, MidpointRounding.AwayFromZero) == 2.35m, "away midpoint");',
        "Two valid midpoint policies produce 2.34 and 2.35.",
        "A rounding difference can be a policy disagreement rather than a compiler defect. Write the expected rule before the implementation.",
    ),
    [
        "Predict which arithmetic operation throws and explain the representation boundary.",
        "Replace maximum plus one with minimum minus one and check the failure.",
        "Calculate a decimal subtotal and tax, rounding only the final payable amount.",
        "Diagnose a price parsed as double and later converted to decimal. Explain where approximation entered.",
        "Compare midpoint values immediately below, at and above the rounding boundary.",
        "Design a quantity and currency contract that states overflow, rounding and invalid-input behavior.",
    ],
    "`checked` does not turn floating-point arithmetic into exact decimal arithmetic. Rounding before aggregation can produce a different total than rounding afterward. Never use an unexplained tolerance to hide a unit mismatch.",
)

lesson(
    "Strings, interpolation and Unicode text",
    """A string is an immutable sequence of UTF-16 code units. Immutability means an operation such as replacement returns a new string; it does not edit the original object. Human-visible characters are more complicated than code units: some Unicode scalar values need two units, and a visible grapheme can combine several scalar values. Choose the unit that matches the task before counting or slicing text.

Text comparison also has a policy. Machine identifiers usually need ordinal comparison; user-facing sorting can need culture rules. Encoding turns text into bytes for a file or protocol. UTF-8 byte length is not string Length, and neither is automatically the number of visible characters. Keep these boundaries distinct when limiting input.""",
    '`$"item {count}"` interpolates a value. `StringComparison.OrdinalIgnoreCase` makes a comparison policy explicit. `EnumerateRunes()` visits Unicode scalar values. `Encoding.UTF8.GetByteCount` measures an encoded representation.',
    [
        ("Code unit", "One storage unit of an encoding, here a UTF-16 char."),
        ("Unicode scalar", "A code point excluding surrogate values."),
        ("Encoding", "A mapping between text and bytes."),
    ],
    (
        "Immutable transformations",
        'string original = "data";\nstring changed = original.ToUpperInvariant();\nCheck(original == "data" && changed == "DATA", "strings are unchanged");\nCheck(string.Equals("KEY", "key", StringComparison.OrdinalIgnoreCase), "identifier comparison");',
        "The original remains data while the result is DATA.",
        "Assignment of the returned value is necessary to keep a transformation. An explicit comparison policy prevents dependence on ambient culture.",
    ),
    (
        "Choose the counting unit",
        'string symbol = "😀";\nCheck(symbol.Length == 2, "UTF-16 units");\nCheck(symbol.EnumerateRunes().Count() == 1, "Unicode scalar");\nCheck(Encoding.UTF8.GetByteCount(symbol) == 4, "UTF-8 bytes");',
        "One scalar occupies two UTF-16 units and four UTF-8 bytes.",
        "The fixture disproves the assumption that Length is a universal character count.",
    ),
    [
        "Predict both string values after ToUpperInvariant and explain ownership of the result.",
        "Build an interpolated label containing a count and a unit.",
        "Implement case-insensitive machine-key comparison with an explicit policy.",
        "Diagnose code that takes one char from the emoji and assumes it is a complete symbol.",
        "Compare ASCII, an emoji and a combining-mark sequence using code units and text elements.",
        "Design a text-field limit and explain whether its contract measures bytes, scalars or user-visible graphemes.",
    ],
    "Indexing a string can split a surrogate pair. Invariant casing is useful for stable transformations but is not a universal user-language display rule. Normalization and comparison are separate policies.",
)

lesson(
    "Boolean decisions and exhaustive alternatives",
    """A branch chooses one path based on a Boolean expression. Good branches expose the domain distinction, not just a compact operator chain. Short-circuit operators evaluate their right side only when needed, which lets a guard protect a later operation. This is a control-flow property, not merely a performance optimization.

For mutually exclusive categories, put the cases in an order that matches the domain and include a policy for values outside the range. A boundary such as zero should have a deliberate meaning. Testing values just below, exactly at and just above a threshold detects mistakes that a typical middle value will miss.""",
    "`&&` requires both conditions and stops after false; `||` stops after true. A switch expression returns one value from its matching arm. The discard pattern `_` can provide an explicit fallback but must not conceal invalid input.",
    [
        ("Predicate", "An expression producing true or false."),
        ("Short circuit", "Skipping an unnecessary right-hand expression."),
        ("Boundary", "An input where a classification changes."),
    ],
    (
        "A guard prevents unsafe access",
        'string? label = null;\nCheck(!(label != null && label.Length > 0), "guarded access");\nlabel = "ok";\nCheck(label != null && label.Length == 2, "present label");',
        "The missing value is handled without dereferencing null.",
        "The left operand establishes the precondition needed by the right operand.",
    ),
    (
        "Classify a threshold",
        'string Classify(int score) => score switch { < 0 => "invalid", < 60 => "retry", <= 100 => "pass", _ => "invalid" };\nCheck(Classify(59) == "retry", "below boundary");\nCheck(Classify(60) == "pass", "at boundary");\nCheck(Classify(101) == "invalid", "outside domain");',
        "59 retries, 60 passes, and 101 is rejected.",
        "Ordered relational patterns make the inclusive boundary visible and preserve the invalid-input category.",
    ),
    [
        "Trace which operands execute when label is null.",
        "Change the classifier pass threshold to 70 and update boundary checks.",
        "Write a classifier for negative, zero and positive temperatures.",
        "Find why replacing && with & can break a null guard.",
        "Test the two ends of the valid score range and one value beyond each end.",
        "Choose a routing policy with three mutually exclusive outcomes and explain how invalid values are represented.",
    ],
    "An else branch can accidentally classify every invalid value as valid. Test domain validity independently from success thresholds. Do not use a fallback to hide an impossible state without explaining recovery.",
)

lesson(
    "Loops, invariants and termination",
    """A loop repeats a state transition. To understand it, state what is true before the first iteration and what remains true after each iteration. This repeated truth is an invariant. A second argument explains termination: some bounded quantity moves toward a stopping condition. A correct-looking body can still fail because its boundary executes once too often or never stops.

`foreach` expresses traversal of an existing sequence and usually avoids manual index bookkeeping. Use an index when the position itself matters, but relate the valid index range to the collection length. Empty inputs are especially revealing because the initial state becomes the final result without any iteration.""",
    "`for (initial; condition; update)` initializes once, checks before each body, and updates after each body. For an array of Length n, valid indices are zero through n minus one. `break` exits the loop; `continue` skips the remainder of one iteration.",
    [
        ("Invariant", "A property maintained across iterations."),
        ("Accumulator", "State summarizing the values seen so far."),
        ("Termination", "An argument that repetition eventually stops."),
    ],
    (
        "Sum with a maintained invariant",
        'int[] values = { 2, 4, 6 };\nint sum = 0;\nforeach (int value in values) sum += value;\nCheck(sum == 12, "sum of all values");\nCheck(Array.Empty<int>().Sum() == 0, "empty sum identity");',
        "The sum is 12 and the empty sum is zero.",
        "Before each iteration, sum equals the sum of values already visited. Zero is the identity that makes the invariant true initially.",
    ),
    (
        "Locate the first match",
        'int[] values = { 3, 8, 8 };\nint found = -1;\nfor (int i = 0; i < values.Length; i++) { if (values[i] == 8) { found = i; break; } }\nCheck(found == 1, "first matching position");\nCheck(!Array.Exists(values, value => value == 9), "absent target");',
        "The first 8 is at index 1; 9 is absent.",
        "Stopping at the first match is part of the contract. Without break, the same loop could return the last match.",
    ),
    [
        "Write the accumulator value before and after every iteration in Example A.",
        "Skip negative values while preserving the sum invariant.",
        "Implement a first-match search returning a separate not-found representation.",
        "Diagnose the condition i <= values.Length using a one-element array.",
        "Check empty, singleton, no-match and repeated-match inputs.",
        "Design a bounded retry loop and explain both its invariant and its stopping argument.",
    ],
    "Loop indices count from zero while lengths count elements. A sentinel such as -1 must be checked before indexing. Mutating a collection during enumeration can invalidate the traversal contract.",
)

lesson(
    "Methods, parameters and return contracts",
    """A method gives a computation a name and a boundary. Its contract states accepted inputs, its result, state changes and failure behavior. Splitting code into methods helps only when those boundaries expose meaning. A helper that secretly edits unrelated state is harder to reason about than one returning a clearly defined result.

C# normally passes arguments by value. For a value type, that means a copied value; for an object reference, it means a copied reference to the same object. The distinction becomes important later. Start with small pure methods, which depend only on arguments and return a result without observable mutation. They are easy to test because the same inputs produce the same outputs.""",
    "`int Double(int value) => value * 2` declares a local function with a typed parameter and return. `return` ends the current method. `ref` and `out` are explicit parameter passing modes, not decorations; prefer ordinary return values until shared mutation is required.",
    [
        ("Parameter", "A named input in a method definition."),
        ("Argument", "The value supplied at a call site."),
        ("Pure function", "A computation without observable external mutation."),
    ],
    (
        "Return a transformed value",
        'int Double(int value) => checked(value * 2);\nint original = 7;\nint result = Double(original);\nCheck(result == 14 && original == 7, "input value is retained");\nCheck(Double(0) == 0, "zero case");',
        "The result is 14 and the caller still holds 7.",
        "The parameter receives a value. Returning a transformed value does not reassign the caller variable.",
    ),
    (
        "Expose rejection as part of the contract",
        'int DivideExact(int value, int divisor) { if (divisor == 0 || value % divisor != 0) throw new ArgumentException("exact nonzero divisor required"); return value / divisor; }\nCheck(DivideExact(12, 3) == 4, "exact quotient");\nbool rejected = false;\ntry { _ = DivideExact(7, 2); } catch (ArgumentException) { rejected = true; }\nCheck(rejected, "fractional quotient rejected");',
        "12 divided by 3 returns 4; the exact-integer contract rejects 7 divided by 2.",
        "A precise function name and guard prevent accidental truncation from masquerading as a valid result.",
    ),
    [
        "Trace the caller and parameter values through Double.",
        "Add a Triple function and test zero and a negative input.",
        "Write a method computing an area from validated nonnegative dimensions.",
        "Diagnose a function whose name promises exact division but silently truncates.",
        "Test zero divisors and non-divisible inputs separately.",
        "Extract one computation from a larger program and state its input, output, mutation and failure contract.",
    ],
    "A method name is part of the interface. A generic catch returning zero can make rejected input indistinguishable from a valid zero result. Prefer one clear responsibility over a long list of optional switches.",
)

lesson(
    "Arrays, indices and rectangular data",
    """An array has a fixed number of elements with one element type. Its length does not grow after creation. Assignment copies the array reference, so two variables can refer to the same storage. A copied array can separate the outer storage while still sharing referenced elements. Before using a copy, identify which level of independence the algorithm needs.

A rectangular array has dimensions built into its shape; a jagged array is an array of arrays whose row lengths may differ. Data-science work often fails at shape boundaries before the numerical formula is wrong. Make row and column assumptions explicit and test a non-square fixture so swapping dimensions cannot accidentally pass.""",
    "`new int[3]` creates three zero-initialized entries. `values[0]` addresses the first. `int[,] grid` has rank two and GetLength selects a dimension. `int[][]` contains separate row arrays.",
    [
        ("Array", "Fixed-length indexed element storage."),
        ("Alias", "Another reference to the same storage."),
        ("Shape", "The size and organization of dimensions."),
    ],
    (
        "Copy the storage deliberately",
        'int[] source = { 2, 4 };\nint[] alias = source;\nint[] copy = (int[])source.Clone();\nalias[0] = 9;\nCheck(source[0] == 9 && copy[0] == 2, "alias versus copy");',
        "The alias changes source; the copied integer array retains 2.",
        "Primitive elements are values, so cloning this array provides independent element storage.",
    ),
    (
        "Respect distinct dimensions",
        'int[,] grid = { { 1, 2, 3 }, { 4, 5, 6 } };\nCheck(grid.GetLength(0) == 2 && grid.GetLength(1) == 3, "rectangular shape");\nint sum = 0;\nfor (int row = 0; row < grid.GetLength(0); row++) for (int col = 0; col < grid.GetLength(1); col++) sum += grid[row, col];\nCheck(sum == 21, "all six cells");',
        "The shape is two by three and the sum is 21.",
        "Different dimension sizes expose swapped-boundary mistakes that a square fixture can hide.",
    ),
    [
        "Predict source and copy after alias mutation.",
        "Change only the copied array and verify source is unchanged.",
        "Compute each row sum of the two-by-three grid.",
        "Diagnose a nested loop that uses the row count for both dimensions.",
        "Test an empty array and a one-row rectangular array.",
        "Choose rectangular or jagged storage for variable-length sensor histories and justify the choice.",
    ],
    "Clone is shallow for referenced elements. Length of a rectangular array is total cells, not the number of rows. Validate an index before using it, including results returned by searches.",
)

lesson(
    "Lists, capacity and safe mutation",
    """A List stores a resizable indexed sequence. Count is the number of elements logically present; capacity is storage reserved to reduce reallocations. Increasing capacity does not create valid elements. Append is often efficient, but inserting at the front shifts existing entries. The interface makes these operations equally easy to write while their costs differ.

Enumeration assumes a stable collection structure. Removing items during foreach invalidates that assumption. Choose a bulk removal operation, construct a new result, or use a deliberate index strategy. The right choice depends on whether other parts of the program should observe mutation of the original list.""",
    "`new List<int> { ... }` uses a collection initializer. `Add` changes Count; an indexer replaces an existing element. `RemoveAll(predicate)` expresses structural removal as one owned operation. `ToArray` creates a snapshot of the element references or values.",
    [
        ("Count", "The number of present elements."),
        ("Capacity", "Allocated room available before growth."),
        ("Snapshot", "A separately stored view captured at a moment."),
    ],
    (
        "Separate count from reserved storage",
        'var values = new List<int>(10);\nCheck(values.Count == 0 && values.Capacity >= 10, "capacity is not count");\nvalues.Add(3); values.Add(5);\nCheck(values.Count == 2 && values[1] == 5, "append order");',
        "Reserving ten slots leaves Count at zero; two appends produce Count two.",
        "Capacity is an implementation resource, not a promise that ten logical entries exist.",
    ),
    (
        "Remove under one mutation policy",
        'var values = new List<int> { -1, 2, -3, 4 };\nint[] before = values.ToArray();\nint removed = values.RemoveAll(value => value < 0);\nCheck(removed == 2 && values.SequenceEqual(new[] { 2, 4 }), "filtered mutation");\nCheck(before.Length == 4, "snapshot retained");',
        "Two entries are removed while the earlier integer snapshot keeps four values.",
        "A bulk operation owns traversal and mutation, avoiding an invalidated external enumerator.",
    ),
    [
        "Predict Count and Capacity before and after appends.",
        "Replace one existing entry and explain why Count stays constant.",
        "Produce a filtered list while preserving the original.",
        "Diagnose removing an entry inside foreach.",
        "Test no removals, all removals and an empty list.",
        "Choose mutation or a new sequence for an undoable editor operation and explain who observes the change.",
    ],
    "Capacity is not an index boundary. A snapshot of objects still shares those objects. Repeated front insertion can turn an apparently simple loop into quadratic work.",
)

lesson(
    "Dictionaries, sets and identity policies",
    """A dictionary maps unique keys to values. A set represents membership without duplicates. Their behavior depends on equality and hashing: values considered equal must have compatible hash codes. Choosing a string comparer is therefore a data-model decision, not just a search convenience. Machine identifiers may be case-sensitive or case-insensitive depending on the contract.

A missing key is different from a present key holding a default value. Use TryGetValue when absence is expected. Sorting output separately from lookup makes demonstrations deterministic without claiming that dictionary iteration order is the business ordering. If order matters, encode that requirement explicitly.""",
    "`Dictionary<string,int>(StringComparer.OrdinalIgnoreCase)` defines key identity. `TryGetValue(key, out value)` separates absence from a stored zero. `HashSet<T>.Add` returns whether membership changed.",
    [
        ("Key", "The identity used for lookup."),
        ("Hashing", "A mapping that narrows candidate equality comparisons."),
        ("Membership", "Whether an equivalent element belongs to a set."),
    ],
    (
        "Preserve absence information",
        'var counts = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase) { ["Oak"] = 0 };\nCheck(counts.TryGetValue("OAK", out int zero) && zero == 0, "present zero");\nCheck(!counts.TryGetValue("Pine", out _), "missing key");',
        "OAK finds a present zero; Pine is absent.",
        "The comparer belongs to the collection contract. A missing value cannot be inferred from the integer alone.",
    ),
    (
        "Deduplicate by an explicit policy",
        'var labels = new HashSet<string>(StringComparer.OrdinalIgnoreCase);\nCheck(labels.Add("red"), "first insertion");\nCheck(!labels.Add("RED"), "duplicate identity");\nlabels.Add("blue");\nCheck(labels.Count == 2, "two identities");',
        "RED is a duplicate under the selected comparer.",
        "Deduplication is meaningful only after defining equality. Case-insensitive comparison is appropriate for this fixture, not for every identifier.",
    ),
    [
        "Predict the difference between absent Pine and present-zero Oak.",
        "Switch to an ordinal case-sensitive comparer and explain the changed lookup.",
        "Build a frequency dictionary from a list of tags.",
        "Diagnose indexing a missing key without an absence policy.",
        "Test empty tags, repeated tags and keys differing only by case.",
        "Design stable identity for records and explain which fields may change without invalidating lookup.",
    ],
    "Changing a key field after insertion can break hash-based lookup for mutable custom keys. Distinct text spellings are not always distinct identities. Do not rely on incidental traversal order for reports.",
)

lesson(
    "Nullability and optional information",
    """Missing information should be visible in a type and a control-flow policy. Nullable reference annotations let the compiler warn when a value may be null; they are static analysis, not a new runtime container. An annotation cannot validate data arriving from another language, reflection or an external format. Keep runtime validation where that data enters.

A nullable value type such as int? represents either an int or no value. Choosing a fallback is a domain decision. Replacing missing age with zero means something very different from reporting unknown age. Prefer explicit branches when a default would blur those meanings.""",
    "`string?` permits null in static analysis; `int?` is Nullable<int>. `?.` conditionally accesses a member and preserves absence. `??` supplies a fallback. The null-forgiving operator `!` silences analysis but performs no check.",
    [
        ("Null", "A missing reference or absent nullable value."),
        ("Flow analysis", "Compiler reasoning about possible values on each path."),
        ("Fallback", "A deliberate replacement for absence."),
    ],
    (
        "Carry absence through a computation",
        'string? label = null;\nint? length = label?.Length;\nCheck(length is null, "absence remains absent");\nCheck((length ?? -1) == -1, "explicit display sentinel");',
        "The optional length is absent, not zero.",
        "Conditional access propagates missing information until a boundary deliberately chooses a display representation.",
    ),
    (
        "Distinguish zero from missing",
        'int? measured = 0;\nint? missing = null;\nCheck(measured.HasValue && measured.Value == 0, "valid zero");\nCheck(!missing.HasValue, "unknown measurement");\nstring Describe(int? value) => value is int actual ? $"measured:{actual}" : "unknown";\nCheck(Describe(measured) == "measured:0" && Describe(missing) == "unknown", "preserved meaning");',
        "A measured zero and an unknown measurement produce distinct descriptions.",
        "Pattern matching unwraps only the present case, giving a nonnullable variable inside that branch.",
    ),
    [
        "Predict nullable length and its fallback for null and empty text.",
        "Use a visible unknown label rather than a numeric sentinel.",
        "Write a formatter preserving missing, zero and positive measurements.",
        "Diagnose using ! to suppress a warning on an actually null value.",
        "Test whitespace-only text separately from null and empty text.",
        "Design an import field whose missing value has different meaning from an explicit zero or empty value.",
    ],
    "A warning suppression is not validation. Null, empty and whitespace-only text are different states. Returning a fallback too early can irreversibly discard useful information.",
)

lesson(
    "Value copies, references and mutation ownership",
    """Value and reference semantics describe what assignment copies. A value-type assignment copies the value. A reference-type assignment copies a reference, so both variables may reach the same object. This is more useful than the misleading slogan that values always live on the stack and objects always live on the heap: storage placement depends on context, while assignment semantics remain the reasoning tool.

A class can deliberately encapsulate mutation behind operations that preserve invariants. A value object can make independent copies easier to reason about. Neither choice is automatically faster or safer. Ask whether identity matters, whether consumers should share changes, and how large or expensive copies may become.""",
    "`struct` introduces a value type; `class` introduces a reference type. Assignment has the same spelling for both, so inspect the declared type. `ReferenceEquals` asks whether references identify the same object, not whether their properties happen to match.",
    [
        ("Value semantics", "Assignment copies the represented value."),
        ("Reference semantics", "Assignment copies a reference to shared identity."),
        ("Ownership", "The responsibility for permitted mutation and lifetime."),
    ],
    (
        "Copy a value",
        'var first = new Point(2, 3);\nvar second = first;\nsecond.X = 9;\nCheck(first.X == 2 && second.X == 9, "struct copy");',
        "Changing the copied point leaves the original X at 2.",
        "The struct contains only integer fields, so its copied state is independently mutable.",
    ),
    (
        "Share an object identity",
        'var first = new Counter();\nvar second = first;\nsecond.Value++;\nCheck(first.Value == 1, "shared mutation");\nCheck(ReferenceEquals(first, second), "same object");',
        "Both references observe the same counter increment.",
        "Passing or assigning a reference by value does not clone the referenced object.",
    ),
    [
        "Draw the values and references after each assignment.",
        "Make a separate Counter instance and compare identity with equal property values.",
        "Choose a representation for a coordinate and for a shared session, explaining the difference.",
        "Diagnose expecting assignment of a class variable to produce a deep copy.",
        "Place a mutable list inside a struct and explain which part of the copied value remains shared.",
        "Design a data boundary that prevents callers from mutating an internal collection.",
    ],
    "A struct containing a reference copies that reference, so value semantics do not imply a recursive deep copy. Equality and identity are separate questions. Avoid reasoning about correctness from presumed stack placement.",
    helpers="public struct Point { public int X; public int Y; public Point(int x, int y) { X = x; Y = y; } }\npublic sealed class Counter { public int Value { get; set; } }",
)

lesson(
    "Classes, constructors and encapsulated invariants",
    """A class can protect a state transition by admitting changes only through reviewed operations. A constructor establishes the initial invariant; methods preserve it. Private setters are useful only when the public operations actually enforce the domain rule. A property named Balance that any caller can replace with a negative number has no meaningful protection.

Model expected rejection distinctly from programming defects. A withdrawal larger than the available balance can be a normal false result. A negative withdrawal is malformed input and may merit an argument exception. State should remain unchanged on rejected operations. This failure atomicity is often more important than a compact implementation.""",
    "A constructor has the class name and no return type. `private set` permits mutation inside the class. `sealed` prevents inheritance when extension is not part of the design. Guard clauses reject invalid inputs before state changes.",
    [
        ("Invariant", "A rule true for every externally visible valid state."),
        ("Encapsulation", "Hiding representation behind controlled operations."),
        ("Failure atomicity", "A failed operation leaves the prior valid state intact."),
    ],
    (
        "Preserve a nonnegative balance",
        'var wallet = new Wallet(10);\nCheck(wallet.TrySpend(4) && wallet.Balance == 6, "valid spend");\nCheck(!wallet.TrySpend(7) && wallet.Balance == 6, "rejection retains balance");',
        "Spending 4 succeeds; spending 7 afterward fails without changing 6.",
        "Validate affordability before subtraction so rejected requests cannot corrupt state.",
    ),
    (
        "Reject malformed operations",
        'var wallet = new Wallet(5);\nbool rejected = false;\ntry { wallet.TrySpend(-1); } catch (ArgumentOutOfRangeException) { rejected = true; }\nCheck(rejected && wallet.Balance == 5, "malformed input keeps state");\nCheck(wallet.TrySpend(0) && wallet.Balance == 5, "zero is allowed");',
        "Negative spending is rejected and zero is an accepted no-op.",
        "These are separate boundary policies. Both preserve the invariant, but they communicate different meanings to the caller.",
    ),
    [
        "Trace the wallet state through successful and rejected spending.",
        "Add a validated deposit operation.",
        "Implement a bounded inventory whose reservations never make stock negative.",
        "Diagnose subtracting before checking affordability.",
        "Test exactly the available amount, zero and a negative request.",
        "Explain whether a shared wallet needs synchronization when several tasks may spend concurrently.",
    ],
    "Private fields alone do not establish a correct contract. A partially mutated object after failure can poison later operations. This class is intentionally single-threaded; encapsulation does not itself provide synchronization.",
    helpers="public sealed class Wallet { public int Balance { get; private set; } public Wallet(int initial) { if (initial < 0) throw new ArgumentOutOfRangeException(nameof(initial)); Balance = initial; } public bool TrySpend(int amount) { if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount)); if (amount > Balance) return false; Balance -= amount; return true; } }",
)

lesson(
    "Records, structs and data equality",
    """Records describe data with synthesized equality and convenient copying. A record class still has reference identity, but its equality normally compares declared data members. A record struct is a value type. These features reduce boilerplate; they do not automatically make nested objects immutable or define the correct business identity.

A with expression constructs a copy with selected changes. That copy is shallow for referenced members. When a record contains a mutable list, two record instances may still share that list. Use immutable representations or deliberate copying when independent history is required. Choose equality fields from the domain rather than accepting every field merely because generation is convenient.""",
    "`record Person(string Name, int Age)` declares positional properties and value-based equality. `record struct` changes assignment semantics. `with { Age = 31 }` creates a changed copy. `==` on records follows generated value equality.",
    [
        ("Record", "A data-focused type with synthesized equality members."),
        ("With expression", "A copy with selected member changes."),
        ("Shallow copy", "A copy that retains references to nested objects."),
    ],
    (
        "Equal data with distinct identities",
        'var first = new Person("Ada", 30);\nvar second = new Person("Ada", 30);\nCheck(first == second, "record value equality");\nCheck(!ReferenceEquals(first, second), "distinct objects");\nvar older = first with { Age = 31 };\nCheck(first.Age == 30 && older.Age == 31, "copy retains prior value");',
        "Equal records can be distinct objects; with preserves the previous age.",
        "Value equality and reference identity answer different questions.",
    ),
    (
        "Notice nested shared state",
        'var first = new Basket(new List<int> { 1 });\nvar second = first with { };\nsecond.Items.Add(2);\nCheck(first.Items.Count == 2, "nested list is shared");\nCheck(ReferenceEquals(first.Items, second.Items), "shallow copied member");',
        "Both records see the appended list item.",
        "The record copy duplicates its field values, including the list reference. Generated copying is not a deep-clone promise.",
    ),
    [
        "Predict record equality and reference equality separately.",
        "Create a changed copy with a new name and retain the original.",
        "Design an immutable coordinate using a readonly record struct.",
        "Diagnose a supposedly immutable history entry containing a mutable list.",
        "Compare records whose nested collections contain equal values but have different identities.",
        "Choose identity-based or data-based equality for an order and explain how updates affect collection membership.",
    ],
    "Record equality does not recursively compare arbitrary collection contents. A positional record can still contain mutable members. Avoid putting fields that change after insertion into a hash key contract.",
    helpers="public record Person(string Name, int Age);\npublic record Basket(List<int> Items);",
)

lesson(
    "Patterns and explicit state models",
    """Pattern matching combines a test with structured access to the matched data. It can replace a chain of unsafe casts with branches that make the valid shape visible. Patterns are especially useful when a finite set of domain states carries different information, such as loading, success and failure. The goal is a truthful state model, not clever syntax.

A fallback branch should have a deliberate meaning. If a new domain state is introduced later, silently treating it as success is dangerous. C# class hierarchies are not fully closed algebraic data types, so review exhaustiveness and reject unexpected cases explicitly when necessary. Keep missing information distinct from failure information.""",
    "`value is int number` tests and binds. Property patterns inspect named properties. A switch expression can select an expression by type and guard. `when` adds a condition after the structural match.",
    [
        ("Pattern", "A rule matching a value shape and optionally binding parts."),
        ("Guard", "An additional condition on a matched case."),
        ("State model", "A representation of allowed states and transitions."),
    ],
    (
        "Narrow before using a value",
        'object value = 12;\nstring Describe(object item) => item switch { int number when number > 0 => "positive", int => "nonpositive", string { Length: 0 } => "empty", _ => "other" };\nCheck(Describe(value) == "positive", "integer branch");\nCheck(Describe(-1) == "nonpositive" && Describe("") == "empty", "distinct shapes");',
        "The same method distinguishes type, value range and string shape.",
        "The bound number is available only after the type pattern succeeds.",
    ),
    (
        "Represent results without impossible combinations",
        'Result success = new Success(8);\nResult failure = new Failure("invalid");\nstring Render(Result result) => result switch { Success(var count) => $"count:{count}", Failure(var reason) => $"error:{reason}", _ => throw new InvalidOperationException("unknown result") };\nCheck(Render(success) == "count:8", "success payload");\nCheck(Render(failure) == "error:invalid", "failure payload");',
        "Success carries a count; failure carries a reason.",
        "Separate cases prevent a Boolean success flag from disagreeing with unrelated optional fields.",
    ),
    [
        "Predict the matched arm for zero, positive integer, empty text and nonempty text.",
        "Add a nonempty string arm without shadowing the empty case.",
        "Model a loading, ready and failed operation with separate payloads.",
        "Diagnose a broad object arm placed before a more specific case.",
        "Test an unexpected subclass and explain the fallback policy.",
        "Replace several loosely related flags in a program with explicit states and justify which impossible combinations disappear.",
    ],
    "An early broad pattern can make a later case unreachable. A default branch can hide a newly added state. Pattern matching is not a substitute for validating external data.",
    helpers="public abstract record Result;\npublic sealed record Success(int Count) : Result;\npublic sealed record Failure(string Reason) : Result;",
)

lesson(
    "Foundation project: a validated inventory report",
    """A useful first project combines parsing, representation and aggregation while keeping their responsibilities separate. The input boundary rejects malformed quantities. The domain representation preserves item identity. The report stage summarizes only accepted records. Mixing these stages often creates a subtle bug: a failed parse becomes zero and then appears as valid data.

This project uses in-memory fixture lines so it runs offline without interactive input. It reports accepted totals and rejected line counts independently. A real importer would also record line identity and a safe reason. Build the smallest end-to-end path first, then introduce invalid and duplicate inputs. The final result must explain what happened, not merely produce a total that looks plausible.""",
    "`Split` produces fields; check the field count before indexing. `TryParse` separates syntax from a valid integer. `TryGetValue` supports accumulating repeated keys. Sorting keys before display gives a stable report.",
    [
        ("Pipeline", "Stages that transform validated information."),
        ("Rejection", "An input excluded under an explicit rule."),
        ("Aggregation", "Combining accepted records into a summary."),
    ],
    (
        "Aggregate repeated valid items",
        'var totals = Import(new[] { "pear,2", "apple,3", "pear,4" });\nCheck(totals.Rejected == 0, "all accepted");\nCheck(totals.Counts["pear"] == 6 && totals.Counts["apple"] == 3, "per-item totals");',
        "Pear totals 6 and apple totals 3.",
        "Repeated identities accumulate after validation rather than creating ambiguous duplicate dictionary entries.",
    ),
    (
        "Retain rejection evidence",
        'var totals = Import(new[] { "pear,2", "pear,no", "apple,-1", "broken" });\nCheck(totals.Rejected == 3, "rejections counted");\nCheck(totals.Counts.Count == 1 && totals.Counts["pear"] == 2, "only valid data contributes");\nCheck(Import(Array.Empty<string>()).Counts.Count == 0, "empty input");',
        "Three rejected lines do not alter the valid pear total.",
        "Malformed and negative quantities remain excluded, and empty input produces an empty report rather than an invented item.",
    ),
    [
        "Trace each input through validation and accumulation.",
        "Add one valid duplicate and predict the new total before running.",
        "Build a sorted text report from the accepted dictionary and the rejection count.",
        "Diagnose an importer that ignores TryParse failure and inserts zero.",
        "Test empty item names, extra fields, zero quantity and empty input.",
        "Design a reusable import result that retains per-line rejection reasons without exposing sensitive raw input.",
    ],
    "Checking field count after indexing is too late. Case policy affects identity and must be documented. Extremely large totals can overflow, so checked accumulation belongs in a production input contract.",
    helpers="""public static (Dictionary<string, int> Counts, int Rejected) Import(IEnumerable<string> lines) { var counts = new Dictionary<string, int>(StringComparer.Ordinal); int rejected = 0; foreach (string line in lines) { string[] fields = line.Split(','); if (fields.Length != 2 || string.IsNullOrWhiteSpace(fields[0]) || !int.TryParse(fields[1], out int quantity) || quantity < 0) { rejected++; continue; } counts.TryGetValue(fields[0], out int before); counts[fields[0]] = checked(before + quantity); } return (counts, rejected); }""",
)
