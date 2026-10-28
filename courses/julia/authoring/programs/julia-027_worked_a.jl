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
