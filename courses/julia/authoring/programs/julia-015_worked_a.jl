using Test
using Statistics
using DataFrames

function observed_mean(values)
    observed = collect(skipmissing(values))
    all(isfinite, observed) || throw(DomainError(observed, "Finite scores required"))
    return isempty(observed) ? missing : mean(observed)
end

function worked_a()
    input = DataFrame(id = [1, 2, 3], score = [10, 20, 30])
    selected = select(input, :id, :score => ByRow(x -> x / 10) => :scaled; copycols = true)
    @test names(selected) == ["id", "scaled"]
    @test selected.scaled == [1, 2, 3]
    alias = input[!, :score]
    snapshot = input[:, :score]
    alias[1] = 99
    @test input.score[1] == 99
    @test snapshot[1] == 10
    println("Selected table: ", selected)
end

worked_a()
