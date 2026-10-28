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

worked_a()

# Task 1: Calculate the mean of -1 and 1.
# Task 2: Call the helper on an empty vector.
# Task 3: Include NaN or Inf in the input.
# Task 4: Pass a value for which the required methods do not exist.
# Task 5: Validate a result using a hand calculation and a limiting case.
# Task 6: Aggregate valid outcomes from a mixed input stream.

# Write your independent changes below.
