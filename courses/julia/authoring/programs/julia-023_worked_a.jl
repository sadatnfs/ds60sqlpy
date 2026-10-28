using Test
using LinearAlgebra
using ForwardDiff
using Optim

objective(x) = (x[1]-1)^2 + 4(x[2]+2)^2
function objective_gradient!(storage, x)
    ForwardDiff.gradient!(storage, objective, x)
    return nothing
end

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

worked_a()
