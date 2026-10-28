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

function worked_a()
    @test finite_mean([1, 2, 3]) == 2
    @test finite_mean([-1, 1]) == 0
    @test_throws ArgumentError finite_mean(Float64[])
    @test_throws DomainError finite_mean([1.0, Inf])
    println("Finite mean: ", finite_mean([1, 2, 3]))
end

worked_a()
