using Test
using Statistics

function finite_mean(values)
    isempty(values) && throw(ArgumentError("At least one observation is required"))
    all(isfinite, values) || throw(DomainError(values, "Observations must be finite"))
    return mean(values)
end

function outcome(values)
    try
        return (status = :ok, value = finite_mean(values))
    catch error
        if error isa ArgumentError || error isa DomainError
            return (status = :rejected, reason = sprint(showerror, error))
        end
        rethrow()
    end
end

# === EXAMPLE A ===
function worked_a()
    @test finite_mean([1, 2, 3]) == 2
    @test finite_mean([-1, 1]) == 0
    @test_throws ArgumentError finite_mean(Float64[])
    @test_throws DomainError finite_mean([1.0, Inf])
    println("Finite mean: ", finite_mean([1, 2, 3]))
end

# === EXAMPLE B ===
function worked_b()
    valid = outcome([2, 4])
    invalid = outcome(Float64[])
    @test valid == (status = :ok, value = 3.0)
    @test invalid.status == :rejected
    @test occursin("observation", invalid.reason)
    @test_throws MethodError outcome(nothing)
    println("Rejected outcome: ", invalid)
end

# === EXERCISES ===
function exercise_checks()
    @test finite_mean([7]) == 7
    @test_throws DomainError finite_mean([NaN])
    @test outcome([0]).value == 0
    @test outcome([Inf]).status == :rejected
    @test_throws MethodError finite_mean(["not numeric"])
    @test isfinite(finite_mean([0.1, 0.2]))
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-009: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
