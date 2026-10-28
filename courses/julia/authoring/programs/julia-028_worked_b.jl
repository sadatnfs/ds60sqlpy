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

function worked_b()
    generator = MersenneTwister(140)
    for count = 1:20
        values = rand(generator, count) .+ 0.01
        result = probabilities(values)
        @test length(result) == count
        @test all(>=(0), result)
        @test sum(result) ≈ 1
        @test probabilities(7 .* values) ≈ result
        permutation = randperm(generator, count)
        @test probabilities(values[permutation]) ≈ result[permutation]
    end
    println("Twenty bounded generated cases satisfy scaling and permutation properties")
end

worked_b()
