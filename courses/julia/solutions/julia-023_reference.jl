using Test
using LinearAlgebra
using ForwardDiff
using Optim

objective(x) = (x[1]-1)^2 + 4(x[2]+2)^2
function objective_gradient!(storage, x)
    ForwardDiff.gradient!(storage, objective, x)
    return nothing
end

# === EXAMPLE A ===
function worked_a()
    result = Optim.optimize(
        objective,
        objective_gradient!,
        [5.0, 5.0],
        Optim.BFGS(),
        Optim.Options(iterations = 200, show_trace = false),
    )
    point = Optim.minimizer(result)
    @test point ≈ [1, -2]
    @test Optim.minimum(result) < 1e-12
    @test norm(ForwardDiff.gradient(objective, point)) < 1e-6
    @test Optim.converged(result)
    println("Quadratic optimizer: ", point, "; objective: ", Optim.minimum(result))
end

# === EXAMPLE B ===
function worked_b()
    result = Optim.optimize(x -> (x-3)^2, 0.0, 2.0)
    point = Optim.minimizer(result)
    @test 0 <= point <= 2
    @test abs(point-2) < 1e-5
    @test isapprox(Optim.minimum(result), 1; atol = 1e-4)
    println("Bounded optimizer: ", point)
end

# === EXERCISES ===
function exercise_checks()
    @test objective([1.0, -2.0]) == 0
    @test ForwardDiff.gradient(objective, [1.0, -2.0]) == [0, 0]
    @test objective([2.0, -2.0]) == 1
    @test objective([1.0, -1.0]) == 4
    scalar = Optim.optimize(x -> (x-0.5)^2, 0.0, 2.0)
    @test abs(Optim.minimizer(scalar)-0.5) < 1e-5
    @test Optim.minimum(scalar) < 1e-8
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-023: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
