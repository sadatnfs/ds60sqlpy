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

# === EXAMPLE A ===
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

# === EXAMPLE B ===
function worked_b()
    values = fill(2.0, 1000)
    observations = [measured(values) for _ = 1:5]
    @test all(row -> row.value == 4000, observations)
    @test all(row -> row.seconds >= 0 && row.bytes >= 0, observations)
    println("Warmed observations: ", observations)
end

# === EXERCISES ===
function exercise_checks()
    @test (@inferred sum_squares(Float32[1, 2])) === Float32(5)
    @test sum_squares([-3.0, 4.0]) == 25
    @test sum_squares([NaN]) |> isnan
    @test sum_squares([Inf]) == Inf
    @test measured([2.0]).value == 4
    @test_throws MethodError sum_squares([1, 2])
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-025: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
