using Test
using LinearAlgebra
using ForwardDiff
using Optim

objective(x) = (x[1]-1)^2 + 4(x[2]+2)^2
function objective_gradient!(storage, x)
    ForwardDiff.gradient!(storage, objective, x)
    return nothing
end

function worked_b()
    result = Optim.optimize(x -> (x-3)^2, 0.0, 2.0)
    point = Optim.minimizer(result)
    @test 0 <= point <= 2
    @test abs(point-2) < 1e-5
    @test isapprox(Optim.minimum(result), 1; atol = 1e-4)
    println("Bounded optimizer: ", point)
end

worked_b()
