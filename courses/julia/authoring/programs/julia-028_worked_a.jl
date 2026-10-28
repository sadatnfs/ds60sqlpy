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

function worked_a()
    @test probabilities([1, 2, 1]) == [0.25, 0.5, 0.25]
    @test probabilities([1e308, 1e308]) == [0.5, 0.5]
    @test probabilities([0, 4]) == [0, 1]
    @test_throws ArgumentError probabilities([0, 0])
    @test_throws ArgumentError probabilities([1, -1])
    println("Known cases and overflow-resistant normalization passed")
end

worked_a()
