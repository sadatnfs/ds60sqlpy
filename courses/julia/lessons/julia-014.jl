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

worked_a()

# Task 1: Summarize 1,missing,3 using observed values.
# Task 2: Fill the missing value with zero.
# Task 3: Include NaN among otherwise observed values.
# Task 4: Summarize two missing observations.
# Task 5: Compare something(nothing,7) with coalesce(nothing,7).
# Task 6: Choose deletion or imputation for a scientific dataset.

# Write your independent changes below.
