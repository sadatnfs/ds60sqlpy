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

worked_a()

# Task 1: Multiply the computed vector by the original matrix.
# Task 2: Double the right-hand side without refactorizing.
# Task 3: Move the repeated-column coefficients along[0,1,-1].
# Task 4: Compare coefficient norms in case B.
# Task 5: Compare adjoint and transpose for the complex vector.
# Task 6: Perturb an ill-conditioned problem before trusting its coefficients.

# Write your independent changes below.
