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

# === EXAMPLE A ===
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

# Task 1: Identify the head and first argument of parsed 1+2.
# Task 2: Explain what the counter would show if the macro evaluated its argument twice.
# Task 3: Explain why the caller result variable stays 99.
# Task 4: Compare strlen and length for the accented character.
# Task 5: Explain why the wrapper rejects a zero byte inside a string.
# Task 6: List the extra facts needed before calling a function that stores a pointer.

# Write your independent changes below.
