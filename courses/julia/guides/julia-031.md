# julia-031: Expressions, hygienic macros and C interoperability

## Starting point and outcome

Advanced; approximately 150 minutes. Direct prerequisites: `julia-003`, `julia-010`, `julia-027`.

Inspect syntax without evaluating untrusted text, implement a hygienic single-evaluation macro and call a precisely typed Linux C function.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Code can be represented as data

Julia represents many syntax forms as expressions. Quoting `:(1 + 2)` constructs a representation instead of immediately adding. `Meta.parse` converts a source string into syntax, but parsing alone does not validate its safety or intended meaning. Evaluating arbitrary parsed input can execute arbitrary program behavior. Configuration and learner records should remain data with a defined schema.

Macros transform syntax before the resulting code executes. Ordinary functions receive evaluated argument values. Prefer a function when values are sufficient; macros add complexity around name resolution, evaluation count and source locations. A macro is useful when it must introduce control structure or inspect the caller's expression.

## Hygiene and evaluation count

Suppose a macro should evaluate an expression, require a positive real result, and return it. Expanding the caller expression twice could duplicate a side effect or an expensive computation. The implementation stores it in a macro-local binding once. Julia's hygiene rules prevent that local name from accidentally overwriting a caller binding. `esc` allows the supplied expression to resolve names in the caller's environment.

This is not permission to escape every generated name indiscriminately. Generated implementation names and caller-supplied syntax have different ownership. A macro that unintentionally captures a caller variable can produce errors that look dependent on unrelated local naming.

### Worked case A: inspect and expand a bounded expression

The first program inspects a literal expression, then uses the macro with a counter side effect. The counter increases once. A caller variable named like the macro's internal temporary remains unchanged. A negative result is rejected, making the condition observable.

```julia
using Test

macro positive(expression)
    return quote
        local result = $(esc(expression))
        result isa Real && result > 0 || throw(ArgumentError("Expected a positive real value"))
        result
    end
end

function c_bytes(value::String)
    occursin('\0', value) && throw(ArgumentError("Embedded zero bytes are not supported"))
    return ccall(:strlen, Csize_t, (Cstring,), value)
end

function worked_a()
    syntax = Meta.parse("1 + 2")
    @test syntax isa Expr
    @test syntax.head == :call
    @test syntax.args[1] == :+
    counter = Ref(0)
    result = 99
    value = @positive begin
        counter[] += 1
        3
    end
    @test value == 3
    @test counter[] == 1
    @test result == 99
    @test_throws ArgumentError (@positive -2)
    println("Syntax inspected; macro evaluates the caller expression once")
end

worked_a()
```

The checks concern this reviewed macro's expansion. They do not make dynamic evaluation of arbitrary source safe. World-age rules also affect methods introduced through eval during running code; explicit modules and ordinary functions are usually easier to maintain.

## A foreign function needs an exact interface

`ccall` crosses Julia's boundary into a C ABI. You must declare the return type, argument types, symbol and lifetime assumptions accurately. A wrong declaration may corrupt memory or crash the process instead of producing a helpful Julia exception. C's `size_t` maps to `Csize_t`; a null-terminated character pointer maps to `Cstring` for this call.

The Linux runtime already provides the C library function `strlen`. It counts bytes before the first zero byte. It does not count Unicode code points or grapheme clusters. The wrapper rejects embedded zero characters so that its result corresponds to the complete UTF 8 string rather than an unexpected prefix.

### Worked case B: count bytes through the actual C library

The second program calls the real Linux symbol, compares its result with Julia's byte count, and contrasts that with character count for an accented character. It performs genuine foreign-function execution without compiling or downloading an extension.

```julia
using Test

macro positive(expression)
    return quote
        local result = $(esc(expression))
        result isa Real && result > 0 || throw(ArgumentError("Expected a positive real value"))
        result
    end
end

function c_bytes(value::String)
    occursin('\0', value) && throw(ArgumentError("Embedded zero bytes are not supported"))
    return ccall(:strlen, Csize_t, (Cstring,), value)
end

function worked_b()
    value = "é"
    @test length(value) == 1
    @test ncodeunits(value) == 2
    @test c_bytes(value) == 2
    @test c_bytes("classroom") == 9
    @test c_bytes("") == 0
    @test_throws ArgumentError c_bytes("a\0b")
    println("Actual C strlen bytes: ", c_bytes(value), "; Julia characters: ", length(value))
end

worked_b()
```

## Lifetimes and transfer

Passing a Julia String as `Cstring` through this direct call lets the conversion machinery preserve the argument for the call duration. If a foreign API stores a pointer after returning, this simple lifetime is insufficient. Manually derived pointers require a careful rooting strategy, often including `GC.@preserve` around the region that uses them. The C library's ownership and free policy must be documented separately.

C++ APIs add name mangling, object layout and exception conventions; a reviewed C wrapper is often the clearer boundary. Python interoperability likewise needs a prepared bridge and compatible environments, which this runtime does not install during lessons. Connect to the existing [C](../../c/README.md) and [C++](../../cpp/README.md) paths for memory and ABI fundamentals. Successful `strlen` execution qualifies this narrow interface, not arbitrary native libraries or unsafe pointers.


## Six investigations

### 1. Inspect syntax

Identify the head and first argument of parsed 1+2.

**Expected:** The head is:call and the function symbol is:+.

**Hint:** Parsing constructs syntax.

### 2. Detect duplicate evaluation

Explain what the counter would show if the macro evaluated its argument twice.

**Expected:** The counter would be 2.

**Hint:** Store the caller expression once.

### 3. Check name ownership

Explain why the caller result variable stays 99.

**Expected:** The macro-local binding is hygienic.

**Hint:** Only the caller expression is escaped.

### 4. Trace UTF 8 bytes

Compare strlen and length for the accented character.

**Expected:** The byte count is 2 and character count is 1.

**Hint:** The C API operates on bytes.

### 5. Reject embedded zeros

Explain why the wrapper rejects a zero byte inside a string.

**Expected:** C strlen would stop at the first zero.

**Hint:** The complete-string contract would be violated.

### 6. Review a native API

List the extra facts needed before calling a function that stores a pointer.

**Expected:** ABI, lifetime, ownership, thread safety and release rules.

**Hint:** The argument must outlive the native use.

## Primary references

- [Julia metaprogramming](https://docs.julialang.org/en/v1/manual/metaprogramming/)
- [Calling C and Fortran](https://docs.julialang.org/en/v1/manual/calling-c-and-fortran-code/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
