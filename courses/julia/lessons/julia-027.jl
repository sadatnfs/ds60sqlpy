using Test
using Statistics

module LocalStats
using Statistics
export center
function center(values)
    isempty(values) && throw(ArgumentError("At least one value is required"))
    return values .- mean(values)
end
end

# === EXAMPLE A ===
function worked_a()
    original = [1.0, 2.0, 3.0]
    centered = LocalStats.center(original)
    @test centered == [-1, 0, 1]
    @test original == [1, 2, 3]
    @test sum(centered) == 0
    @test_throws ArgumentError LocalStats.center(Float64[])
    println("Qualified module result: ", centered)
end

worked_a()

# Task 1: Call LocalStats.center on[2,4].
# Task 2: Explain whether export makes other names private.
# Task 3: Identify which file declares identity and which defines twice.
# Task 4: Explain why @__DIR__ is used in the test entrypoint.
# Task 5: List what Project and Manifest do and do not establish.
# Task 6: Separate a CSV workflow into numerical core, IO and tests.

# Write your independent changes below.
