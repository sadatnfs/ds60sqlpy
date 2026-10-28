using Test
using Random

function probabilities(weights)
    isempty(weights) && throw(ArgumentError("Weights cannot be empty"))
    stored = Float64.(weights)
    all(value -> isfinite(value) && value >= 0, stored) ||
        throw(ArgumentError("Finite nonnegative weights required"))
    largest = maximum(stored)
    largest > 0 || throw(ArgumentError("At least one positive weight required"))
    scaled = stored ./ largest
    return scaled ./ sum(scaled)
end

# === EXAMPLE A ===
function worked_a()
    @test probabilities([1, 2, 1]) == [0.25, 0.5, 0.25]
    @test probabilities([1e308, 1e308]) == [0.5, 0.5]
    @test probabilities([0, 4]) == [0, 1]
    @test_throws ArgumentError probabilities([0, 0])
    @test_throws ArgumentError probabilities([1, -1])
    println("Known cases and overflow-resistant normalization passed")
end

worked_a()

# Task 1: Compute probabilities for[2,5,3] by hand.
# Task 2: Explain why direct sum([1e308,1e308]) is dangerous.
# Task 3: Swap the first and last weights and predict the output.
# Task 4: Explain why sum-to-one alone cannot verify weighting.
# Task 5: Specify how negative, all-zero and nonfinite inputs should behave.
# Task 6: Propose properties for predictions from a fitted exact line.

# Write your independent changes below.
