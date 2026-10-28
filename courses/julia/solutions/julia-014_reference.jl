using Test
using Statistics

function observed_summary(values)
    observed = collect(skipmissing(values))
    all(isfinite, observed) || throw(DomainError(observed, "Observed values must be finite"))
    estimate = isempty(observed) ? missing : mean(observed)
    return (total = length(values), observed = length(observed), estimate = estimate)
end

# === EXAMPLE A ===
function worked_a()
    values = Union{Missing,Float64}[1, missing, 3]
    summary = observed_summary(values)
    @test summary == (total = 3, observed = 2, estimate = 2.0)
    replaced = coalesce.(values, 0.0)
    @test mean(replaced) ≈ 4/3
    @test ismissing(sum(values))
    println("Observed summary: ", summary, "; replaced mean: ", mean(replaced))
end

# === EXAMPLE B ===
function worked_b()
    @test_throws DomainError observed_summary([1.0, NaN, missing])
    empty_observed = observed_summary([missing, missing])
    @test empty_observed.observed == 0
    @test ismissing(empty_observed.estimate)
    @test something(nothing, 7) == 7
    @test coalesce(nothing, 7) === nothing
    @test (missing & false) === false
    println("No observed values: ", empty_observed)
end

# === EXERCISES ===
function exercise_checks()
    @test coalesce(missing, 4) == 4
    @test ismissing(missing + 1)
    @test ismissing(something(missing, 4))
    @test observed_summary([2, 4]).estimate == 3
    @test observed_summary(Float64[]).total == 0
    @test_throws DomainError observed_summary([Inf])
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-014: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
