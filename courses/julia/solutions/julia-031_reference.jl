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

# === EXAMPLE B ===
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

# === EXERCISES ===
function exercise_checks()
    @test (@positive 0.5) == 0.5
    @test_throws ArgumentError (@positive 0)
    @test_throws ArgumentError (@positive NaN)
    @test c_bytes("abc") == 3
    @test c_bytes("λ") == ncodeunits("λ")
    @test Meta.parse("x * 2").head == :call
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-031: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
