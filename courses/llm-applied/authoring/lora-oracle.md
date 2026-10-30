## Independent NumPy audit of the first gradient

This additional calculation is standalone. It uses float64 algebra and a central finite difference to check the derivative independently of autograd. It does not train a second language model or replace the actual PyTorch update above.

```python
import numpy as np

x = np.ones((1, 8), dtype=np.float64)
w = np.eye(8, dtype=np.float64)
a = np.full((8, 2), 1 / 8, dtype=np.float64)
b = np.zeros((2, 8), dtype=np.float64)
scale = 2.0


def objective(first, second):
    prediction = x @ (w + scale * first @ second)
    return np.mean(prediction**2)


prediction = x @ (w + scale * a @ b)
grad_output = 2 * prediction / prediction.size
grad_b = scale * (x @ a).T @ grad_output
grad_a = scale * x.T @ grad_output @ b.T
np.testing.assert_array_equal(grad_a, np.zeros_like(a))
np.testing.assert_allclose(grad_b, 0.5, atol=1e-12, rtol=0)

step = 1e-6
positive = b.copy()
negative = b.copy()
positive[0, 0] += step
negative[0, 0] -= step
finite_difference = (objective(a, positive) - objective(a, negative)) / (2 * step)
np.testing.assert_allclose(finite_difference, grad_b[0, 0], atol=1e-9, rtol=0)

updated_b = b - 0.1 * grad_b
updated_output = x @ (w + scale * a @ updated_b)
np.testing.assert_allclose(updated_output, 0.8, atol=1e-12, rtol=0)
np.testing.assert_allclose(objective(a, updated_b), 0.64, atol=1e-12, rtol=0)
assert np.linalg.matrix_rank(a @ updated_b) == 1

zero_a = np.zeros_like(a)
zero_b = np.zeros_like(b)
zero_grad_b = scale * (x @ zero_a).T @ grad_output
zero_grad_a = scale * x.T @ grad_output @ zero_b.T
np.testing.assert_array_equal(zero_grad_a, zero_a)
np.testing.assert_array_equal(zero_grad_b, zero_b)
```

**Expected:** the analytic and finite-difference B derivative agree at 0.5; the first update gives output 0.8 and loss 0.64; setting both factors to zero leaves both factor derivatives zero.

The distinction between rank bound and realized rank also has a geometric interpretation. For any invertible r-by-r matrix R, the factors AR and R-inverse B represent the same product AB. The factorization is not unique, so interpreting one column of A as a uniquely identified semantic concept is generally unjustified. Different initialization, regularization and optimization paths can select different equivalent or approximately equivalent factors.

The [original LoRA paper](https://arxiv.org/abs/2106.09685) supplies the adaptation method and scaling convention used here. [QLoRA](https://arxiv.org/abs/2305.14314) adds a quantized frozen base and specific storage/training techniques; it is not equivalent to this unquantized matrix example. The next chapter distinguishes storage codes, dequantized computation, adapter gradients and actual GPU implementation claims. Neither a rank count nor the successful one-step fixture establishes that an adapted assistant follows domain evidence reliably.
