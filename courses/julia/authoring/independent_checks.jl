using Test
using Dates
using LinearAlgebra
using Statistics
using ForwardDiff
using JSON3
using SHA
BLAS.set_num_threads(1)

module Unit005
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-005_reference.jl"))
end

module Unit006
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-006_reference.jl"))
end

module Unit009
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-009_reference.jl"))
end

module Unit010
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-010_reference.jl"))
end

module Unit011
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-011_reference.jl"))
end

module Unit012
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-012_reference.jl"))
end

module Unit014
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-014_reference.jl"))
end

module Unit015
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-015_reference.jl"))
end

module Unit018
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-018_reference.jl"))
end

module Unit021
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-021_reference.jl"))
end

module Unit022
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-022_reference.jl"))
end

module Unit023
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-023_reference.jl"))
end

module Unit024
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-024_reference.jl"))
end

module Unit026
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-026_reference.jl"))
end

module Unit028
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-028_reference.jl"))
end

module Unit029
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-029_reference.jl"))
end

module Unit030
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-030_reference.jl"))
end

module Unit031
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-031_reference.jl"))
end

module Unit032
const DS60Plots = Main.DS60Plots
include(joinpath(@__DIR__, "..", "solutions", "julia-032_reference.jl"))
end

@testset "Independent values and ownership" begin
    @test Unit005.sum_range(-4:9) == 35
    input = [7, 8]
    replaced = Unit006.rebind(input)
    @test input == [7, 8]
    @test replaced !== input
    @test Unit006.make_scaler(-3)(7) == -21
    @test Unit012.typed_total([1//2, 2//3]) == 7//6
    @test Unit012.typed_total(Float32[2, 7]) === Float32(9)
    @test_throws MethodError Unit012.accepts_reals(["not numeric"])
    @test Unit009.finite_mean([2, 7, 12, 19]) == 10
    @test_throws ArgumentError Unit009.finite_mean(Float64[])
    @test_throws DomainError Unit009.finite_mean([NaN])
    @test_throws ArgumentError Unit010.Measurement(big"1e10000", :m)
    @test_throws ArgumentError Unit011.Circle(big"1e10000")
    @test Unit011.area(Unit011.Rectangle(7, 9)) == 63
    @test Unit011.total_area([Unit011.Circle(2), Unit011.Rectangle(7, 9)]) ≈ 4pi + 63
    @test Unit014.observed_summary([missing, -4.0, 10.0, missing]).estimate == 3
    @test Unit014.observed_summary([missing, -4.0, 10.0, missing]).observed == 2
    @test ismissing(Unit014.observed_summary([missing]).estimate)
    @test_throws DomainError Unit015.observed_mean([Inf, missing])
    @test Unit015.observed_mean([missing, 2, 9, 4]) == 5
end

@testset "Availability and calendar rules" begin
    ledger = [
        (
            entity = "a",
            event = DateTime(2024, 1, 1),
            available = DateTime(2024, 1, 3),
            version = 1,
            value = 4,
        ),
        (
            entity = "a",
            event = DateTime(2024, 1, 1),
            available = DateTime(2024, 1, 5),
            version = 2,
            value = 9,
        ),
        (
            entity = "b",
            event = DateTime(2024, 1, 2),
            available = DateTime(2024, 1, 2),
            version = 1,
            value = 100,
        ),
    ]
    @test ismissing(Unit018.historical_value(ledger, "a", DateTime(2024, 1, 2)))
    @test Unit018.historical_value(reverse(ledger), "a", DateTime(2024, 1, 4)) == 4
    @test Unit018.historical_value(ledger, "a", DateTime(2024, 1, 5)) == 9
    february = Date(2024, 1, 31) + Month(1)
    @test february + Month(1) == Date(2024, 3, 29)
    @test Date(2024, 1, 31) + Month(1) + Month(1) == Date(2024, 3, 31)
end

@testset "Independent ridge and derivative oracles" begin
    x = [-2.0, -1, 0, 1, 2]
    y = [-3.0, -1, 1, 3, 5]
    @test Unit021.fit_ridge(x, y, 0) ≈ [1, 2]
    @test Unit021.fit_ridge(x, y, 10) ≈ [1, 1]
    @test Unit021.fit_ridge(x .+ 10, y, 10) ≈ [-9, 1]
    @test Unit021.fit_ridge(reverse(x), reverse(y), 10) ≈ [1, 1]
    @test_throws ArgumentError Unit021.fit_ridge(x, y, NaN)
    @test_throws ArgumentError Unit021.fit_ridge(ones(5), y, 0)
    @test ForwardDiff.gradient(Unit022.quadratic, [3.0, -2.0]) == [6, -12]
    @test ForwardDiff.jacobian(Unit022.vector_function, [3.0, -2.0]) == [6 1; -2 3]
    @test ForwardDiff.gradient(Unit022.generic_storage, [3.0, -2.0]) == [6, -4]
    storage = zeros(2)
    Unit023.objective_gradient!(storage, [0.0, 0.0])
    @test storage == [-2, 16]
    optimum = Unit023.Optim.optimize(
        Unit023.objective,
        Unit023.objective_gradient!,
        [-8.0, 7.0],
        Unit023.Optim.BFGS(),
    )
    @test Unit023.Optim.minimizer(optimum) ≈ [1, -2]
    @test Unit023.Optim.minimum(optimum) < 1e-12
    polynomial(v) = v[1]^3 + v[1]*v[2] + 2v[2]^2
    point = [2.0, -1.0]
    @test ForwardDiff.gradient(polynomial, point) ≈ [11, -2]
    @test ForwardDiff.hessian(polynomial, point) ≈ [12 1; 1 4]
    direction = [0.3, -0.4]
    h = 1e-5
    finite_difference =
        (polynomial(point .+ h .* direction)-polynomial(point .- h .* direction))/(2h)
    @test finite_difference ≈ dot([11, -2], direction) rtol=1e-8
end

@testset "Numerical methods and input rejection" begin
    _, path = Unit024.euler_decay(2.0, 8)
    @test path[end] ≈ (3/4)^8
    @test all(>=(0), path)
    _, coarse = Unit024.euler_decay(2.0, 8)
    _, fine = Unit024.euler_decay(2.0, 16)
    @test abs(fine[end]-exp(-2)) < abs(coarse[end]-exp(-2))
    @test Unit024.bisect(x->x^3-27, 0.0, 5.0) ≈ 3 atol=1e-9
    @test Unit024.bisect(x->x-4, 0.0, 4.0) == 4
    @test_throws ArgumentError Unit024.bisect(x->NaN, 0.0, 1.0)
    @test_throws ArgumentError Unit024.bisect(x->x, 2.0, 1.0)
    @test_throws ArgumentError Unit024.euler_decay(-1.0, 4)
    @test_throws ArgumentError Unit024.euler_decay(1.0, true)
    @test_throws ArgumentError Unit024.bisect(x -> x, -1.0, 1.0; tolerance = Inf)
    @test_throws ArgumentError Unit024.bisect(x -> x, -1.0, 1.0; maxiter = 2.5)
    output = fill(99.0, 3)
    matrix = [1.0 2.0; 3.0 4.0; 5.0 6.0]
    input = [2.0, -1.0]
    @test Unit026.affine!(output, matrix, input, [1.0, 2.0, 3.0]) == [1, 4, 7]
    @test input == [2, -1]
    original = copy(output)
    @test_throws DimensionMismatch Unit026.affine!(output, ones(2, 2), input, [1, 2])
    @test output == original
end

@testset "Properties, tasks and native boundaries" begin
    weights = [2.0, 6.0, 8.0]
    expected = [1/8, 3/8, 1/2]
    @test Unit028.probabilities(weights) == expected
    @test Unit028.probabilities(weights .* 1e100) ≈ expected
    @test Unit028.probabilities(reverse(weights)) == reverse(expected)
    @test Unit028.probabilities([0.0, 7.0, 0.0]) == [0, 1, 0]
    @test_throws ArgumentError Unit028.probabilities([big"1e10000"])
    @test_throws ArgumentError Unit028.probabilities([-1, 2])
    @test Unit029.squared_pipeline([-4, 1, 7]) == [16, 1, 49]
    @test_throws CompositeException Unit029.squared_pipeline([3, 4]; fail_after = 1)
    @test Unit030.chunk_squares(collect(-10:10)) == 770
    @test Unit030.locked_counter(3, 17) == 51
    @test Unit031.c_bytes("λx") == 3
    @test_throws ArgumentError Unit031.c_bytes("bad\0suffix")
end

@testset "Held-out decision, exact fixture and leakage failures" begin
    fixture = read(joinpath(@__DIR__, "..", "fixtures", "sensor-calibration.csv"), String)
    @test fixture == Unit032.SENSOR_CSV
    result = Unit032.analyze(fixture)
    @test result.memo["penalty"] == 2
    @test result.memo["coefficients"] ≈ [12/7, 13/7]
    @test result.memo["final_mse"] ≈ 5/98
    @test result.predictions .- result.final.y ≈ [-1/7, -2/7]
    @test result.memo["fixture_sha256"] == bytes2hex(sha256(fixture))
    table = Unit032.load_sensor()
    @test_throws ArgumentError Unit032.validate_sensor(table; cutoff = Date(2024, 1, 8))
    duplicate = copy(table)
    duplicate.id[2]=duplicate.id[1]
    @test_throws ArgumentError Unit032.validate_sensor(duplicate)
    late = copy(table)
    late.feature_available_at[5]=Date(2024, 2, 1)
    @test_throws ArgumentError Unit032.validate_sensor(late)
    wrong = copy(table)
    wrong.split[1]="final"
    @test_throws ArgumentError Unit032.validate_sensor(wrong)
    missing_label = copy(table)
    Unit032.allowmissing!(missing_label, :y)
    missing_label.y[8]=missing
    @test_throws ArgumentError Unit032.validate_sensor(missing_label)
    changed_final = replace(fixture, "s07,6,13,final"=>"s07,6,130,final")
    changed = Unit032.analyze(changed_final)
    @test changed.memo["penalty"] == result.memo["penalty"]
    @test changed.memo["coefficients"] == result.memo["coefficients"]
    @test changed.memo["final_mse"] > result.memo["final_mse"]
    @test changed.memo["fixture_sha256"] != result.memo["fixture_sha256"]
end
println("Julia independent contracts passed")
