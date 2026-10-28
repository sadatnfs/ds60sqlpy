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

function worked_b()
    values = fill(2.0, 1000)
    observations = [measured(values) for _ = 1:5]
    @test all(row -> row.value == 4000, observations)
    @test all(row -> row.seconds >= 0 && row.bytes >= 0, observations)
    println("Warmed observations: ", observations)
end

worked_b()
