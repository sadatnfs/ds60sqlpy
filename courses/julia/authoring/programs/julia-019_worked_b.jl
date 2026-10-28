using Test
using LinearAlgebra
BLAS.set_num_threads(1)

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

worked_b()
