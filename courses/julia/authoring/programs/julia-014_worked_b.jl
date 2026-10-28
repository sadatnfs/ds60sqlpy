using Test
using Statistics

function observed_summary(values)
    observed = collect(skipmissing(values))
    all(isfinite, observed) || throw(DomainError(observed, "Observed values must be finite"))
    estimate = isempty(observed) ? missing : mean(observed)
    return (total = length(values), observed = length(observed), estimate = estimate)
end

function worked_b()
    @test_throws DomainError observed_summary([1.0, NaN, missing])
    empty_observed = observed_summary([missing, missing])
    @test empty_observed.observed == 0
    @test ismissing(empty_observed.estimate)
    @test something(nothing, 7) == 7
    @test coalesce(nothing, 7) === nothing
    @test (missing & false) === false
    println("No observed values: ", empty_observed)
end

worked_b()
