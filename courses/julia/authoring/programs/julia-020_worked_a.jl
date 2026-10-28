using Test
using Random
using Statistics
using Distributions
using .DS60Plots

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
