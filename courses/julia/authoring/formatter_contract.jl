# Regression checks for syntax identity; no learner expression is evaluated.
using Test

module FormatterContract
const TOOL = joinpath(@__DIR__, "..", "..", "..", "scripts", "julia_source_tools.jl")
const DEFINITIONS = first(split(read(TOOL, String), "function main()"; limit = 2))
Base.include_string(@__MODULE__, DEFINITIONS, TOOL)
end

@testset "Parser metadata versus semantic changes" begin
    parse = FormatterContract.parse_source
    @test isequal(parse("x = 1\n@test x == 1"), parse("\n\nx = 1\n\n@test x == 1"))
    @test !isequal(parse("x = 1"), parse("x = 2"))
    @test !isequal(parse("x + y"), parse("x - y"))
    @test !isequal(parse("label = \"one\""), parse("label = \"two\""))
    @test !isequal(parse("@test x == 1"), parse("@test x == 2"))
    @test !isequal(parse(":(x + 1)"), parse(":(x + 2)"))
    @test !isequal(parse("label = \"a b\""), parse("label = \"a  b\""))
    @test_throws ErrorException parse("function missing_end()")
    source = read(joinpath(@__DIR__, "programs", "julia-011_learner.jl"), String)
    formatted =
        FormatterContract.format_text(source; margin = 100, indent = 4, format_docstrings = false)
    @test isequal(parse(source), parse(formatted))
end
println("Julia formatter semantic contracts passed")
