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

# === EXAMPLE A ===
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

# === EXAMPLE B ===
function worked_b()
    x = [2.0, 3.0]
    @test hardcoded_storage(x) == 13
    @test generic_storage(x) == 13
    @test_throws MethodError ForwardDiff.gradient(hardcoded_storage, x)
    @test ForwardDiff.gradient(generic_storage, x) ≈ [4, 6]
    println("Generic storage retains derivative information")
end

# === EXERCISES ===
function exercise_checks()
    @test ForwardDiff.derivative(sin, 0.0) == 1
    @test ForwardDiff.derivative(x -> x^3, 2.0) == 12
    @test size(ForwardDiff.jacobian(vector_function, [2.0, 3.0])) == (2, 2)
    @test ForwardDiff.gradient(x -> sum(x), [1.0, 2.0]) == [1, 1]
    @test ForwardDiff.gradient(x -> sum(x)/length(x), [1.0, 2.0]) == [0.5, 0.5]
    @test generic_storage(Float32[2, 3]) isa Float32
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-022: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
