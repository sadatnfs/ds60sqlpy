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


def implicit_solution(theta, right):
    diagonal = jnp.array([2.0 + theta, 3.0])

    def matvec(value):
        return diagonal * value

    def solve(operation, rhs):
        return rhs / diagonal

    return jax.lax.custom_linear_solve(matvec, right, solve=solve, symmetric=True)


right = jnp.array([2.0, 6.0])


def main():
    # Case 1: Check the primal equation
    solution = implicit_solution(0.0, right)
    close(solution, [1.0, 2.0])
    close(jnp.array([2.0, 3.0]) * solution, right)

    # Case 2: Check the implicit sensitivity
    close(jax.grad(lambda theta: implicit_solution(theta, right).sum())(0.0), -0.5)

    # Case 3: Pull back to the right-hand side
    close(jax.grad(lambda b: implicit_solution(0.0, b).sum())(right), [0.5, 1 / 3])

    # Case 4: Change the diagonal
    close(implicit_solution(2.0, right), [0.5, 2.0])

    # Case 5: Compare an ordinary solve
    a = jnp.diag(jnp.array([2.5, 3.0]))
    close(implicit_solution(0.5, right), jnp.linalg.solve(a, right))

    # Case 6: Detect a bogus solver
    diagonal = jnp.array([2.0, 3.0])
    wrong = jax.lax.custom_linear_solve(
        lambda x: diagonal * x,
        right,
        solve=lambda operation, rhs: jnp.zeros_like(rhs),
        symmetric=True,
    )
    assert bool(jnp.isfinite(wrong).all())
    assert not np.allclose(np.asarray(diagonal * wrong), np.asarray(right))

    # Case 7: Check a second derivative
    second = jax.grad(jax.grad(lambda theta: implicit_solution(theta, right).sum()))
    close(second(0.0), 0.5)

    # Case 8: Compile the valid interface
    solution = jax.jit(implicit_solution)(1.0, right)
    close(solution, [2 / 3, 2.0])
    close(jnp.array([3.0, 3.0]) * solution, right)

    print("jax-023" + ": 8 asserted cases passed")


if __name__ == "__main__":
    main()
