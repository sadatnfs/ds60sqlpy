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

# === EXAMPLE B ===
function worked_b()
    distribution = Binomial(10, 0.2)
    @test mean(distribution) == 2
    @test var(distribution) ≈ 1.6
    @test pdf(distribution, 0) ≈ 0.8^10
    sample = rand(MersenneTwister(7), distribution, 2000)
    values = collect(0:10)
    exact = pdf.(distribution, values)
    empirical = [count(==(value), sample) / length(sample) for value in values]
    @test sum(empirical) ≈ 1
    z = 10.0
    density = exp(-z^2 / 2) / sqrt(2pi)
    tail = ccdf(Normal(), z)
    @test density * z / (1 + z^2) < tail < density / z
    @test isfinite(logccdf(Normal(), z))
    rows = [[values[i], exact[i], empirical[i]] for i in eachindex(values)]
    data = [
        Dict("type" => "bar", "x" => values, "y" => exact, "name" => "Exact mass"),
        Dict(
            "type" => "scatter",
            "x" => values,
            "y" => empirical,
            "mode" => "markers",
            "name" => "Empirical frequency",
        ),
    ]
    layout = Dict(
        "title" => "Authored Binomial model and 2000 draws",
        "meta" => Dict(
            "description" => "A fixed-seed sample fluctuates around the declared Binomial(10, 0.2) probability mass. These are synthetic draws, not observed population data.",
            "table" => Dict(
                "columns" => ["Value", "Exact mass", "Empirical frequency"],
                "rows" => rows,
            ),
        ),
    )
    show_plotly(
        data;
        layout = layout,
        description = "Binomial simulation and analytic probabilities",
    )
    println("Stable normal-tail probability: ", tail)
end

# === EXERCISES ===
function exercise_checks()
    @test cdf(Normal(), 0) == 0.5
    @test quantile(Normal(), 0.5) == 0
    @test logpdf(Normal(), 0) ≈ -log(2pi)/2
    @test_throws DomainError Normal(0, -1)
    generator = MersenneTwister(3)
    before = rand(generator, 3)
    after = rand(generator, 3)
    @test before != after
    @test rand(MersenneTwister(3), 3) == before
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-020: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
