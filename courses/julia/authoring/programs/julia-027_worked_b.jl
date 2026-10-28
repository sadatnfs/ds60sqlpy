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

worked_b()
