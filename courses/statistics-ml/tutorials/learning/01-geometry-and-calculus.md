# Geometry, derivatives and the meaning of a fit

Tutorial ID: `statistics-learning-001`. Prerequisites: `statistics-002`, `statistics-003`. Complete program: [learning_07.py](examples/learning_07.py).

## Build the objects before multiplying them

Three observations have predictor values 0,1,2 and outcomes 1,2,4. A scalar is one number. A vector stores an ordered collection of numbers; here the outcome vector has three entries. A matrix arranges numbers by row and column. Put an intercept and predictor in a three-by-two design matrix:

\[
X=\begin{pmatrix}1&0\\1&1\\1&2\end{pmatrix},\quad
y=\begin{pmatrix}1\\2\\4\end{pmatrix},\quad
\beta=\begin{pmatrix}\beta_0\\\beta_1\end{pmatrix}.
\]

Each row's dot product with beta is a prediction: multiply corresponding entries and add. Therefore \(X\beta\) has three entries, while \(X^{\mathsf T}r\) has two. These dimensions are a useful check before interpreting a result. A broadcast that creates a three-by-three array from two length-three quantities can silently turn one error per observation into nine unrelated differences.

## Derive the closest prediction

Let \(L(\beta)=\frac12\sum_i(x_i^{\mathsf T}\beta-y_i)^2\). The chain rule differentiates the outer square, then the inner linear expression. The resulting gradient and Hessian are

\[
\nabla L=X^{\mathsf T}(X\beta-y),\qquad H=X^{\mathsf T}X.
\]

The gradient is the local slope in each coefficient direction. The Hessian describes how those slopes change. For any vector \(v\), \(v^{\mathsf T}Hv=\lVert Xv\rVert^2\ge0\), so the squared-loss surface is convex. Full column rank makes it strictly convex and the coefficient solution unique.

Solving gives \(\widehat\beta=(5/6,3/2)\). Residuals are \((1/6,-1/3,1/6)\), orthogonal to both columns. The program checks the coefficients and orthogonality using a least-squares solver. The all-ones column explains why residuals sum to zero. Without an intercept that identity need not hold.

## Check a derivative independently

The code compares the analytic gradient at a chosen point with small finite differences of the scalar objective. Agreement checks this derivative locally. Finite differences themselves can be unreliable near discontinuities, with poorly conditioned calculations or when subtraction cancellation dominates. Use more than one perturbation size for difficult functions rather than increasing tolerance until a check passes.

For a positive-definite quadratic, gradient descent is stable with a positive step smaller than \(2/\lambda_{\max}(H)\). The example compares a step of \(1/\lambda_{\max}\) with \(2.2/\lambda_{\max}\). The larger step diverges along the steepest direction. A converged optimizer still says nothing about whether the chosen outcome or sampling model is scientifically appropriate.

## Redundant columns and numerical sensitivity

Adding twice the predictor as another column does not add an independent direction. Predictions can remain uniquely determined even when coefficients are not. A tiny singular value indicates a direction in which small data changes create large coefficient changes. Ridge changes the estimation problem by shrinking such directions; QR/SVD improves numerical solution without inventing missing information.

**Answered discussion: Does the fitted line prove a population effect?** No. Its geometry holds without normality. An uncertainty interval adds assumptions about sampling and errors; a causal interpretation adds identification assumptions. Keep these layers separate when explaining a coefficient.

Continue to [likelihood and intervals](02-likelihood-and-inference.md). API reference: [NumPy least squares](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html).
