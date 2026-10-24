# ruff: noqa: E501
"""Rust advanced mechanisms and real Arrow 60 data-engineering chapters."""

from render import lesson

lesson(
    "Futures, async syntax and executor boundaries",
    """A Future represents a computation that can make progress when polled. It may return Ready with a result or Pending and arrange a wakeup when progress becomes possible. Creating an async block does not automatically execute it or create a thread. An executor owns polling and scheduling.

Rust\'s standard library defines Future and task primitives but does not provide a general production async runtime. Tokio and similar ecosystems are separate prepared dependencies, not installed by this pad. This chapter polls immediately ready futures once to reveal the mechanism. It deliberately does not present a busy polling loop as a correct executor for arbitrary I/O.""",
    "An async block produces a Future. Pin protects address-sensitive future state from invalid movement while polled. Context carries a Waker. Poll::Ready and Poll::Pending are distinct completion states.",
    [
        ("Future", "A computation progressed through polling."),
        ("Executor", "The owner scheduling and polling futures."),
        (
            "Waker",
            "A notification mechanism requesting another poll when progress may be possible.",
        ),
    ],
    (
        "Poll a ready computation",
        "use std::future::Future;\nuse std::task::{Context, Poll, Waker};\nlet mut future = Box::pin(async { 7 });\nlet mut context = Context::from_waker(Waker::noop());\nassert_eq!(future.as_mut().poll(&mut context), Poll::Ready(7));",
        "The immediately ready future yields seven on its first poll.",
        "A no-op waker is sufficient only because this fixture cannot require a later external wakeup.",
    ),
    (
        "Observe pending without spinning",
        "use std::future::Future;\nuse std::task::{Context, Poll, Waker};\nlet mut future = Box::pin(std::future::pending::<i32>());\nlet mut context = Context::from_waker(Waker::noop());\nassert_eq!(future.as_mut().poll(&mut context), Poll::Pending);",
        "The pending future reports no completed value.",
        "The program stops after one inspection rather than wasting CPU pretending a tight loop is a runtime.",
    ),
    [
        "Separate future creation, polling and completion.",
        "Compose two immediately ready async values and poll the combined fixture.",
        "Explain the ownership responsibilities of an executor in a written event trace.",
        "Diagnose creating a future and expecting it to run without a consumer.",
        "Contrast Ready, Pending and dropping an uncompleted future.",
        "Plan a separately prepared Tokio service, naming runtime, cancellation, I/O and dependency requirements.",
    ],
    "Async is not automatically parallel. A no-op waker cannot drive real asynchronous I/O. Dropping a future does not necessarily reverse effects already performed by external systems.",
    source="https://doc.rust-lang.org/std/future/trait.Future.html",
)

lesson(
    "Unsafe code, FFI and a documented safety argument",
    """Unsafe permits a small set of operations whose correctness the compiler cannot fully establish. It does not disable every safety rule or turn wrong memory access into valid behavior. Each unsafe block needs an argument covering pointer validity, alignment, initialized length, aliasing and lifetime. Keep the block small and wrap it in a safe interface that enforces those conditions.

Foreign-function interfaces add an ABI contract: layout, calling convention, string encoding, ownership and failure signaling must agree across languages. A successful link does not prove those agreements. The ordinary fixture uses a pointer obtained from a live array and immediately reconstructs a read-only slice under a documented invariant, without calling undeclared native libraries.""",
    "`as_ptr` borrows an address from live storage. `slice::from_raw_parts` is unsafe because the caller supplies validity and length. A SAFETY comment explains why this exact operation satisfies its preconditions.",
    [
        ("Unsafe operation", "An operation requiring caller-provided safety evidence."),
        ("ABI", "The binary-level calling and layout agreement between compiled components."),
        ("Safety invariant", "The conditions a safe wrapper must preserve around unsafe code."),
    ],
    (
        "Reconstruct a bounded borrowed view",
        "let values = [2_i32, 3, 4];\nlet pointer = values.as_ptr();\n// SAFETY: pointer comes from this live initialized array; length is exact; no mutation overlaps.\nlet view = unsafe { std::slice::from_raw_parts(pointer, values.len()) };\nassert_eq!(view, &[2, 3, 4]);",
        "The reconstructed view matches the live initialized array.",
        "The safety proof is tied to the pointer origin and exact length, not merely to the pointer being non-null.",
    ),
    (
        "Prefer the safe operation when available",
        "let values = [2, 3, 4];\nlet view = &values[..];\nassert_eq!(view.iter().sum::<i32>(), 9);",
        "A normal slice provides the same read contract without a manual safety burden.",
        "Unsafe should be justified by a real boundary, not used because pointer syntax appears advanced.",
    ),
    [
        "State every precondition needed by from_raw_parts.",
        "Reduce the borrowed length while retaining valid initialized storage.",
        "Write a safe wrapper specification before considering an unsafe implementation.",
        "Diagnose returning a pointer after its owner is dropped.",
        "Review zero-length and alignment rules without executing undefined behavior.",
        "Design an FFI ownership document stating allocation, release, encoding and error conventions.",
    ],
    "Never test undefined behavior by hoping it crashes predictably. A null check is insufficient to prove pointer validity. Panics crossing an incompatible FFI boundary need a deliberate policy.",
    source="https://doc.rust-lang.org/nomicon/",
)

