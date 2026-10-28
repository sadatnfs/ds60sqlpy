using Test
using Random
using Statistics
using Distributions
using .DS60Plots

# === EXAMPLE A ===
function worked_a()
    distribution = Normal(2, 3)
    first = rand(MersenneTwister(42), distribution, 4000)
    second = rand(MersenneTwister(42), distribution, 4000)
    standard_error = 3 / sqrt(length(first))
    @test first == second
    @test mean(distribution) == 2
    @test var(distribution) == 9
    @test abs(mean(first) - 2) < 8standard_error
    println("Monte Carlo mean: ", mean(first), "; standard-error scale: ", standard_error)
end

worked_a()

# Task 1: Construct Normal(2,3).
# Task 2: Create two generators with the same seed and sample the same distribution.
# Task 3: Draw twice from one generator object.
# Task 4: Increase the draw count by a factor of 4 under independent sampling.
# Task 5: Compare a survival-function calculation with naive subtraction.
# Task 6: Compare empirical frequencies with the exact Binomial masses.

# Write your independent changes below.
