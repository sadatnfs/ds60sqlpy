using Test
using Statistics
using DataFrames

function observed_mean(values)
    observed = collect(skipmissing(values))
    all(isfinite, observed) || throw(DomainError(observed, "Finite scores required"))
    return isempty(observed) ? missing : mean(observed)
end

function worked_b()
    input = DataFrame(group = ["a", "a", "b", "b"], score = [1, missing, 3, 5])
    summary = combine(
        groupby(input, :group; sort = true),
        nrow => :n_rows,
        :score => (x -> count(v -> !ismissing(v), x)) => :n_observed,
        :score => observed_mean => :mean_score,
    )
    @test summary.group == ["a", "b"]
    @test summary.n_rows == [2, 2]
    @test summary.n_observed == [1, 2]
    @test summary.mean_score == [1.0, 4.0]
    println("Grouped summary: ", summary)
end

worked_b()