lesson(
    "Memory layout, allocation and performance evidence",
    """Rust exposes enough control to optimize data layout and allocation, but correctness and a workload model come first. Contiguous arrays can improve locality for column scans, while pointer-heavy structures may incur indirection. Copying a small value can be cheaper than managing shared ownership; cloning a large buffer can dominate a pipeline.

Measure allocations and throughput under a realistic workload, and retain identical semantics across implementations. A single elapsed-time sample is weak evidence. The classroom uses deterministic size and operation observations, then prepares the learner to design an external benchmark. Representation details should not leak into a stable API unless the contract requires them.""",
    "size_of measures a type's inline representation, not every allocation reachable from it. Vec capacity is separate allocated storage. reserve can reduce reallocations without changing the algorithmic cost of shifting or sorting.",
    [
        ("Inline size", "The bytes occupied directly by a value representation."),
        ("Locality", "Access patterns that reuse nearby memory effectively."),
        ("Allocation profile", "Evidence about the number and size of allocated resources."),
    ],
    (
        "Distinguish handle size from owned data",
        'let small = String::from("a");\nlet large = "x".repeat(1000);\nassert_eq!(std::mem::size_of_val(&small), std::mem::size_of_val(&large));\nassert_ne!(small.len(), large.len());',
        "String handle size is equal while the owned text lengths differ.",
        "Inline size is not a total retained-memory measurement.",
    ),
    (
        "Prepare capacity without inventing elements",
        "let mut values = Vec::with_capacity(100);\nvalues.extend(0..10);\nassert_eq!(values.len(), 10);\nassert!(values.capacity() >= 100);\nassert_eq!(values.iter().sum::<i32>(), 45);",
        "Only ten initialized elements participate in the sum.",
        "Reserved capacity is a resource decision, not part of the logical dataset.",
    ),
    [
        "Separate inline handles from their owned allocations.",
        "Compare vector lengths after different reserve calls.",
        "Write a benchmark plan comparing repeated clone with borrowed processing.",
        "Diagnose measuring size_of as total memory retained by nested objects.",
        "Test empty and large inputs with the same correctness oracle.",
        "Choose a layout for repeated column scans and explain locality, ownership and update tradeoffs.",
    ],
    "Benchmarking different validation or ordering semantics is invalid. Size and alignment can vary by target. Do not use unsafe layout assumptions to replace an actual profiling result.",
)

lesson(
    "Cargo, editions and reproducible release workflows",
    """Cargo describes packages, targets, dependencies and build profiles. A Rust edition selects language compatibility rules while the compiler version selects available implementations and library APIs. These are related but distinct. Pinning an edition does not pin a dependency graph or a compiler toolchain.

Cargo.lock records selected dependency versions for reproducible resolution under a project policy. Locked and offline modes answer different questions: locked rejects graph changes, while offline forbids network access and requires prepared assets. The classroom bypasses per-attempt Cargo resolution by linking a reviewed read-only Arrow library. External projects use their own explicit preparation and lock review.""",
    "Cargo.toml declares package and dependency intent. Cargo.lock records a resolved graph. cargo build --locked checks lock consistency; --offline requires cached dependencies. cargo test and cargo clippy are distinct verification tools.",
    [
        ("Edition", "A language compatibility mode for a crate."),
        ("Lockfile", "A record of the selected dependency graph."),
        ("Offline build", "A build restricted to already prepared dependency assets."),
    ],
    (
        "Keep build policy explicit",
        'let policy = ["edition=2024", "locked", "offline-after-preparation"];\nassert!(policy.contains(&"edition=2024"));\nassert_ne!(policy[0], "compiler-version");',
        "Edition and compiler version remain different policy fields.",
        "This metadata kernel supports reasoning; the real Cargo fixture supplies build evidence.",
    ),
    (
        "Retain an error rather than hide a failed gate",
        "let checks = [true, true, false];\nassert!(!checks.iter().all(|passed| *passed));\nassert_eq!(checks.iter().filter(|passed| !**passed).count(), 1);",
        "One failed gate prevents a claimed complete release.",
        "Release accounting should retain a failed check instead of substituting an older successful result.",
    ),
    [
        "Explain edition, compiler version and dependency version separately.",
        "Build InventoryLab with its checked-in lockfile.",
        "Run its tests and inspect a deliberately changed public contract.",
        "Diagnose offline mode failing because a dependency was never prepared.",
        "Remove only owned target output and perform a clean build.",
        "Design a dependency upgrade review including lock diff, licenses, compile tests and runtime evidence.",
    ],
    "A successful dependency download is not successful compilation. Do not edit checksums manually to force a lockfile pass. A native binary is platform- and architecture-specific.",
    notes="The complete [InventoryLab](../fixtures/InventoryLab/README.md) demonstrates Cargo without external dependencies. Arrow dependencies are prepared by the classroom image, not installed by learner source.",
    source="https://doc.rust-lang.org/cargo/guide/",
)

