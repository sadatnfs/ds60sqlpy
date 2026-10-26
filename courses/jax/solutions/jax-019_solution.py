"""Small offline JAX mechanism investigation; CPU evidence only."""

from __future__ import annotations

import math
import numpy as np
import jax
import jax.numpy as jnp


# Choose precision before creating arrays; the usual JAX default is 32 bit.
jax.config.update("jax_enable_x64", True)


def close(actual, expected, *, atol=1e-10, rtol=1e-10):
    np.testing.assert_allclose(np.asarray(actual), expected, atol=atol, rtol=rtol)


matrix = jnp.array([[3.0, 1.0], [1.0, 2.0]])
right = jnp.array([9.0, 8.0])


def admitted_matrix(value):
    condition = np.linalg.cond(np.asarray(value))
    if not np.isfinite(condition) or condition > 1e10:
        raise ValueError("matrix outside the declared conditioning policy")


def parameter_solution(theta):
    a = jnp.diag(jnp.array([2.0 + theta, 3.0]))
    return jnp.linalg.solve(a, jnp.array([2.0, 6.0]))


def main():
    # Case 1: Check a solve by its equation
    admitted_matrix(matrix)
    solution = jnp.linalg.solve(matrix, right)
    close(solution, [2.0, 3.0])
    close(matrix @ solution - right, [0.0, 0.0])

    # Case 2: Differentiate a controlled matrix change
    close(parameter_solution(0.0), [1.0, 2.0])
    close(jax.grad(lambda theta: parameter_solution(theta).sum())(0.0), -0.5)

    # Case 3: Change the right-hand side
    close(jnp.linalg.solve(matrix, jnp.array([4.0, 3.0])), [1.0, 1.0])

    # Case 4: Differentiate with respect to b
    gradient = jax.grad(lambda b: jnp.linalg.solve(matrix, b).sum())(right)
    close(gradient, [0.2, 0.4])
    close(matrix.T @ gradient, [1.0, 1.0])

    # Case 5: Reject a singular fixture
    try:
        admitted_matrix(jnp.array([[1.0, 2.0], [2.0, 4.0]]))
    except ValueError:
        pass
    else:
        raise AssertionError("singular matrix admitted")

    # Case 6: Check the sensitivity numerically
    h = 1e-5
    finite = (parameter_solution(h).sum() - parameter_solution(-h).sum()) / (2 * h)
    close(finite, -0.5, atol=1e-8, rtol=0.0)

    # Case 7: Interpret ridge regularization
    x = jnp.array([[1.0], [2.0], [3.0]])
    y = 2 * x[:, 0]
    ridge = jnp.linalg.solve(x.T @ x + 14 * jnp.eye(1), x.T @ y)
    close(ridge, [1.0])

    # Case 8: Compile a valid solve
    compiled = jax.jit(jnp.linalg.solve)
    solution = compiled(matrix, right)
    close(solution, [2.0, 3.0])
    close(matrix @ solution, right)

    print("jax-019" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
