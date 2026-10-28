"""Numerical quantization error and exact speculative acceptance accounting."""

import numpy as np


def example_one():
    weights = np.array([[0.1, -0.6, 1.0], [5.0, -0.01, 0.03]], dtype=np.float64)
    scale = np.max(np.abs(weights), axis=1, keepdims=True) / 127
    quantized = np.clip(np.rint(weights / scale), -127, 127).astype(np.int8)
    reconstructed = quantized.astype(float) * scale
    assert np.max(np.abs(weights - reconstructed)) <= float(scale.max() / 2 + 1e-12)
    vector = np.array([2.0, -1.0, 3.0])
    error = np.abs((weights - reconstructed) @ vector)
    bound = scale[:, 0] / 2 * np.abs(vector).sum()
    assert np.all(error <= bound + 1e-12)
    print("Weight codes", quantized, "output error", error, "bound", bound)
    print("Dequantized NumPy multiplication is not an accelerated integer kernel.")


def example_two():
    target = np.array([0.6, 0.3, 0.1])
    draft = np.array([0.2, 0.5, 0.3])
    acceptance = np.minimum(1.0, target / draft)
    accepted_mass = draft * acceptance
    rejection = 1 - float(accepted_mass.sum())
    residual = np.maximum(target - draft, 0.0)
    residual /= residual.sum()
    total = accepted_mass + rejection * residual
    np.testing.assert_allclose(acceptance, [1.0, 0.6, 1 / 3])
    np.testing.assert_allclose(total, target)
    np.testing.assert_allclose(accepted_mass, [0.2, 0.3, 0.1])
    assert abs(rejection - 0.4) < 1e-12
    print("Accepted mass", accepted_mass, "rejection", rejection, "corrected distribution", total)
    print("Exact one-step distribution proof does not establish a wall-clock speedup.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