lesson(
    "Arrow columnar memory and typed arrays",
    """Apache Arrow defines a columnar in-memory representation for analytical data. A typed array stores values of one logical type along with validity information and, for variable-width types, offsets and data buffers. This differs from a collection of row objects with independent allocations for every field.

Columnar layout can make scans and vectorized operations efficient, but Arrow is not a database, query optimizer or automatic distributed engine. Its arrays provide a representation and compute building blocks. The prepared Arrow 60 crate is real library code linked into the worker. Begin with typed arrays and the Array trait before using type-erased columns in a RecordBatch.""",
    "Int32Array stores signed 32-bit integer values. Importing the Array trait exposes common methods such as len and null_count. StringArray stores variable-width UTF-8 values. ArrayRef later erases concrete type behind Arc<dyn Array>.",
    [
        (
            "Columnar layout",
            "Grouping values by column rather than storing independent row objects.",
        ),
        ("Typed array", "An Arrow array with a known concrete element representation."),
        ("Validity", "Information identifying which logical positions are null."),
    ],
    (
        "Create a concrete integer column",
        "use arrow::array::{Array, Int32Array};\nlet values = Int32Array::from(vec![2, 4, 6]);\nassert_eq!(values.len(), 3);\nassert_eq!(values.value(1), 4);\nassert_eq!(values.null_count(), 0);",
        "The concrete column contains three non-null integers.",
        "The trait supplies common array behavior while the concrete type supplies typed value access.",
    ),
    (
        "Use a variable-width text column",
        'use arrow::array::{Array, StringArray};\nlet labels = StringArray::from(vec!["a", "longer", "é"]);\nassert_eq!(labels.len(), 3);\nassert_eq!(labels.value(1), "longer");\nassert_eq!(labels.value(2), "é");',
        "Different text lengths share one logical column.",
        "Offsets and UTF-8 data support variable-width values without pretending every row has a fixed-size string slot.",
    ),
    [
        "Identify logical length, type and null count.",
        "Add a fourth value and inspect its typed access.",
        "Construct paired integer and text columns with equal row counts.",
        "Diagnose treating Arrow as an automatically installed SQL engine.",
        "Test an empty typed array and a non-ASCII string.",
        "Compare row-object and columnar representations for a repeated analytical scan.",
    ],
    "Value access at an invalid index still violates bounds. A library being linked does not mean every optional Arrow feature is enabled. Parquet and DataFusion are separate crates and workflows.",
    source="https://docs.rs/arrow/60.0.0/arrow/",
)

lesson(
    "Arrow nulls, validity and NaN semantics",
    """A null means the logical value is absent under the dataset\'s policy. The physical value buffer can still contain bytes at that position, but those bytes are not a valid observation. Always consult validity or use an iterator returning Option. Reading value at a null position and treating its physical contents as data can silently corrupt an analysis.

NaN is a floating-point value category, not an Arrow null. It can represent an undefined numerical result while remaining logically present. A pipeline must decide separately how to handle missing and non-finite measurements. Conflating them changes counts, means and validation outcomes.""",
    "Array::is_null and is_valid inspect validity. Int32Array::iter yields Option<i32>. Float64Array can contain both Some(NaN) and None. null_count counts absence, not non-finite values.",
    [
        ("Null bitmap", "The validity representation marking absent logical values."),
        ("NaN", "A present floating-point value representing not-a-number."),
        ("Logical value", "The value after applying type and validity semantics."),
    ],
    (
        "Preserve null versus zero",
        "use arrow::array::{Array, Int32Array};\nlet values = Int32Array::from(vec![Some(0), None, Some(4)]);\nassert_eq!(values.null_count(), 1);\nassert!(values.is_valid(0) && values.is_null(1));\nassert_eq!(values.iter().collect::<Vec<_>>(), vec![Some(0), None, Some(4)]);",
        "A valid zero and a null remain distinct positions.",
        "Optional iteration respects validity rather than exposing meaningless physical contents at null positions.",
    ),
    (
        "Keep NaN separate from null",
        "use arrow::array::{Array, Float64Array};\nlet values = Float64Array::from(vec![Some(f64::NAN), None, Some(2.0)]);\nassert_eq!(values.null_count(), 1);\nassert!(values.is_valid(0) && values.value(0).is_nan());\nassert_eq!(values.iter().flatten().filter(|value| value.is_finite()).count(), 1);",
        "The column contains one null, one present NaN and one finite value.",
        "A finite-value policy is an additional analytical rule, not a synonym for Arrow validity.",
    ),
    [
        "Classify zero, null and NaN separately.",
        "Add a present infinity and update finite-value accounting.",
        "Write a summary returning valid, null and finite counts.",
        "Diagnose summing physical values without applying validity.",
        "Test all-null, empty and no-null columns.",
        "Define missingness and non-finite policies for a sensor dataset before calculating a mean.",
    ],
    "Null positions can contain arbitrary physical values. NaN is not equal to itself under ordinary floating equality. Do not replace every null with zero without a domain justification.",
    source="https://arrow.apache.org/docs/format/Columnar.html",
)

