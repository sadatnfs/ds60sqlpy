## A matrix calculation needs named axes

A linear system \(A x=b\) relates a matrix, a vector of unknowns and an observed right-hand side. The dimensions determine which products are defined, but they do not establish whether the solution is unique or stable. Name the row and column meanings before applying a numerical operation.

Use a linear solve for a system rather than explicitly constructing an inverse just to multiply by a vector. Factorizations can be reused when several right-hand sides share the same matrix. A small residual checks how well a computed solution satisfies the equations; it does not by itself guarantee a small error in the unknowns when the system is ill-conditioned.

Rank and conditioning answer different questions. A rank-deficient system has nonunique or incompatible solutions. A nearly dependent system can have a formally unique solution that is highly sensitive to small perturbations. The numerical rank also depends on precision and a tolerance convention.

## Worked case A: solve and check the residual

The first example solves a2-by -2 system using a reusable LU factorization. Its known solution is[2,3]. The program checks both that value and the residual. This provides an independent expected result instead of treating a successful library call as its own proof.

{{WORKED_A}}

## Worked case B: identical predictions from different coefficients

The second design matrix repeats one column. Its pseudoinverse gives a minimum-norm coefficient vector, but another vector displaced along a null direction produces the same fitted values. Matching predictions on the design matrix therefore does not identify every coefficient uniquely. The distinction matters when interpreting model parameters scientifically.

{{WORKED_B}}

## Real and complex transposes

For complex arrays, an adjoint conjugates as well as transposes. Julia's apostrophe form represents the adjoint. `transpose` does not conjugate. An inner product uses the appropriate conjugation convention, so substituting a plain transpose can change the result even when dimensions agree. The reference includes a small complex-vector check.

Choose tolerances according to scale, conditioning and the intended decision. A printed decimal with many digits is not evidence that all digits are accurate. Inspect singular values or other conditioning information when a solution changes sharply after a small input perturbation.

## Diagnose before optimizing

Check dimensions, rank assumptions, input finiteness and residuals on small fixtures. An unexpected result can come from a transposed axis, a duplicated feature or an unsupported assumption about independence. Do not automatically regularize every failure without stating how the regularization changes the problem.

A pseudoinverse is a particular mathematical and numerical choice. It does not make a nonidentified parameter scientifically identifiable. Likewise, a factorization can solve an equation accurately while the equation is a poor model of the underlying data.

The programs use the prepared LinearAlgebra library and tiny matrices. They establish the stated solve, null-space and conjugation properties, not a universal recommendation for large sparse systems or arbitrary numerical scales. Later regression and optimization units retain these distinctions when constructing fitted models.
