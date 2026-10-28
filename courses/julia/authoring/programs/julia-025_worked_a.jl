using Test
using InteractiveUtils

function sum_squares(values::AbstractVector{T}) where {T<:AbstractFloat}
    total = zero(T)
    for value in values
        total += value * value
    end
    return total
end

function measured(values)
    sum_squares(values)
    result = @timed sum_squares(values)
    return (value = result.value, seconds = result.time, bytes = result.bytes)
end

function worked_a()
    values = Float64.(1:5)
    @test (@inferred sum_squares(values)) == 55
    @test sum_squares(Float64[]) == 0
    report = IOBuffer()
    code_warntype(report, sum_squares, (Vector{Float64},); color = false)
    text = String(take!(report))
    @test !isempty(text)
    println("Inferred kernel result: ", sum_squares(values))
    println("Inference diagnostic captured: ", ncodeunits(text), " bytes")
end

worked_a()