lesson(
    "Schemas, fields and RecordBatch invariants",
    """A Schema gives columns names, logical types, nullability and optional metadata. A RecordBatch pairs that schema with arrays representing one batch of rows. The arrays must match the schema types and have compatible lengths. This is a useful executable contract at a data boundary.

A batch is not the entire dataset and does not imply a global uniqueness or ordering guarantee. Several batches can share a schema while representing different chunks. Validate domain rules such as unique IDs separately. A schema mismatch should remain an error rather than being repaired by silently dropping or reordering columns.""",
    "Field::new records name, DataType and nullable policy. Schema::new groups fields. RecordBatch::try_new validates arrays against an Arc<Schema>. ArrayRef stores different concrete arrays behind one shared interface.",
    [
        ("Schema", "A contract for column names, types and nullability."),
        ("RecordBatch", "Equal-length columns representing one batch of rows."),
        ("ArrayRef", "Shared ownership of a type-erased Arrow array."),
    ],
    (
        "Build an aligned batch",
        'use std::sync::Arc;\nuse arrow::array::{ArrayRef, Int32Array, StringArray};\nuse arrow::datatypes::{DataType, Field, Schema};\nuse arrow::record_batch::RecordBatch;\nlet schema = Arc::new(Schema::new(vec![Field::new("name", DataType::Utf8, false), Field::new("quantity", DataType::Int32, false)]));\nlet columns: Vec<ArrayRef> = vec![Arc::new(StringArray::from(vec!["pear", "apple"])), Arc::new(Int32Array::from(vec![2, 3]))];\nlet batch = RecordBatch::try_new(schema, columns)?;\nassert_eq!((batch.num_rows(), batch.num_columns()), (2, 2));\nassert_eq!(batch.column(0).as_any().downcast_ref::<arrow::array::StringArray>().unwrap().value(0), "pear");',
        "Two aligned columns form a two-row, two-column batch.",
        "Names and types are explicit rather than inferred from arbitrary array positions.",
    ),
    (
        "Reject incompatible lengths",
        'use std::sync::Arc;\nuse arrow::array::{ArrayRef, Int32Array};\nuse arrow::datatypes::{DataType, Field, Schema};\nuse arrow::record_batch::RecordBatch;\nlet schema = Arc::new(Schema::new(vec![Field::new("a", DataType::Int32, false), Field::new("b", DataType::Int32, false)]));\nlet columns: Vec<ArrayRef> = vec![Arc::new(Int32Array::from(vec![1, 2])), Arc::new(Int32Array::from(vec![3]))];\nassert!(RecordBatch::try_new(schema, columns).is_err());',
        "Unequal column lengths are rejected.",
        "A batch cannot invent which row a shorter column should align with.",
    ),
    [
        "State the row grain and schema of the valid batch.",
        "Add a nullable numeric field with matching length.",
        "Construct a batch for a small validated inventory dataset.",
        "Diagnose swapping arrays while retaining the old field order.",
        "Test type mismatch, length mismatch and a zero-row batch.",
        "Design a schema evolution policy that preserves names, units and saved data meaning.",
    ],
    "A nullable field permits nulls; it does not require them. Schema validation does not establish unique keys or domain ranges. Do not infer whole-dataset row count from one batch.",
    source="https://docs.rs/arrow/60.0.0/arrow/record_batch/struct.RecordBatch.html",
)

lesson(
    "Compute kernels, filtering and row selection",
    """Arrow compute kernels operate on arrays while respecting their logical representation. A Boolean mask selects rows; take selects positions by an index array. These are different operations with different output ordering. Filtering normally preserves the order of admitted rows, while take can repeat or reorder positions.

Type erasure means a kernel can return ArrayRef. Inspect or validate the logical type before downcasting to a concrete array. An unwrap can be justified only by a nearby known kernel/type contract in a controlled fixture. Production generic code should return a useful error for an unexpected type. Preserve null and index bounds policies explicitly.""",
    "compute::filter accepts an array and BooleanArray mask. compute::take selects by integer indices. as_any().downcast_ref recovers a known concrete array after the type contract has been established.",
    [
        ("Kernel", "A reusable array computation."),
        ("Filter mask", "A Boolean decision per input row."),
        ("Take indices", "Positions selecting and potentially reordering rows."),
    ],
    (
        "Filter with an explicit mask",
        "use arrow::array::{BooleanArray, Int32Array};\nlet values = Int32Array::from(vec![2, 4, 6]);\nlet mask = BooleanArray::from(vec![true, false, true]);\nlet result = arrow::compute::filter(&values, &mask)?;\nlet typed = result.as_any().downcast_ref::<Int32Array>().unwrap();\nassert_eq!(typed.iter().collect::<Vec<_>>(), vec![Some(2), Some(6)]);",
        "Filtering retains two and six in input order.",
        "The mask expresses one admission decision for every original position.",
    ),
    (
        "Reorder and repeat with take",
        "use arrow::array::{Int32Array, UInt32Array};\nlet values = Int32Array::from(vec![2, 4, 6]);\nlet indices = UInt32Array::from(vec![2, 0, 2]);\nlet result = arrow::compute::take(&values, &indices, None)?;\nlet typed = result.as_any().downcast_ref::<Int32Array>().unwrap();\nassert_eq!(typed.iter().collect::<Vec<_>>(), vec![Some(6), Some(2), Some(6)]);",
        "Take repeats and reorders values according to the index sequence.",
        "A selected row can appear more than once, so cardinality and aggregation assumptions need review.",
    ),
    [
        "Predict row count and order for both operations.",
        "Change one mask value and independently derive the result.",
        "Filter every column of a batch consistently under one row mask.",
        "Diagnose filtering one column while leaving others unfiltered.",
        "Test empty selection, all-selected rows and checked invalid indices.",
        "Choose filter or take for a sampling procedure and explain duplicate-row consequences.",
    ],
    "Downcast failure is possible in generic code. A mask and array must have compatible lengths. A kernel result does not establish a domain-level ordering guarantee unless the operation contract does.",
    source="https://docs.rs/arrow/60.0.0/arrow/compute/",
)

