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

# === EXAMPLE B ===
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

# === EXERCISES ===
function exercise_checks()
    @test_throws ArgumentError probabilities(Float64[])
    @test_throws ArgumentError probabilities([Inf, 1])
    @test_throws ArgumentError probabilities([NaN])
    @test probabilities([3]) == [1]
    values = [2.0, 5.0, 3.0]
    before = copy(values)
    @test probabilities(values) ≈ [0.2, 0.5, 0.3]
    @test values == before
    @test probabilities(values)[2] / probabilities(values)[1] ≈ 2.5
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-028: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
