using Test
using LinearAlgebra
BLAS.set_num_threads(1)

# === EXAMPLE A ===
function worked_a()
    matrix = [3.0 1.0; 1.0 2.0]
    target = [9.0, 8.0]
    factorization = lu(matrix)
    solution = factorization \ target
    @test solution ≈ [2.0, 3.0]
    @test norm(matrix * solution - target) < 1e-12
    @test factorization \ (2target) ≈ 2solution
    println("Linear solution: ", solution)
end

# === EXAMPLE B ===
function worked_b()
    x = collect(0.0:3.0)
    design = hcat(ones(4), x, x)
    target = 1 .+ 2x
    coefficients = pinv(design) * target
    alternative = coefficients + [0.0, 1.0, -1.0]
    @test rank(design) == 2
    @test design * coefficients ≈ target
    @test design * alternative ≈ target
    @test norm(coefficients) < norm(alternative)
    println("Nonunique coefficients with identical fitted values")
end

# === EXERCISES ===
function exercise_checks()
    values = ComplexF64[1+im, 2-im]
    @test dot(values, values) == 7+0im
    @test values' * values == 7+0im
    @test transpose(values) * values == 3-2im
    @test norm(values)^2 ≈ 7
    @test rank([1.0 2.0; 2.0 4.0]) == 1
    @test_throws DimensionMismatch [1.0 0.0; 0.0 1.0] * [1.0, 2.0, 3.0]
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-019: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