lesson(
    "Variable-width arrays, nested values and zero-copy slices",
    """Variable-width arrays use offsets to locate each logical value in a shared data region. Nested list arrays add another layer: a parent position can be null, an empty list, or a nonempty list whose children may themselves be null. These states carry different meanings and must not be flattened indiscriminately.

Arrow slices often share underlying buffers instead of copying all data. This makes views cheap, but a small retained slice can keep a large allocation alive. Logical offsets and validity still matter. Zero-copy is a specific ownership and representation property, not a blanket claim that an entire analytical pipeline performs no allocations.""",
    "ListBuilder<Int32Builder> appends child values, then append(true) closes a valid parent list. append(false) adds a null parent. Array::slice creates a logical view over a selected region.",
    [
        ("Offset buffer", "Positions locating variable-width logical values."),
        ("Nested validity", "Separate nullability at parent and child levels."),
        ("Zero-copy view", "A view sharing existing storage rather than duplicating its payload."),
    ],
    (
        "Distinguish nonempty, empty and null lists",
        "use arrow::array::{Array, Int32Builder, ListBuilder};\nlet mut builder = ListBuilder::new(Int32Builder::new());\nbuilder.values().append_value(2); builder.values().append_null(); builder.append(true);\nbuilder.append(true);\nbuilder.append(false);\nlet lists = builder.finish();\nassert_eq!(lists.len(), 3);\nassert_eq!(lists.value_length(0), 2);\nassert_eq!(lists.value_length(1), 0);\nassert!(lists.is_null(2));",
        "The three rows are a two-child list, an empty list and a null list.",
        "The first row even contains a null child, demonstrating independent validity levels.",
    ),
    (
        "Slice without confusing logical positions",
        'use arrow::array::{Array, StringArray};\nlet values = StringArray::from(vec!["first", "middle", "last"]);\nlet slice = values.slice(1, 1);\nlet typed = slice.as_any().downcast_ref::<StringArray>().unwrap();\nassert_eq!(typed.len(), 1);\nassert_eq!(typed.value(0), "middle");',
        "The sliced array exposes middle at its logical index zero.",
        "A view's logical indices are interpreted relative to the sliced array rather than the original source positions.",
    ),
    [
        "Classify parent-null, empty and child-null states.",
        "Add another valid list with two non-null children.",
        "Build a nested column from a small ragged dataset.",
        "Diagnose treating an empty list as equivalent to a missing list.",
        "Test zero-length slices and nonzero source offsets.",
        "Explain when retaining a tiny shared slice may retain excessive memory and when copying is justified.",
    ],
    "Nested nullability has several layers. Zero-copy views can extend buffer lifetime. Do not manually manipulate offset buffers without validating every format invariant.",
    source="https://arrow.apache.org/docs/format/Columnar.html",
)

lesson(
    "Arrow IPC and explicit stream completion",
    """Arrow IPC is a binary interchange format carrying schemas and record batches. It is useful for exchanging Arrow data without converting every value through a text representation. The stream and file formats have different framing and access properties. A stream reader needs a complete schema message before decoding batches, and a writer must be finished to complete its framing.

IPC preserves a representation contract, not an entire application protocol. Bound message sizes, validate schemas and retain ownership of buffers. The classroom writes to an in-memory byte vector and reads it back, so the example remains offline and does not imply an external file-transfer channel exists in the coding pad.""",
    "StreamWriter::try_new accepts a writer and schema. write appends a batch; finish closes the stream framing. StreamReader::try_new consumes a reader and optional projection. Each yielded batch is fallible.",
    [
        ("IPC", "Inter-process communication format for Arrow schemas and batches."),
        ("Framing", "The structure separating messages in a byte stream."),
        ("Round trip", "Encoding and decoding while checking retained logical meaning."),
    ],
    (
        "Round-trip a complete IPC stream",
        'use std::sync::Arc;\nuse std::io::Cursor;\nuse arrow::array::{ArrayRef, Int32Array};\nuse arrow::record_batch::RecordBatch;\nuse arrow::ipc::{reader::StreamReader, writer::StreamWriter};\nlet batch = RecordBatch::try_from_iter(vec![("quantity", Arc::new(Int32Array::from(vec![2, 3])) as ArrayRef)])?;\nlet mut bytes = Vec::new();\n{ let mut writer = StreamWriter::try_new(&mut bytes, &batch.schema())?; writer.write(&batch)?; writer.finish()?; }\nlet mut reader = StreamReader::try_new(Cursor::new(bytes), None)?;\nlet restored = reader.next().unwrap()?;\nassert_eq!(restored, batch);\nassert!(reader.next().is_none());',
        "The schema and two values round-trip as one complete batch.",
        "Finishing the writer and exhausting the reader establish the bounded stream outcome.",
    ),
    (
        "Reject invalid framing",
        "use std::io::Cursor;\nuse arrow::ipc::reader::StreamReader;\nassert!(StreamReader::try_new(Cursor::new(vec![1_u8, 2, 3]), None).is_err());",
        "Arbitrary bytes are rejected as an IPC stream.",
        "A binary buffer is not trusted merely because an application labels it Arrow.",
    ),
    [
        "Trace schema, batch and finish operations.",
        "Write two batches with the same schema and count them on readback.",
        "Build an in-memory IPC round trip preserving a nullable column.",
        "Diagnose reading before writer completion or ignoring a reader error.",
        "Test malformed bytes and an empty-batch stream with a valid schema.",
        "Design an IPC transport with size limits, schema checks and explicit ownership of received buffers.",
    ],
    "IPC is not encryption or authentication. A valid schema can still describe unwanted data. Do not assume a file reader and stream reader accept identical framing.",
    source="https://arrow.apache.org/docs/format/Columnar.html#serialization-and-interprocess-communication-ipc",
)

