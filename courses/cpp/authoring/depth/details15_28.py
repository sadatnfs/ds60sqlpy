DETAILS = {
    15: (
        "Exclusive ownership and deterministic destruction",
        """A unique_ptr represents one owning responsibility for a dynamically allocated object. The pointee can be borrowed through a raw pointer or reference, but those borrows do not become additional owners. When the unique_ptr is destroyed, its deleter releases the resource. The useful property is not that delete disappeared syntactically; it is that cleanup follows the lifetime of a visible owner on every ordinary scope-exit path.

make_unique<int>(7) constructs an int and returns its owner. Moving p into q transfers that owning responsibility, leaving p empty for unique_ptr's specified move behavior. It does not move the integer7 to a different allocation in this example. The address can stay the same while the object responsible for cleanup changes. Dereferencing the moved-from p would be invalid because it no longer owns or points to the integer.

The Tracked fixture uses a counter to make lifetime observable. Construction increments live and destruction decrements it. Inside the owner scope, live is1; after the scope, it is0. The counter itself must outlive Tracked because Tracked borrows its address. A resource wrapper can still contain an unsafe borrow if that dependency is ignored. RAII solves cleanup ownership, not every possible lifetime relationship automatically.

Exception unwinding destroys fully constructed local owners. If a later operation throws, a unique_ptr already in scope still releases its pointee. By contrast, a raw new followed by a throwing operation before a matching delete can leak. The correct fix is to establish ownership immediately, not to add a delete to one guessed error branch. For non-memory resources, the same structure can use an appropriate custom deleter.

Exclusive ownership is not appropriate for every graph. shared_ptr introduces shared lifetime responsibility and additional costs, while raw pointers can express non-owning access. Choose based on who must keep the object alive, not on which pointer syntax seems easiest. The examples deliberately avoid shared ownership so the transfer and destruction points are inspectable.""",
        """If live remains1 after the scope, inspect whether ownership escaped or was released without cleanup. If a moved-from unique_ptr is dereferenced, test its empty state and use the new owner instead. Do not construct two unique_ptr objects from the same raw pointer: that creates two deletion responsibilities for one allocation. A destructor counter proves the fixture lifecycle, not the safety of every borrowed pointer elsewhere in the program.""",
    ),
    16: (
        "Copy, move and the state left behind",
        """Copying a value preserves the source and creates another value with the type's copy semantics. Moving allows a destination to take resources from a source that will no longer be used in the same way. std::move itself is a cast that makes a move-capable overload eligible; it does not perform resource transfer on its own. The selected constructor or assignment operator determines what actually happens.

Batch contains vector and string members, so generated operations compose those members' semantics. Copying a Batch copies its vector elements and label. Mutating the copied vector does not change the original. Moving a Batch can transfer member resources efficiently, but the source remains a valid object whose exact values should not be assumed unless its type contract specifies them. In particular, do not assert that every moved-from vector or string must be empty.

The second program checks the destination values and then assigns a fresh Batch to the moved-from source. This tests a useful guaranteed operation: reusing a valid object through assignment. Reading an unspecified old label and treating it as a meaningful business value would be a different, unjustified assumption. Valid means permitted operations remain possible under their preconditions, not that all previous content survives.

The rule of zero favors types composed of well-behaved owning members so that manually written copy/move/destruction logic is unnecessary. Once a class owns a raw resource directly, those special operations must be designed together to avoid shallow copies, double release or lost ownership. A custom destructor can also affect implicit move generation, so adding one is not always a harmless logging change.

Performance claims need observation. Moving a tiny value can be no cheaper than copying, and library exception guarantees may influence whether a container copies or moves elements during reallocation. Correctness should follow the type contract first. A benchmark can then measure the actual workload and implementation rather than assuming every occurrence of std::move made the program faster.""",
        """If changing a copy changes the original, inspect whether the member is truly owning or merely a pointer/view. If a moved-from value is used for business logic, replace the assumption with a documented post-move operation or explicit reassignment. If a class becomes unexpectedly non-movable after adding a destructor, review the generated special-member rules. Do not add std::move indiscriminately to return statements or const objects without understanding overload selection.""",
    ),
    17: (
        "Representing failure as data or control flow",
        """An operation can fail without producing a valid result. The interface must make that distinction visible. optional<T> represents either a value or absence, but carries no detailed error by itself. variant<int,ParseError> can represent a successful integer or a structured reason. An exception transfers control to a matching handler and can unwind intermediate scopes. These choices express different contracts rather than one universally best error style.

The positive function accepts zero because nonnegative includes the boundary. Its success alternative contains int0. The failure alternative for -1 contains ParseError with reason negative. holds_alternative checks which type is active before the caller extracts a value. Treating the variant as though it always held int would lose the error path; using get on the wrong alternative can itself throw bad_variant_access.

Error context should explain the input boundary without exposing unnecessary data. A parser might retain row number and a reason code while avoiding a complete sensitive record. A small structured error also supports exact tests and programmatic handling more reliably than matching a long free-form sentence. The teaching reason string is deliberately simple, not a complete production diagnostic schema.

Choose a consistent handling boundary. If a lower-level parser returns a variant, the caller should deliberately decide whether to count a rejected row, abort the operation or translate the error into an exception. Silently substituting zero for every failure makes invalid input indistinguishable from legitimate zero. Conversely, aborting an entire batch for one malformed row may violate a declared partial-acceptance policy.

Exceptions and RAII work together when a failure crosses several calls. Returned error values can make expected local alternatives explicit. In both designs, test that success and failure have different observable results and that required cleanup/accounting still happens. A function that prints an error but returns an apparently valid value leaves callers unable to enforce the contract.""",
        """When a bad input contributes zero to a total, inspect whether rejection was collapsed into a default value. When variant access throws unexpectedly, inspect the active alternative before extraction. When an exception is swallowed, verify that the caller still records failure and does not publish a normal result. Test zero, negative input and the largest supported valid value separately because they exercise different parts of the domain boundary.""",
    ),
    18: (
        "Views describe storage without owning it",
        """A span describes a contiguous sequence using an address and an extent. A string_view describes characters similarly. Neither owns the underlying storage. Copying a view copies that description, not the elements, so the owner must remain alive and its storage valid for every use. A view is useful for avoiding unnecessary copies only when that lifetime relationship is clear.

The first program borrows a vector through span<const int> and selects subspan(1,2). The offset1 skips the first element and count2 selects4 and6. The sum is10. The operation does not allocate a new vector. The caller must satisfy the subspan bounds; a view type does not make every offset/count automatically safe. Validate externally supplied ranges before constructing or slicing views.

The second program creates a two-character view over alpha. Changing the first character of the owning string in place makes the view observe Al. This illustrates aliasing: the view is not a frozen snapshot. A string reallocation or destruction would instead invalidate the view. The safe example changes an existing character without altering storage capacity and checks the result while the owner remains in scope.

Const in span<const int> blocks writing elements through that view. It does not prevent another mutable alias from changing the same vector. A function that needs a stable snapshot across later mutation should own a copy or establish a stronger synchronization/lifetime contract. Read-only access and immutable data are different promises.

Returning a view requires identifying an owner that survives the function. Returning a span into a local vector is dangling immediately after return. Returning an owning vector is often the clearer result when the function creates new data. A view into a caller-owned object can be appropriate, but the caller must know which later edits or destruction invalidate it. Document those operations alongside the return type.""",
        """A view that worked once can still be dangling. Inspect owner scope and reallocating operations rather than trusting printed bytes. If a returned view points into a local temporary, change the ownership design. If a span slice is out of range, fix the offset/count contract before access. If a supposedly constant result changes, check whether the program borrowed a mutable owner instead of taking a snapshot.""",
    ),
    19: (
        "Lazy ranges, predicates and projections",
        """A range provides a sequence to traverse. A view is commonly a lightweight, lazy description of a transformation over a range. Building a filter view does not necessarily evaluate the predicate for every element immediately. Iteration performs the work needed to produce values. This distinction matters when the underlying data changes or a predicate has side effects.

The first program filters [-1,0,3] with x>=0 and materializes the observed result into a vector. Zero is retained because the boundary is inclusive. The view itself does not erase -1 from the original vector. Materialization creates an owning result with a stable sequence independent of later changes to the input. Without that step, the view remains coupled to its source and its lifetime/invalidation rules.

The projection in ranges::sort(scores,{},&Score::points) selects which member participates in comparison. The empty braces choose the default comparator; the member pointer supplies a projection from Score to points. Sorting moves whole Score values, so IDs remain attached to their corresponding points. Sorting a separate points vector without preserving identity would answer a different question.

A predicate should be understandable as a rule over an element. Side effects such as incrementing an external counter can make the result depend on how often and when the range implementation evaluates it. Do not use an assumed predicate-call count as a business result unless the algorithm explicitly guarantees it. Keep counting as a separate deliberate operation when that count is part of the contract.

Views also require care around temporary owners. A pipeline that safely owns or references its source under one type combination is not proof that every returned view survives. When a function returns a filtered result for later use, an owning vector may be the simplest correct interface. The later generic-pipeline lesson develops this boundary for single-pass input ranges.""",
        """If the original vector changed after filtering, inspect whether the code actually used an erasing algorithm. If a view later reads garbage, trace its owner lifetime and invalidation. If IDs no longer match scores, check whether fields were sorted separately. If a lambda counter produces a surprising total, remove side effects and reason from the algorithm's traversal contract rather than guessing how many times the predicate runs.""",
    ),
    20: (
        "Templates and constraints as interface documentation",
        """A function template describes a family of functions parameterized by types or values. The compiler instantiates the needed specialization from a call. Generic syntax alone does not explain what operations are valid for a type, so constraints can make the intended domain visible before a deeply nested implementation error appears.

The integral constraint says that the type belongs to the language/library concept for integral types. The complete program instantiates identity_sum for integers and checks2+3=5. The second program uses static_assert to establish that double is not integral. That assertion is checked during compilation and produces no runtime branch. The actual negative exercise attempts a constrained call with double and retains the compiler diagnostic.

A syntactic constraint is not the whole semantic contract. Integral addition can still overflow for signed types, and mixing signed and unsigned arguments can affect deduction or conversions. A template constrained to integral types must still state supported value ranges and any overflow policy. Concepts should not be advertised as automatic arithmetic safety or proof of all algorithm assumptions.

Template argument deduction also requires compatible inputs. A function taking two values of the same template parameter may reject an int and long combination even when a programmer considers both numbers. An explicit conversion can resolve the call, but it should be deliberate because narrowing or sign changes can lose meaning. Inspect the inferred types when a call does not match expectations.

Good constraints describe the weakest capabilities the implementation actually needs. Requiring a random-access container for a one-pass accumulation unnecessarily excludes useful inputs. Conversely, accepting any type while relying on an undocumented operation shifts the error into the implementation. The aim is a readable contract and useful diagnostics, followed by ordinary value-boundary tests.""",
        """If template errors are long, find the first failed constraint or mismatched deduced type rather than the final cascade. If a valid type produces a wrong numeric result, inspect values and conversions: type constraints do not prevent overflow. If an interface rejects an input range unnecessarily, compare the declared capability with the operations actually used. Do not weaken every constraint to make one call compile without reviewing the algorithm assumptions.""",
    ),
    21: (
        "Strong domain types and operator meaning",
        """Two integers can have incompatible meanings even when their machine representation is identical. A Cents type makes a monetary unit visible at function boundaries. It can prevent a caller from accidentally passing a raw row count where a price is expected, provided its constructors and conversions preserve that separation. This is a domain-model benefit rather than a different arithmetic engine.

An overloaded operator should preserve a familiar, documented meaning. Adding two Cents values produces a Cents result; comparing two values compares their amounts. The complete examples check125=25+100 and the zero identity. They do not establish currency conversion, rounding policy or overflow handling. Those requirements would need distinct types or explicit functions and tests.

The zero value is useful because it supplies an identity for accumulation. If price+zero changes price, either the operator or the type invariant is wrong. Equality should compare the semantic value represented by the type, not an incidental address. In a richer money type, currency would also matter: equal numeric amounts in different currencies should not be casually added.

Operator syntax can hide cost and failure. A small Cents addition is simple, while an overloaded plus that performs network I/O or mutates unrelated state would violate ordinary reader expectations. Prefer explicit named operations when behavior is surprising or requires a policy argument. The goal is clearer code, not making every business action look like arithmetic.

Construction is the boundary where invalid states should be considered. If negative cents are forbidden in one domain but valid for a signed balance in another, one universal wrapper may be misleading. State the type's invariant and choose names accordingly. The lesson uses a tiny representation so the learner can separate unit correctness from the later checked-arithmetic policy.""",
        """If raw integers slip into a Cents API unexpectedly, inspect implicit constructors and conversion operators. If an operator mutates its left input when it is expected to return a new value, compare the intended value semantics with the implementation. If a large amount wraps or overflows, strong typing alone is not enough: add the numeric range policy. Keep unit tests distinct from arithmetic-boundary tests.""",
    ),
    22: (
        "Paths, serialized bytes and versioned records",
        """A filesystem path describes a location; a serialized record describes data. Joining records and batch.csv with filesystem::path uses platform-aware path composition. It does not open the file, create directories or validate the record bytes. A .csv suffix is a naming convention, not a parser implementation or a guarantee about quoting and delimiters.

The record format in this lesson is intentionally narrow: v1,id,cents with exactly three fields, decimal integer values and nonnegative domain constraints. The version tag is part of the data contract. A decoder should reject an unsupported version rather than guessing that a future format has the same meaning. A writer and reader can round-trip a value only when they agree on those details.

Shape validation checks delimiters and field count; value validation checks each field's full conversion and range. The reference contains both an introductory shape illustration and a strict decoder. A string such as v1,7,125x has the right number of fields but fails full numeric consumption. A negative amount can parse as an integer while failing the domain rule. Keep those reasons distinct when debugging.

Text serialization avoids some machine-layout hazards but still needs explicit rules for encoding, line endings, whitespace and maximum size. Writing the raw bytes of a C++ struct is not a portable substitute: padding, endianness, integer width and ABI layout can differ. Even on the same machine, uninitialized padding is not a stable public format.

Path safety is also separate from grammar. A correctly parsed record can be written to the wrong location if the working directory or user-controlled path is misunderstood. The examples only construct a relative path and inspect filename/parent components. Actual file creation belongs to an owned host directory with explicit failure handling. Later lessons restrict identifiers before mapping them into filenames.""",
        """If a round-trip passes only because both writer and reader share the same bug, add independent known-byte fixtures. If a suffix slips through, inspect conversion end pointers. If a file appears in an unexpected folder, record the process working directory and resolved input/output paths. If a version mismatch is silently accepted, restore an explicit version gate rather than treating every three-field string as v1.""",
    ),
    23: (
        "C-compatible boundaries and error translation",
        """A C-compatible function boundary is useful when code crosses a language or binary interface. extern "C" changes language linkage conventions for the named function; it does not automatically make every C++ parameter,exception or object layout safe for a C caller. The public signature should use a deliberately constrained representation and a documented ownership/error policy.

add_checked takes two integers and an output pointer,returning a status code. Status0 means the output was written successfully; status1 denotes a null output pointer; status2 denotes signed-int overflow. Both failure paths return before assigning the output, so its previous value is preserved. The interface uses this platform\'s int representation, not a fixed-width wire format. A caller must check status before consuming the output. Returning an integer sum alone would leave no distinct channel for a failure if every integer value could also be legitimate data.

A null check can reject a missing pointer,but it cannot prove that an arbitrary nonnull pointer points to writable live storage. The caller still has a precondition to supply a valid output object. After an object is destroyed,a dangling address may remain nonnull. C-style interfaces therefore need precise lifetime and buffer-size contracts in addition to defensive null checks.

Exceptions must not escape a boundary that promises not to throw. A wrapper around potentially throwing C++ work should catch exceptions and translate them into the declared status result while preserving cleanup through RAII. noexcept is a promise enforced by termination if an exception escapes,it is not a catch block. Marking a function noexcept without controlling its implementation can make failure less recoverable.

The single-file program proves the illustrated call and error conventions within one C++ executable. It does not prove dynamic loading,ABI compatibility across compilers or successful use by another language. The later opaque-handle and host-library exercises add those boundaries separately. Keep source linkage,linker success and real foreign-consumer acceptance as distinct evidence.""",
        """If the caller reads output after a nonzero status,it may be using an old value. If a null check passes but access crashes,inspect lifetime and buffer validity rather than assuming nonnull means safe. If an exception crosses a C boundary,add translation at the boundary and preserve a stable error contract. If a symbol cannot be found during linking,check language linkage and the actual exported name separately from runtime pointer behavior.""",
    ),
    24: (
        "Tests that distinguish plausible wrong programs",
        """A useful test is chosen to reject a plausible defect. One expected example can show a behavior,but it may also be satisfied by a shortcut that returns a constant. Boundary cases,negative cases and independent properties make the contract harder to fake accidentally. The reverse example starts with a concrete known result,then checks a relationship over changed inputs.

Reversing twice should recover the original sequence. This is a metamorphic property: it relates outputs of multiple executions without requiring a handwritten expected vector for every possible input. However,the identity function also satisfies reverse(reverse(x))==x. Therefore the property must be paired with an ordinary example whose expected order differs from its input. Properties complement examples;they do not automatically prove the intended algorithm.

Empty and single-element sequences are important because they expose invalid index calculations. For an unsigned size,computing size-1 on an empty vector wraps before a loop even begins. A standard algorithm can avoid that hand-written boundary hazard,but the input contract still needs tests. Repeated values check multiplicity preservation rather than only order.

A deterministic corpus is easier to reproduce than an unexplained random failure. If randomized generation is used,record the seed and the minimized failing input,but do not assume the seed alone remains sufficient after generator changes. A small exact counterexample usually teaches more than thousands of passing cases. Test reporting should retain the first meaningful mismatch rather than hide it in a large log.

Mutation testing asks whether the test suite rejects a deliberately wrong implementation,such as returning the input unchanged or dropping one repeated value. The exercise can perform that change in a scratch copy and compare which test catches it. Do not weaken the expectation to accept the mutated behavior. The purpose is to assess whether the tests cover the contract,not whether every edited program can be made green.""",
        """If a property passes for a wrong implementation,construct a concrete case that distinguishes the intended transformation from the shortcut. If only empty input crashes,inspect size arithmetic before indexing. If a randomized failure cannot be reproduced,preserve the exact input in addition to the seed. If all tests compare a function with itself through the same helper,add an independent oracle or manually derived expected value.""",
    ),
    25: (
        "Checked access and instrumented memory diagnostics",
        """Undefined behavior means the language does not provide a meaningful execution contract for that operation. An out-of-range vector subscript can appear to work,crash or produce unrelated effects. Observing one plausible value does not make it valid. A lesson should teach the invalid operation by explanation and isolated diagnostic tooling,not rely on its output as a deterministic result.

vector::at performs a checked access and throws out_of_range when the index is outside size. The first program accesses index1 of [2,4] and gets4. The second requests index2,catches the specific exception and asserts that the handler ran. This is defined behavior and a deterministic boundary test. It is different from using operator[] with index2 and hoping for a sanitizer report.

AddressSanitizer instruments compiled code to detect selected memory errors such as certain out-of-bounds accesses and use-after-free. UndefinedBehaviorSanitizer targets other categories. These tools do not prove the absence of every bug,and their availability and supported combinations depend on the toolchain. Compile and link the isolated diagnostic program with the matching flags so the runtime support is present.

A useful sanitizer report connects an invalid access to an allocation or lifetime event and a source stack. Read the first relevant error before interpreting later symptoms. Debug symbols and a reproducible small input make the report more useful. Fix the owner,bounds or lifetime rule that caused the access rather than merely increasing allocation size until the example stops crashing.

The normal safe reference does not intentionally invoke undefined behavior. The actual fault exercise is a separate host-tooling activity with its own process and expected nonzero diagnostic outcome. That boundary prevents the browser's successful safe example from being mislabeled as a sanitizer qualification. Compiler warnings,checked APIs and dynamic instrumentation are complementary evidence.""",
        """If at throws unexpectedly,compare the index with size,not capacity. If a sanitizer finds a use-after-free,trace the owner destruction and every retained borrow. If an instrumented link fails,check that sanitizer flags reached the link step too. If an uninstrumented invalid access seems fine,do not convert that observation into an expected output. Keep the reproducer isolated and repair the contract.""",
    ),
    26: (
        "Debugging a wrong value before timing it",
        """Debugging begins with a reproducible mismatch between expected and observed behavior. A debugger lets you stop at a relevant point,inspect variables and follow the call stack. It is most useful when guided by a hypothesis,such as the accumulator being reset or a caller passing the wrong range. Stepping through every line without a question can produce activity without narrowing the cause.

The total function provides a small deterministic target. For [2,4,6],the expected sum is12. A breakpoint before the return can inspect the input size and accumulated value. The call stack distinguishes a defect inside total from a caller supplying a different vector. Preserve the smallest failing fixture and the first point where actual state diverges from the predicted trace.

Timing asks a separate question. Repeating the computation1000 times yields a checksum of12000,which prevents the benchmark from being judged only by an elapsed number. A benchmark must still consider optimization,allocation,setup work,warm caches and whether the work resembles the real workload. The compiler may simplify work whose result is predictable,so an apparently tiny duration can reflect optimization rather than useful throughput.

Use a monotonic clock such as steady_clock for elapsed time. Wall-clock adjustments should not create negative benchmark durations. A single measurement is noisy because scheduling and other activity vary. Compare repeated samples and keep the correctness gate fixed. Never assert one exact nanosecond value as a portable expected result.

Debug builds improve some forms of observability,but their performance may differ substantially from optimized builds. A debug-time result should not be advertised as production speed. Record compiler,flags,architecture,input size and included setup costs. If an optimization changes the answer or skips a required validation step,the faster timing is not a valid improvement.""",
        """When the wrong output appears only in optimized builds,investigate undefined behavior,uninitialized state and configuration differences before blaming the optimizer. When timing varies wildly,inspect fixture size,setup costs and competing work. When a benchmark is nearly zero,check whether the compiler eliminated or precomputed it. Retain a deterministic checksum and a real workload justification before drawing performance conclusions.""",
    ),
    27: (
        "Dependency identity and reproducible local builds",
        """A dependency is part of the program's input,not merely a name in a build file. Reproducibility requires identifying the exact source or binary artifact,version,build options and relevant toolchain. A local vendored dependency can support offline builds when its complete reviewed inputs are present. A declaration that fetches a dependency at configure time still has a network requirement,even if the main source is local.

The tiny vendored namespace demonstrates a version constant and a behavior check. static_assert verifies the expected API version at compile time,and add(2,3)==5 checks a concrete operation. Those checks do not prove that an external package was downloaded,installed or independently built. They deliberately separate the idea of dependency identity from a host packaging workflow.

For a real local target,public include paths and required compile features belong to the target interface when consumers need them. Private implementation details should not leak into every consumer. A consumer that builds only because it happens to inherit a global include path is not a clean dependency contract. Test it from a fresh build directory with only the documented target relationship.

Offline qualification means attempting the build without fetching missing inputs. A populated developer cache can hide an undeclared dependency. Record which artifacts were already present and distinguish an offline rebuild from the initial connected preparation. Hashes can identify bytes,but they do not by themselves establish publisher trust or acceptable licensing.

Updating a dependency requires both compatibility and behavior review. An API-version constant may remain unchanged while behavior or ABI differs. Retain representative boundary tests and actual consumer acceptance for the supported platform. A successful single-file demonstration does not certify every architecture or toolchain mentioned in a README.""",
        """If a clean build fails while a long-lived build succeeds,inspect undeclared generated files,caches and global include paths. If configure unexpectedly contacts the network,look for fetch commands and missing vendored inputs. If a consumer links but behaves differently,check the actual artifact identity and ABI configuration. Do not repair an offline failure by silently installing or downloading a new dependency during the lesson.""",
    ),
    28: (
        "Designing and consuming a reusable parser library",
        """A reusable library separates its public contract from implementation and from the application's I/O policy. The record parser accepts one string_view and returns an owning Record or rejection. The caller decides where raw text came from and whether a rejected row aborts a batch. This separation lets the parser be tested without a terminal,file or cluster and keeps its lifetime reasoning small.

The public Record owns integer id and cents values. It does not retain a view into the input,so a successful result survives after the caller's raw string is destroyed. The parser still borrows the input while reading it. A library that returned views into a temporary normalization buffer would violate that lifetime contract even if its ordinary example happened to print correct values.

The grammar is exactly two comma-separated nonnegative integer fields. The parser checks delimiter count,both conversion results,full consumption and domain ranges. The suffix fixture7,125x rejects a plausible permissive parser that accepts a numeric prefix. Valid0,0 prevents the opposite bug of treating zero as absence. These cases are independent of packaging and should pass before the library is exported.

The real record-library fixture contains a public header,implementation,independent consumer and CMake target. Building the consumer against that target tests whether the header declares everything it needs and whether the implementation is actually linked. A combined single-file source cannot expose a missing exported include path or omitted library object in the same way.

Installation/export is another boundary. A local install tree should let a fresh consumer find the documented package/target without relying on the original source directory. The host exercise records configure,build,install and consumer results separately. The browser's one-main.cpp run is still useful for parser behavior,but it does not execute that packaging workflow.

A library release also needs a stability policy. Changing the accepted grammar,error representation or ownership behavior can break callers even when the function name stays the same. Document format/version changes and keep an independent consumer test. A package that compiles but silently accepts malformed suffixes is not a successful release under this contract.""",
        """If a consumer compiles only inside the library source tree,inspect public includes and exported target properties. If it links without the intended library,check whether a header accidentally contains a duplicate implementation. If parsing passes normal rows but accepts125x,inspect full consumption. If a returned record changes when raw input is edited,look for borrowed fields where the public contract promised owning values.""",
    ),
}
