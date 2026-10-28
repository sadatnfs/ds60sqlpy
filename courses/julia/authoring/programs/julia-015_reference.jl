using Test
using Statistics
using DataFrames

function observed_mean(values)
    observed = collect(skipmissing(values))
    all(isfinite, observed) || throw(DomainError(observed, "Finite scores required"))
    return isempty(observed) ? missing : mean(observed)
end

# === EXAMPLE A ===
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

# === EXAMPLE B ===
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

# === EXERCISES ===
function exercise_checks()
    @test ismissing(observed_mean([missing]))
    input = DataFrame(id = [1, 2], x = [2, 4])
    changed = transform(input, :x => ByRow(x -> x^2) => :square)
    @test changed.square == [4, 16]
    @test names(input) == ["id", "x"]
    @test nrow(input) == 2
    @test ncol(changed) == 3
    @test select(input, :id; copycols = true).id !== input.id
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-015: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