lesson(
    "CSV and JSON readers with explicit schemas",
    """CSV and JSON are external representations with their own syntax and ambiguity. CSV supports quoted delimiters and escaped quotes, so a naive split is not a general parser. JSON can contain fields with inconsistent types across records. An explicit Arrow schema gives the reader a target contract and makes incompatible values visible.

Automatic inference is useful exploration but should not silently become a production schema policy. A sample may miss later nulls or wider numeric ranges. Bound input size and batch size, inspect errors and validate domain constraints after decoding. The prepared crate includes actual CSV and newline-delimited JSON reader features; no separate package is fetched during a run.""",
    "CSV ReaderBuilder takes a schema and with_header policy. JSON ReaderBuilder consumes newline-delimited object records. Both readers yield fallible RecordBatch values, and batch size bounds one produced chunk.",
    [
        ("Schema inference", "Estimating a schema from observed data."),
        ("NDJSON", "JSON objects separated by newlines for record-oriented streaming."),
        ("Batch size", "The maximum records targeted in one reader output batch."),
    ],
    (
        "Read CSV through its real parser",
        'use std::sync::Arc;\nuse std::io::Cursor;\nuse arrow::datatypes::{DataType, Field, Schema};\nlet schema = Arc::new(Schema::new(vec![Field::new("name", DataType::Utf8, false), Field::new("quantity", DataType::Int32, false)]));\nlet input = b"name,quantity\\npear,2\\napple,3\\n";\nlet mut reader = arrow::csv::ReaderBuilder::new(schema).with_header(true).with_batch_size(8).build(Cursor::new(input))?;\nlet batch = reader.next().unwrap()?;\nassert_eq!((batch.num_rows(), batch.num_columns()), (2, 2));\nassert_eq!(batch.column(0).as_any().downcast_ref::<arrow::array::StringArray>().unwrap().value(0), "pear");',
        "The parser produces two rows under the explicit schema.",
        "Header handling and column types are deliberate rather than guessed from a hand-written split.",
    ),
    (
        "Read newline-delimited JSON",
        'use std::sync::Arc;\nuse std::io::Cursor;\nuse arrow::array::Int32Array;\nuse arrow::datatypes::{DataType, Field, Schema};\nlet schema = Arc::new(Schema::new(vec![Field::new("quantity", DataType::Int32, true)]));\nlet input = b"{\\"quantity\\":2}\\n{\\"quantity\\":null}\\n";\nlet mut reader = arrow::json::ReaderBuilder::new(schema).with_batch_size(8).build(Cursor::new(input))?;\nlet batch = reader.next().unwrap()?;\nlet values = batch.column(0).as_any().downcast_ref::<Int32Array>().unwrap();\nassert_eq!(values.iter().collect::<Vec<_>>(), vec![Some(2), None]);',
        "JSON null becomes Arrow null under the declared nullable field.",
        "Structural decoding retains missingness rather than converting it to zero.",
    ),
    [
        "State the schema and framing expected by each reader.",
        "Add a CSV quoted field containing a comma and inspect its single parsed value.",
        "Read a small nullable dataset and validate its domain ranges afterward.",
        "Diagnose using the foundation split_once parser for general quoted CSV.",
        "Test malformed numeric text, explicit null and records spanning more than one batch.",
        "Design an inference-to-reviewed-schema workflow with checks for later type and nullability drift.",
    ],
    "NDJSON is not a single enclosing JSON array. Reader success does not establish domain validity. Always handle each yielded batch error rather than counting only successful batches.",
    source="https://docs.rs/arrow/60.0.0/arrow/",
)

lesson(
    "Cross-language data contracts: decimals, timestamps and metadata",
    """Cross-language interoperability succeeds when logical meaning agrees, not merely when bytes can be transferred. Decimal scale identifies how an integer coefficient maps to a decimal quantity. Timestamp units identify the precision of an epoch-based value, and time-zone metadata affects interpretation. A millisecond value read as seconds can be wildly wrong while remaining a valid integer.

Arrow metadata can record application meaning such as units, but consumers must agree to interpret it. IPC provides a portable transport; the C Data Interface provides an in-process ownership boundary and requires separate FFI preparation. The default pad does not enable every FFI feature or install PyArrow, Parquet or DataFusion. Keep these ecosystem boundaries explicit.""",
    "Decimal128Array::with_precision_and_scale sets decimal interpretation. TimestampMillisecondArray carries a specific unit and can attach timezone metadata. data_type exposes the logical contract independently of physical integer access.",
    [
        (
            "Decimal scale",
            "The number of fractional decimal places represented by an integer coefficient.",
        ),
        ("Timestamp unit", "The time increment represented by one stored integer unit."),
        (
            "Interchange contract",
            "Agreement about types, nulls, units, ownership and framing across consumers.",
        ),
    ],
    (
        "Preserve decimal interpretation",
        "use arrow::array::{Array, Decimal128Array};\nuse arrow::datatypes::DataType;\nlet prices = Decimal128Array::from(vec![125_i128, 250]).with_precision_and_scale(10, 2)?;\nassert_eq!(prices.value(0), 125);\nassert_eq!(prices.data_type(), &DataType::Decimal128(10, 2));",
        "Coefficient 125 with scale two represents 1.25 under the declared contract.",
        "The raw coefficient alone does not state the decimal amount.",
    ),
    (
        "Keep timestamp units explicit",
        'use arrow::array::{Array, TimestampMillisecondArray};\nuse arrow::datatypes::{DataType, TimeUnit};\nlet times = TimestampMillisecondArray::from(vec![0_i64, 1000]).with_timezone("UTC");\nassert_eq!(times.value(1), 1000);\nassert_eq!(times.data_type(), &DataType::Timestamp(TimeUnit::Millisecond, Some("UTC".into())));',
        "The second value is one thousand milliseconds after the epoch.",
        "The logical type prevents a consumer from legitimately treating the same coefficient as seconds without conversion.",
    ),
    [
        "Explain coefficient, scale and represented amount separately.",
        "Add a negative decimal coefficient and retain its scale.",
        "Create a schema documenting measurement units and timestamp precision.",
        "Diagnose reading milliseconds as seconds or losing decimal scale.",
        "Test null decimal/timestamp values and a schema mismatch.",
        "Plan a separately prepared Rust-to-PyArrow IPC round trip that checks schema, nulls, decimal scale and timestamp units in both languages.",
    ],
    "An integer cast is not a timestamp-unit conversion. Time-zone metadata is not a complete application scheduling policy. C Data Interface release callbacks and lifetime ownership require a reviewed FFI implementation.",
    source="https://arrow.apache.org/docs/format/CDataInterface.html",
)

