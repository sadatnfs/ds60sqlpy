"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import optimize


def case_07():
    x = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
    y = np.array([1.0, 2.0, 4.0])
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    assert np.allclose(beta, [5 / 6, 3 / 2]) and np.allclose(x.T @ residual, 0)
    hessian = x.T @ x
    eigenvalues = np.linalg.eigvalsh(hessian)
    at = np.array([0.2, 0.5])
    analytic = x.T @ (x @ at - y)
    difference = optimize.approx_fprime(at, lambda b: 0.5 * np.sum((x @ b - y) ** 2), 1e-7)
    assert np.allclose(analytic, difference, atol=1e-6)

    def descend(rate):
        b = np.zeros(2)
        for _ in range(30):
            b -= rate * (x.T @ (x @ b - y))
        return float(np.linalg.norm(b - beta))

    stable = descend(1 / eigenvalues[-1])
    unstable = descend(2.2 / eigenvalues[-1])
    assert stable < unstable
    result = {
        "beta": beta.tolist(),
        "residual": residual.tolist(),
        "hessian_eigenvalues": eigenvalues.tolist(),
        "gradient": analytic.tolist(),
        "stable_error": stable,
        "oversized_step_error": unstable,
    }
    print("07 geometry and optimization:", result)
    return result


def main():
    case_07()


if __name__ == "__main__":
    main()
