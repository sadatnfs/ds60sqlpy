using Test
using Statistics

function observed_summary(values)
    observed = collect(skipmissing(values))
    all(isfinite, observed) || throw(DomainError(observed, "Observed values must be finite"))
    estimate = isempty(observed) ? missing : mean(observed)
    return (total = length(values), observed = length(observed), estimate = estimate)
end

function worked_a()
    values = Union{Missing,Float64}[1, missing, 3]
    summary = observed_summary(values)
    @test summary == (total = 3, observed = 2, estimate = 2.0)
    replaced = coalesce.(values, 0.0)
    @test mean(replaced) ≈ 4/3
    @test ismissing(sum(values))
    println("Observed summary: ", summary, "; replaced mean: ", mean(replaced))
end

worked_a()
