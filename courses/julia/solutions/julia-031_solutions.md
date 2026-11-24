# julia-031: explained reference

The executable reference is `julia-031_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Parse text into `Expr` objects only to inspect them, never to run untrusted input. `@positive` stores the escaped caller expression once in a `local` variable, checks it is a positive real and returns it. `c_bytes` rejects embedded zero bytes, then calls C `strlen` through `ccall` with an exact `Csize_t` return and `Cstring` argument.

## 1. Inspect syntax

The representation describes a call; this inspection does not evaluate arbitrary input.

**Expected observation:** The head is `:call` and the function symbol is `:+`.

**Why it holds here:** `Meta.parse("1 + 2")` produces an `Expr` with head `:call` whose first argument is the function symbol `:+`.

**Plausible wrong approach:** Calling `eval` on the parsed expression to look at it runs the code, which is unsafe for text from outside.

**How to verify:** Example A asserts `syntax.head == :call` and `syntax.args[1] == :+`; the reference checks `Meta.parse("x * 2").head == :call`.

## 2. Detect duplicate evaluation

The test protects against duplicated side effects in generated syntax.

**Expected observation:** The counter would be 2.

**Why it holds here:** The macro inserts the caller expression once, so the block that increments `counter[]` runs once and the counter ends at 1.

**Plausible wrong approach:** Writing the check as `$(esc(expression)) > 0 || ...; $(esc(expression))` evaluates the argument twice and leaves the counter at 2.

**How to verify:** Example A asserts `counter[] == 1` after `@positive` returns 3.

## 3. Check name ownership

Generated temporary names must not capture unrelated caller bindings.

**Expected observation:** The macro-local binding is hygienic.

**Why it holds here:** The macro's `local result` is renamed by hygiene, so the caller's own `result = 99` is not overwritten.

**Plausible wrong approach:** Escaping the whole quoted block would make the macro's temporary name capture the caller's `result`.

**How to verify:** Example A asserts `result == 99` after the macro call.

## 4. Trace UTF 8 bytes

Unicode text has multiple valid units; choose the unit required by the interface.

**Expected observation:** The byte count is 2 and character count is 1.

**Why it holds here:** The letter é is stored as two UTF-8 bytes, so C `strlen` returns 2 while Julia's `length` counts 1 character.

**Plausible wrong approach:** Passing `length(s)` to a C function that expects a byte count truncates multibyte strings.

**How to verify:** Example B asserts `c_bytes("é") == 2` and `length("é") == 1`; the reference checks `c_bytes("λ") == ncodeunits("λ")`.

## 5. Reject embedded zeros

Explicit validation prevents a truncated prefix from being mistaken for the full length.

**Expected observation:** C strlen would stop at the first zero.

**Why it holds here:** C `strlen` stops at the first zero byte, so for `"a\0b"` it would report 1 instead of the full Julia length.

**Plausible wrong approach:** Skipping the check returns a short but plausible number, which looks like a valid length.

**How to verify:** Example B asserts `@test_throws ArgumentError c_bytes("a\0b")`.

## 6. Review a native API

A successful synchronous call does not establish a safe retained-pointer integration.

**Expected observation:** ABI, lifetime, ownership, thread safety and release rules.

**Why it holds here:** A native function that keeps a pointer after returning needs the Julia string to stay alive and unmoved for as long as C uses it.

**Plausible wrong approach:** Assuming that a successful immediate call proves safety ignores that garbage collection may free the string later.

**How to verify:** Read the library's ownership and threading documentation and add a test that holds a reference with `GC.@preserve` for the native lifetime.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-031: all reference checks passed`:

The macro passes 0.5 through unchanged and rejects 0 and NaN, because NaN is a real but not greater than zero. The string checks use ASCII `"abc"`, where bytes equal characters, and λ, where `strlen` must agree with `ncodeunits`. `Meta.parse("x * 2")` is another call expression, inspected but not evaluated.

```julia
function exercise_checks()
    @test (@positive 0.5) == 0.5
    @test_throws ArgumentError (@positive 0)
    @test_throws ArgumentError (@positive NaN)
    @test c_bytes("abc") == 3
    @test c_bytes("λ") == ncodeunits("λ")
    @test Meta.parse("x * 2").head == :call
end
```
