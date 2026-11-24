# julia-019: Linear algebra, conditioning and nonunique solutions

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-012`, `julia-013`.

Solve small linear systems, inspect residuals and distinguish a fitted prediction from an identified coefficient vector.

## Classroom execution

Open `julia-019` in `/classroom` with its prepared `julia` runtime. Worked case A (solve and check the residual) and worked case B (identical predictions from different coefficients) are complete programs: save your current pad, paste one of them and press Run. The learner file contains the six investigations below; the explained reference ends by printing `julia-019: all reference checks passed`. The [course overview](../README.md) describes the shared runtime: a fresh offline `main.jl` process with two threads and a fixed package environment.

## Key terms

- **Linear solve:** Computing `A \ b` to solve a linear system with a method suited to the matrix, rather than forming an explicit inverse.
- **LU factorization:** Decomposing a square matrix into permuted lower and upper triangular factors once so several right-hand sides solve cheaply.
- **Rank:** The number of linearly independent columns, which numerical code estimates with a tolerance on singular values.
- **Pseudoinverse:** The `pinv` result that gives the minimum-norm least-squares solution when a system is rank deficient.
- **Adjoint:** The conjugate transpose written `A'`, which equals the ordinary transpose only for real matrices.

## A matrix calculation needs named axes

A linear system \(A x=b\) relates a matrix, a vector of unknowns and an observed right-hand side. The dimensions determine which products are defined, but they do not establish whether the solution is unique or stable. Name the row and column meanings before applying a numerical operation.

Use a linear solve for a system rather than explicitly constructing an inverse just to multiply by a vector. Factorizations can be reused when several right-hand sides share the same matrix. A small residual checks how well a computed solution satisfies the equations; it does not by itself guarantee a small error in the unknowns when the system is ill-conditioned.

Rank and conditioning answer different questions. A rank-deficient system has nonunique or incompatible solutions. A nearly dependent system can have a formally unique solution that is highly sensitive to small perturbations. The numerical rank also depends on precision and a tolerance convention.

## Worked case A: solve and check the residual

The first example solves a 2-by-2 system using a reusable LU factorization. Its known solution is `[2, 3]`. The program checks both that value and the residual. This provides an independent expected result instead of treating a successful library call as its own proof.

```julia
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
```

## Worked case B: identical predictions from different coefficients

The second design matrix repeats one column. Its pseudoinverse gives a minimum-norm coefficient vector, but another vector displaced along a null direction produces the same fitted values. Matching predictions on the design matrix therefore does not identify every coefficient uniquely. The distinction matters when interpreting model parameters scientifically.

```julia
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
```

## Real and complex transposes

For complex arrays, an adjoint conjugates as well as transposes. Julia's apostrophe form represents the adjoint. `transpose` does not conjugate. An inner product uses the appropriate conjugation convention, so substituting a plain transpose can change the result even when dimensions agree. The reference includes a small complex-vector check.

Choose tolerances according to scale, conditioning and the intended decision. A printed decimal with many digits is not evidence that all digits are accurate. Inspect singular values or other conditioning information when a solution changes sharply after a small input perturbation.

## Diagnose before optimizing

Check dimensions, rank assumptions, input finiteness and residuals on small fixtures. An unexpected result can come from a transposed axis, a duplicated feature or an unsupported assumption about independence. Do not automatically regularize every failure without stating how the regularization changes the problem.

A compact first check is to print `size(design)`, `rank(design)` and `norm(design * solution - target)` together. A rank below the number of columns explains why several coefficient vectors fit equally well, and a large residual means the system has no exact solution, so least squares is answering a different question.

A pseudoinverse is a particular mathematical and numerical choice. It does not make a nonidentified parameter scientifically identifiable. Likewise, a factorization can solve an equation accurately while the equation is a poor model of the underlying data.

The programs use the prepared LinearAlgebra library and tiny matrices. They establish the stated solve, null-space and conjugation properties, not a universal recommendation for large sparse systems or arbitrary numerical scales. Later regression and optimization units retain these distinctions when constructing fitted models.


## Six investigations

### 1. Verify a solution

Multiply the computed vector by the original matrix.

**Expected:** The residual is near zero.

**Hint:** Keep the original equation and units visible.

### 2. Reuse a factorization

Double the right-hand side without refactorizing.

**Expected:** The solution doubles for this linear system.

**Hint:** The matrix is unchanged.

### 3. Expose nonidentification

Move the repeated-column coefficients along `[0, 1, -1]`.

**Expected:** Predictions on the design remain unchanged.

**Hint:** The displacement lies in the null space.

### 4. Interpret a pseudoinverse

Compare coefficient norms in case B.

**Expected:** The pseudoinverse solution has smaller norm than the shifted alternative.

**Hint:** Minimum norm is a selection rule among compatible solutions.

### 5. Use the correct transpose

Compare adjoint and transpose for the complex vector.

**Expected:** The products are 7 and 3-2im.

**Hint:** Conjugation changes the calculation.

### 6. Assess sensitivity

Perturb an ill-conditioned problem before trusting its coefficients.

**Expected:** Inspect conditioning as well as residuals.

**Hint:** A small residual need not imply stable parameters.

## Primary references

- [Julia LinearAlgebra](https://docs.julialang.org/en/v1/stdlib/LinearAlgebra/)
- [Complex arithmetic](https://docs.julialang.org/en/v1/manual/complex-and-rational-numbers/)

## Study companion

A repository-aware assistant with the learning-companion skill can review `julia-019` with you. Give it your prediction for one investigation, your source and the actual output, and ask it to find the first incorrect assumption about linear solve, factorization, rank, pseudoinverse or adjoint.