lesson(
    "Bounded batch pipelines and data accounting",
    """A data pipeline needs bounds on admitted input, buffered batches, memory and output. Processing one batch at a time can reduce peak memory, but retaining every batch in a result vector defeats that design. A batch size is not a total-job limit, and one variable-width value can still be very large.

Preserve accounting at every boundary: submitted rows, valid rows, rejected rows and output rows should have defined relationships. Filtering changes row count while projection changes columns. Cancellation and partial failure need explicit outcome semantics so an incomplete report is not presented as complete. The fixture demonstrates deterministic batch accounting without a remote source.""",
    "Chunking a slice gives bounded views of owned input. An accumulator stores only the required summary. Checked arithmetic and explicit row counters prevent silent overflow or dropped-record accounting.",
    [
        ("Admission bound", "A limit on work accepted into processing."),
        ("Streaming aggregation", "Updating a summary without retaining all prior records."),
        ("Accounting invariant", "A defined relationship between input and outcome counts."),
    ],
    (
        "Aggregate bounded chunks",
        "let values = [1_i32, 2, 3, 4, 5];\nlet mut total = 0;\nlet mut rows = 0;\nfor batch in values.chunks(2) { rows += batch.len(); total += batch.iter().sum::<i32>(); }\nassert_eq!((rows, total), (5, 15));",
        "Three chunks account for five rows and total fifteen.",
        "The summary retains only counters, not a duplicate copy of every processed batch.",
    ),
    (
        "Account for rejected rows",
        "let values = [2, -1, 0, 3];\nlet accepted: Vec<_> = values.iter().copied().filter(|value| *value >= 0).collect();\nlet rejected = values.len() - accepted.len();\nassert_eq!(accepted, vec![2, 0, 3]);\nassert_eq!(accepted.len() + rejected, values.len());",
        "Valid zero is retained and every input row is accounted for.",
        "A rejection policy must preserve the denominator needed to interpret the result.",
    ),
    [
        "Trace chunk sizes and cumulative row counts.",
        "Change the chunk size without changing the final result.",
        "Apply the same accounting to an Arrow batch reader.",
        "Diagnose collecting all batches before claiming bounded-memory processing.",
        "Test empty input, an all-rejected batch and a partial final batch.",
        "Design cancellation and partial-output semantics for a long-running import.",
    ],
    "Batch size alone does not bound total memory or individual value size. A partial result needs an explicit incomplete status. Do not infer complete input consumption from a valid first batch.",
)

lesson(
    "Diagnostics, security boundaries and safe output",
    """Operational evidence should explain an outcome without exposing raw private input. Use stable stages, result categories and bounded counters. A parsing error, rejected domain value and unknown external effect are different categories. Correlation identity connects observations of one operation without embedding credentials or payloads.

Security boundaries appear wherever data gains authority: paths reach files, text becomes commands, or requests select resources. Prefer fixed reviewed operations and typed parsing over string-built commands. Rust memory safety does not provide authentication, authorization or an input-size policy. Keep those responsibilities visible in system design.""",
    "A diagnostic record can contain a fixed operation ID, stage, outcome and count. Match exact allowed actions rather than executing arbitrary input. Format only reviewed fields and bound output volume.",
    [
        ("Correlation identity", "A value connecting observations of one operation."),
        ("Authorization", "A decision about permitted actions on a resource."),
        ("Allowlist", "An explicit set of admitted values or operations."),
    ],
    (
        "Describe outcome without raw payload",
        'let event = Event { operation: "fixture-1", stage: "validate", outcome: "rejected", count: 2 };\nassert_eq!(event.render(), "fixture-1 validate rejected count=2");',
        "The event retains useful context without echoing input contents.",
        "The field set is intentionally small and reviewable.",
    ),
    (
        "Reject unlisted actions",
        'let allowed = ["report:read", "report:list"];\nassert!(allowed.contains(&"report:read"));\nassert!(!allowed.contains(&"report:delete"));',
        "Only explicitly listed actions are admitted.",
        "A missing policy entry is not implicit permission.",
    ),
    [
        "Identify every field safe to emit in the event.",
        "Add a fixed stage category without adding raw input.",
        "Instrument an importer with submitted, accepted and rejected counts.",
        "Diagnose including a token or entire source record in an error message.",
        "Test missing permissions and empty workloads.",
        "Design a fixed-operation boundary that separates validated data from executable instructions.",
    ],
    "Memory safety does not make arbitrary command execution safe. Do not log secrets or unbounded payloads. A successful process exit can still contain domain rejections that need explicit reporting.",
    helpers="struct Event { operation: &'static str, stage: &'static str, outcome: &'static str, count: usize }\nimpl Event { fn render(&self) -> String { format!(\"{} {} {} count={}\", self.operation, self.stage, self.outcome, self.count) } }",
)

