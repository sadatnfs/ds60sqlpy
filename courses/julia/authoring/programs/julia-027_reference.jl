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

# === EXAMPLE B ===
function worked_b()
    mktempdir() do root
        mkpath(joinpath(root, "src"))
        mkpath(joinpath(root, "test"))
        write(
            joinpath(root, "Project.toml"),
            "name = \"TinyScale\"\nuuid = \"7c087348-1b29-4e97-8d15-e711b29d8d5a\"\nversion = \"0.1.0\"\n",
        )
        write(
            joinpath(root, "src", "TinyScale.jl"),
            "module TinyScale\nexport twice\ntwice(x) = 2x\nend\n",
        )
        write(
            joinpath(root, "test", "runtests.jl"),
            "using Test\nBase.include(@__MODULE__, joinpath(@__DIR__, \"..\", \"src\", \"TinyScale.jl\"))\nusing .TinyScale\n@test twice(3) == 6\n@test twice(-2) == -4\ntrue\n",
        )
        target = Module(:OwnedFixture)
        result = Base.include(target, joinpath(root, "test", "runtests.jl"))
        @test result === true
        @test isfile(joinpath(root, "Project.toml"))
        println("Owned source and test files executed without package resolution")
    end
end

# === EXERCISES ===
function exercise_checks()
    @test LocalStats.center([2, 4]) == [-1, 1]
    @test LocalStats.center([5]) == [0]
    @test isdefined(LocalStats, :center)
    @test :center in names(LocalStats)
    @test joinpath("src", "TinyScale.jl") != "TinyScale.jl"
    @test_throws SystemError Base.include(
        Module(:MissingFixture),
        joinpath(tempdir(), "ds60-no-such-owned-source.jl"),
    )
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-027: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
