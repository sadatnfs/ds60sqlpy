# A non-Gaussian group likelihood without R

Suppose observations within a group share an unobserved event rate. The model is

\[
\lambda_g\sim\operatorname{Gamma}(\alpha,\text{rate}=\beta),\qquad
Y_{gi}\mid\lambda_g\sim\operatorname{Poisson}(e_{gi}\lambda_g),
\]

with positive known exposures. Alpha is a dimensionless shape, beta is a rate parameter rather than a Gamma scale, and the fitted coordinates are `log_alpha` and `log_beta`. Rates are independent across groups given those shared parameters. A latent rate shared across different declared groups would violate this factorization.

The source is `example_gamma_poisson.py`, a normal custom registration module. Neither the row reducer nor the complete-unit reducer contains a special case for this distribution.

## Integrate the rate exactly

For one complete group, write \(S=\sum_i y_i\) and \(E=\sum_i e_i\). Multiplying the conditional Poisson probabilities by the Gamma density and integrating the rate gives

\[
p(\mathbf y)=\frac{\beta^\alpha\Gamma(\alpha+S)}
 {\Gamma(\alpha)(\beta+E)^{\alpha+S}}
 \prod_i\frac{e_i^{y_i}}{\Gamma(y_i+1)}.
\]

The NLL therefore includes both Gamma normalizers and all exposure/factorial terms. Directly subtracting two large `lgamma` values can erase a real likelihood and gradient. The implementation instead uses the exact integer-count rising-factorial identity

\[
\log\Gamma(\alpha+S)-\log\Gamma(\alpha)
=S\log\alpha+\sum_{k=1}^{S-1}\log(1+k/\alpha).
\]

The sum is empty for zero or one total count. Softplus evaluates the logarithms in log coordinates. A log-product formulation preserves the small ratio multiplied by a large shape, including the Poisson limit `log_alpha=log_beta=100`: zero counts with total exposure three have NLL approximately three and log-coordinate gradient `(3, -3)`, not zero. This reference model explicitly bounds total count per group at 10,000 for the finite recurrence, independently of the row bound. Both log parameters must remain in the declared float64 reference domain `[-300, 300]`. It refuses larger counts and nonfinite results rather than silently fitting an inaccurate objective. That bound belongs to this example, not the generic complete-unit engine. It validates positive exposures and nonnegative integer counts. The integral is exact through conjugacy; this example does not claim a generic numerical integration or Laplace engine.

The validation uses independent SciPy `gammaln` and `digamma` formulas. In log coordinates, the two score components are

\[
\frac{\partial L}{\partial\log\alpha}
=\alpha\left[\psi(\alpha)-\psi(\alpha+S)-\log\beta+\log(\beta+E)\right],
\]

\[
\frac{\partial L}{\partial\log\beta}
=-\alpha+(\alpha+S)\frac{\beta}{\beta+E}.
\]

Checking those against automatic differentiation tests more than whether a gradient happens to be finite.

## Why the group cannot be split

With alpha two, beta one, two exposures equal to one and two zero counts, the joint zero-count probability is \(1/9\). Integrating two independent rates separately would instead give \(1/16\). Both computations can return finite numbers, but they describe different dependence structures.

`TorchUnitLoss` preserves the whole group. `CompleteUnit` carries a single unit weight and the driver combines only the resulting likelihood/gradient summaries. A large group must not be split to satisfy a batch limit. This model has sufficient statistics for its parameter-dependent terms; a separately derived statistics-based model could reduce large groups in Spark, but must retain the allocation constants when claiming the full normalized probability. That alternative needs its own declared schema and numerical tests.

## Register and use the model

```python
from ds60_spark_likelihood import register_model_factory, resolve_model
from ds60_spark_likelihood.example_gamma_poisson import gamma_poisson_model

register_model_factory("gamma_poisson_shared_rate", gamma_poisson_model)
model = resolve_model("gamma_poisson_shared_rate", {"max_unit_rows": 256})
```

Each unit row contains exposure followed by count. The numerical validation compares a Torch fit with a serial analytic SciPy objective, and the Spark validation compares the distributed fit with that same independent reference. These are small original synthetic cases, not large-data timing or interval-coverage claims.

## Prediction for a new group

The declared target is `new_group_expected_count`:

\[
E[Y_{\mathrm{new}}\mid e,\alpha,\beta]=e\alpha/\beta.
\]

It averages over the rate of a new group. Prediction receives only exposure, never a response label or training group ID. For an already observed group, the posterior rate mean would instead be \((\alpha+S)/(\beta+E)\). That conditional target needs its own state/input contract and is not silently substituted by the package.

The likelihood can be poorly identified with too few independent groups, and all-zero data can lead toward a boundary. More rows sharing one rate are not the same as more independent rate realizations. Inspect optimizer status, bounds, gradients and the scientific design before interpreting hyperparameters.
