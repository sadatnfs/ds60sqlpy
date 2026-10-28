## Automatic differentiation follows the implemented computation

Forward-mode automatic differentiation propagates derivative information through supported numerical operations. A dual number carries a value and partial information. Arithmetic combines both components according to differentiation rules. This is different from estimating a derivative by subtracting nearby function values or manipulating a symbolic formula.

ForwardDiff supplies derivative, gradient, Jacobian and Hessian operations for suitable Julia functions. Their input/output shapes matter. A gradient belongs to a scalar-valued function of a vector; a Jacobian describes a vector-valued function; a Hessian describes second derivatives of a scalar function. A correct shape does not establish that the chosen function is the right scientific objective.

Type-generic code is essential. Hardcoding an intermediate buffer as Float64 can reject the dual values needed to propagate derivatives. Use an appropriate input-derived representation when the algorithm is intended to support such values, and avoid silently converting away derivative information.

## Worked case A: independent analytic derivatives

The scalar quadratic has a known gradient and Hessian. A second vector function has a known Jacobian. The program compares ForwardDiff's results to those hand-derived arrays, making axes and coefficients explicit. A finite-difference directional check adds a separate numerical perspective without being treated as the definition of the derivative.

{{WORKED_A}}

## Worked case B: a storage mistake blocks differentiation

One function writes into a Float64 buffer, while another uses `similar` on its input. Ordinary Float64 evaluation succeeds in both. Differentiation fails in the hardcoded-storage version because it cannot retain the required numeric type, while the generic version produces the expected derivative. The failure is a representation issue, not evidence that the mathematical function lacks a derivative.

{{WORKED_B}}

## Boundaries and nonsmooth operations

Automatic differentiation computes derivatives of the executed supported path. At a branch boundary or a nonsmooth point, the mathematical derivative may not exist or the returned convention may need careful interpretation. A value produced by an AD library is not a proof of differentiability. Diagnose the function and its domain independently.

Finite differences have their own tradeoff: a large step introduces approximation error, while a tiny step can amplify floating-point cancellation. Use a range of sensible steps and analytic cases when validating a new differentiable implementation. Do not widen a tolerance to hide an incorrect gradient shape or reduction.

## Transfer to scientific models

Check units and scaling of the objective and parameters. A sum and a mean loss have different gradient scales. Hidden state, randomness and data-dependent transformations can also change what function is being differentiated. Keep these inputs explicit and freeze any information that should not receive derivative updates.

The reference uses small CPU functions with prepared ForwardDiff. It does not qualify GPU differentiation, every external library operation or a large model's optimization behavior. Later optimization uses these derivatives as one component while still checking convergence, objective values and independent scientific assumptions.