lesson(
    "Properties, compile-fail cases and regression design",
    """Advanced verification combines examples, properties and boundary-specific evidence. A property such as sorting preserving element multiplicity can expose mistakes that one expected list misses. Compile-fail tests can preserve an API\'s ownership or visibility restrictions, but they belong to a deliberately prepared test harness rather than an ordinary successful runtime reference.

Fuzzing and property-testing crates are valuable external tools, not hidden dependencies in this pad. Start with deterministic exhaustive enumeration over a small bounded domain and an independent oracle. Keep minimized counterexamples when a failure appears. Never weaken an invariant to accommodate a wrong implementation merely because a large suite is expensive.""",
    "Nested loops can enumerate a small input space reproducibly. A sorted clone can be compared with the original through a frequency map. Compile diagnostics should be categorized by the violated rule rather than fragile full-message text.",
    [
        ("Property test", "A test of a relationship across many inputs."),
        ("Counterexample", "An input disproving a claimed property."),
        (
            "Compile-fail test",
            "Evidence that an invalid program is rejected by the intended language contract.",
        ),
    ],
    (
        "Check a bounded algebraic property",
        "for a in 0_i32..10 { for b in 0_i32..10 { assert_eq!(a + b, b + a); } }\nassert_eq!(10 * 10, 100);",
        "One hundred bounded pairs satisfy the addition relation.",
        "The range avoids overflow, making the mathematical property appropriate to this representation.",
    ),
    (
        "Check order and multiplicity separately",
        "let original = vec![3, 1, 3, 2];\nlet mut sorted = original.clone(); sorted.sort();\nassert!(sorted.windows(2).all(|pair| pair[0] <= pair[1]));\nfor value in 1..=3 { assert_eq!(original.iter().filter(|item| **item == value).count(), sorted.iter().filter(|item| **item == value).count()); }",
        "Sorting establishes order without losing the repeated three.",
        "Order alone would not reject a broken implementation that drops duplicates.",
    ),
    [
        "State the assumptions making the bounded arithmetic property valid.",
        "Add a small exhaustive test for checked quantity addition.",
        "Write a property checking an Arrow filter's output count against its Boolean mask.",
        "Diagnose a sortedness test that never checks retained values.",
        "Preserve empty, duplicate and all-null regression fixtures.",
        "Design an external fuzzing and compile-fail plan with reproducible seeds, minimized failures and clear acceptance scope.",
    ],
    "A property can be too weak to distinguish incorrect implementations. Integer overflow can invalidate a mathematical law's assumed domain. Compiler message wording may change even when the underlying rule remains correct.",
)

lesson(
    "Capstone: a validated Arrow analytical report",
    """The final project combines a schema, nullable columns, domain admission and a deterministic report. Arrow provides the representation and kernels; the application owns what counts as a valid measurement and how rejection is reported. A correct total must state its population and handling of missing values.

Build the portable kernel first, then extend the external InventoryLab or a separately prepared Arrow Cargo project. Keep package resolution, source compilation, runtime assertions, browser delivery and cross-language interchange evidence separate. Expert practice includes explaining limits and diagnosing unfamiliar failures, not assuming a finite tutorial covers every library or production architecture.""",
    "A typed nullable array exposes valid values through Option iteration. The application can count nulls, reject negative present values and sum the admitted population. A stable report record makes those decisions inspectable.",
    [
        (
            "Analytical contract",
            "The population, units and missingness rules defining a calculation.",
        ),
        ("Acceptance evidence", "Observed results establishing a declared requirement."),
        ("Extension boundary", "A deliberate interface for adding a new capability."),
    ],
    (
        "Summarize a nullable measurement column",
        "use arrow::array::{Array, Int32Array};\nlet values = Int32Array::from(vec![Some(2), None, Some(3), Some(-1), Some(0)]);\nlet accepted: Vec<_> = values.iter().flatten().filter(|value| *value >= 0).collect();\nassert_eq!(accepted.iter().sum::<i32>(), 5);\nassert_eq!(accepted.len(), 3);\nassert_eq!(values.null_count(), 1);\nassert_eq!(values.len() - values.null_count() - accepted.len(), 1);",
        "Three valid nonnegative values total five, alongside one null and one rejected negative.",
        "The calculation preserves a complete accounting of its five input positions.",
    ),
    (
        "Keep empty and all-null data distinct",
        "use arrow::array::{Array, Int32Array};\nlet empty = Int32Array::from(Vec::<Option<i32>>::new());\nlet missing = Int32Array::from(vec![None::<i32>, None]);\nassert_eq!((empty.len(), empty.null_count()), (0, 0));\nassert_eq!((missing.len(), missing.null_count()), (2, 2));",
        "No submitted rows and two missing observations remain different reports.",
        "A total of zero alone cannot express this distinction.",
    ),
    [
        "Trace each value to accepted, null or rejected accounting.",
        "Add another valid value and independently derive the new report.",
        "Build a multi-column RecordBatch report and round-trip it through IPC.",
        "Introduce and diagnose a null-as-zero, schema-order or duplicate-row defect.",
        "Test empty, all-null, all-rejected, overflow and malformed-input boundaries.",
        "Deliver a project README with schema, ownership, bounds, failure policies, actual runtime evidence and one independent Arrow extension.",
    ],
    "A passing kernel does not prove external storage, authentication or every architecture. Do not label Parquet, DataFusion or a distributed service supported without explicit dependency and runtime qualification. Retain source-bound evidence for the program actually executed.",
    notes="Use [InventoryLab](../fixtures/InventoryLab/README.md) for the real library/project structure. The Arrow classroom dependency is already prepared; any independent Cargo project must deliberately prepare and lock Arrow60 before claiming offline builds.",
    source="https://docs.rs/arrow/60.0.0/arrow/",
)
