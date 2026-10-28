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

function worked_b()
    valid = outcome([2, 4])
    invalid = outcome(Float64[])
    @test valid == (status = :ok, value = 3.0)
    @test invalid.status == :rejected
    @test occursin("observation", invalid.reason)
    @test_throws MethodError outcome(nothing)
    println("Rejected outcome: ", invalid)
end

worked_b()
