# Boosting: follow the objective across stages

Tutorial ID: `statistics-learning-005`. Prerequisites: `statistics-learning-003`, `statistics-learning-004`. Complete program: [learning_04.py](examples/learning_04.py).

## Fit the correction rather than the labels again

For half squared loss, the derivative with respect to the current prediction is \(F(x_i)-y_i\). A new tree approximates its negative, the residual. Add a shrunken update \(F_m=F_{m-1}+\eta h_m\). Initialization is part of the model: a constant mean minimizes initial squared error, while a constant log-odds score minimizes initial binary logistic loss.

Six observations have outcomes 0,0,0,6,6,6. The initial mean prediction is three and MSE is nine. A stump exactly fits residuals -3 and +3. With learning rate .5, the first update has MSE 2.25. Each subsequent exact half correction divides residuals by two and MSE by four. The complete trace is 9,2.25,.5625,.140625,.03515625. The program verifies this geometric relationship across four stages rather than only one training-loss decrease.

This noiseless easy fixture isolates optimization. It cannot establish the best stage count for noisy data. Continued training can chase noise; a validation procedure is needed for model selection.

## Derive a logistic leaf update

Use a score \(F\) with probability \(p=\sigma(F)\). Logistic loss has first derivative \(g_i=p_i-y_i\) and second derivative \(h_i=p_i(1-p_i)\). For a leaf with total gradient \(G\), total curvature \(H\), and L2 penalty \(\lambda\), the local quadratic objective is

\[
Gw+\frac12(H+\lambda)w^2,
\qquad w^*=-\frac{G}{H+\lambda}.
\]

At initial probability .5, three negative labels give \(G=1.5,H=.75\). With lambda one the leaf weight is about -.857; the positive-label leaf has +.857. Multiplying by the .5 learning rate updates scores, then the sigmoid produces probabilities. Adding .429 directly to probability would implement a different, potentially invalid model.

The gain for splitting one parent into two leaves is half the sum of the two child scores minus the parent score, less a leaf-complexity penalty gamma. Lambda controls leaf magnitude; gamma controls whether extra structure pays. Neither replaces validation. Very small logistic curvature also motivates minimum-information constraints and careful numerical handling.

## Select stages without consulting the test

The second case fits 100 shallow boosted trees on 180 rows of the nonlinear six-feature fixture. `staged_predict` evaluates every stage on a separate 90-row validation set. The minimum selects stage count; an otherwise identical model with that count is refit on the same training rows and evaluated on 90 untouched test rows.

The validation minimum contains selection noise. Its reported score is not the final performance estimate. Learning rate, depth, leaf restrictions and stage count interact: comparing only equal stage counts can give an unfair optimization budget. Real early stopping should preserve the full preprocessing and split boundary.

**Answered discussion: Is this the XGBoost package?** The leaf calculation teaches its regularized objective, and the staged example uses scikit-learn. Real optional XGBoost/LightGBM practice already exists in [Python Day 39](../../../../python/ds-60day/companion-guides/day39_gradient_boosting_xgboost_lightgbm.md). Use its declared environment; this tutorial does not import either optional package.

Continue to [PCA](06-pca-compression-and-prediction.md). Primary derivation: [XGBoost boosted-tree tutorial](https://xgboost.readthedocs.io/en/stable/tutorials/model.html).
