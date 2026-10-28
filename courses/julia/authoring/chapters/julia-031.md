## Code can be represented as data

Julia represents many syntax forms as expressions. Quoting `:(1 + 2)` constructs a representation instead of immediately adding. `Meta.parse` converts a source string into syntax, but parsing alone does not validate its safety or intended meaning. Evaluating arbitrary parsed input can execute arbitrary program behavior. Configuration and learner records should remain data with a defined schema.

Macros transform syntax before the resulting code executes. Ordinary functions receive evaluated argument values. Prefer a function when values are sufficient; macros add complexity around name resolution, evaluation count and source locations. A macro is useful when it must introduce control structure or inspect the caller's expression.

## Hygiene and evaluation count

Suppose a macro should evaluate an expression, require a positive real result, and return it. Expanding the caller expression twice could duplicate a side effect or an expensive computation. The implementation stores it in a macro-local binding once. Julia's hygiene rules prevent that local name from accidentally overwriting a caller binding. `esc` allows the supplied expression to resolve names in the caller's environment.

This is not permission to escape every generated name indiscriminately. Generated implementation names and caller-supplied syntax have different ownership. A macro that unintentionally captures a caller variable can produce errors that look dependent on unrelated local naming.

### Worked case A: inspect and expand a bounded expression

The first program inspects a literal expression, then uses the macro with a counter side effect. The counter increases once. A caller variable named like the macro's internal temporary remains unchanged. A negative result is rejected, making the condition observable.

{{WORKED_A}}

The checks concern this reviewed macro's expansion. They do not make dynamic evaluation of arbitrary source safe. World-age rules also affect methods introduced through eval during running code; explicit modules and ordinary functions are usually easier to maintain.

## A foreign function needs an exact interface

`ccall` crosses Julia's boundary into a C ABI. You must declare the return type, argument types, symbol and lifetime assumptions accurately. A wrong declaration may corrupt memory or crash the process instead of producing a helpful Julia exception. C's `size_t` maps to `Csize_t`; a null-terminated character pointer maps to `Cstring` for this call.

The Linux runtime already provides the C library function `strlen`. It counts bytes before the first zero byte. It does not count Unicode code points or grapheme clusters. The wrapper rejects embedded zero characters so that its result corresponds to the complete UTF 8 string rather than an unexpected prefix.

### Worked case B: count bytes through the actual C library

The second program calls the real Linux symbol, compares its result with Julia's byte count, and contrasts that with character count for an accented character. It performs genuine foreign-function execution without compiling or downloading an extension.

{{WORKED_B}}

## Lifetimes and transfer

Passing a Julia String as `Cstring` through this direct call lets the conversion machinery preserve the argument for the call duration. If a foreign API stores a pointer after returning, this simple lifetime is insufficient. Manually derived pointers require a careful rooting strategy, often including `GC.@preserve` around the region that uses them. The C library's ownership and free policy must be documented separately.

C++ APIs add name mangling, object layout and exception conventions; a reviewed C wrapper is often the clearer boundary. Python interoperability likewise needs a prepared bridge and compatible environments, which this runtime does not install during lessons. Connect to the existing [C](../../../c/README.md) and [C++](../../../cpp/README.md) paths for memory and ABI fundamentals. Successful `strlen` execution qualifies this narrow interface, not arbitrary native libraries or unsafe pointers.
