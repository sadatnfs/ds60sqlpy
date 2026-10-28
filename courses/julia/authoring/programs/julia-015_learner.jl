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

worked_a()

# Task 1: Scale the score column by 10 using ByRow.
# Task 2: Mutate input[!, :score].
# Task 3: Copy the column before later source mutation.
# Task 4: Summarize the group containing one missing score.
# Task 5: Apply observed_mean to only missing values.
# Task 6: Average the two group means with and without count weights.

# Write your independent changes below.
