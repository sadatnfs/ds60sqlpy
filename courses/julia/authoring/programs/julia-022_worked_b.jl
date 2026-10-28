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

function worked_b()
    x = [2.0, 3.0]
    @test hardcoded_storage(x) == 13
    @test generic_storage(x) == 13
    @test_throws MethodError ForwardDiff.gradient(hardcoded_storage, x)
    @test ForwardDiff.gradient(generic_storage, x) ≈ [4, 6]
    println("Generic storage retains derivative information")
end

worked_b()
