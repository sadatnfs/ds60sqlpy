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
