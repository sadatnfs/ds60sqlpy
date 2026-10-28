using Test
using LinearAlgebra
using ForwardDiff

quadratic(x) = x[1]^2 + 3x[2]^2
vector_function(x) = [x[1]^2 + x[2], x[1] * x[2]]

function hardcoded_storage(x)
    output = zeros(Float64, length(x))
    output .= x .^ 2
    return sum(output)
end

function generic_storage(x)
    output = similar(x)
    output .= x .^ 2
    return sum(output)
end

function worked_a()
    x = [2.0, 3.0]
    @test ForwardDiff.gradient(quadratic, x) ≈ [4, 18]
    @test ForwardDiff.hessian(quadratic, x) ≈ [2 0; 0 6]
    @test ForwardDiff.jacobian(vector_function, x) ≈ [4 1; 3 2]
    direction = [1.0, -1.0]
    step = 1e-5
    finite_difference = (quadratic(x + step*direction) - quadratic(x - step*direction)) / (2step)
    @test isapprox(finite_difference, dot([4, 18], direction); atol = 1e-8)
    println("Gradient: ", ForwardDiff.gradient(quadratic, x))
end

worked_a()
