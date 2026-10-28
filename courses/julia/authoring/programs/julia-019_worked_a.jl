using Test
using LinearAlgebra
BLAS.set_num_threads(1)

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

worked_a()
