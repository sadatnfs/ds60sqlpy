# A legitimate Gaussian exception to independent marginal fitting

Global dependence does not always require collecting observations. Consider

\[
 y=X\beta+Zu+\epsilon,\quad
 u\sim N(0,tC),\quad \epsilon\sim N(0,sI_n),
\]

where \(X,Z\) are fixed known design matrices, \(C\) is a known positive-definite
small matrix, \(s=\sigma^2>0\), and \(t=\tau^2>0\). One latent vector \(u\)
is shared across every partition. The marginal covariance is
\(V=sI_n+tZCZ^\top\). It is generally not block diagonal by Spark partition.

The conditional observation terms factor given this one shared vector. Integrating
a different vector independently inside every partition would define a different
model. Instead, combine the sufficient statistics first and perform the one global
Gaussian integration afterward.

## Bounded distributed summary

Workers can stream sums for

\[
 X^\top X,\quad X^\top y,\quad y^\top y,\quad
 Z^\top Z,\quad Z^\top y,\quad Z^\top X,\quad n.
\]

These are blocks of the augmented Gram matrix for \([X\;Z\;y]\). With fixed small
column counts, their size does not grow with the observation count. The reference
caps fixed-design and latent-design widths at eight each. Counts, partition IDs
and an order-independent observation fingerprint accompany the sums. Empty
partitions remain present. Missing/duplicate partitions or changed data fail
rather than yielding an apparently successful partial likelihood.

The implemented `summarize` function is streaming: it holds bounded accumulators,
not all rows of a partition. `combine` requires the expected partition coverage,
row count and snapshot fingerprint. The current runnable example uses explicit
small fixture slices and an independent dense oracle. That is mathematical and
aggregation evidence; it is not actual Spark execution or a production package
API. A later Spark adapter must preserve the same snapshot and coverage contract.

## Derive the marginal objective

Let \(C=LL^\top\), \(W=ZL\), \(r=y-X\beta\), \(h=t/s\), and
\(A=I_q+hW^\top W\). The determinant and quadratic identities give

\[
 \log|V|=n\log s+\log|A|,
\]

\[
 r^\top V^{-1}r=
 \frac1s\left(r^\top r-h(W^\top r)^\top A^{-1}(W^\top r)\right).
\]

Both \(r^\top r\) and \(W^\top r\) are reconstructed from the summary blocks.
The normalized negative log likelihood is half the sum of
\(n\log(2\pi)\), the log determinant and the quadratic. The operational calculation
factorizes only the small \(q\)-dimensional matrix. It never forms an
\(n\)-dimensional inverse. The deliberately separate validation oracle does form
a tiny dense covariance, capped at64 observations.

For \(v=A^{-1}W^\top r\) and \(G=W^\top W\), the analytic score includes

\[
 \nabla_\beta L=-X^\top r/s+(h/s)X^\top Wv,
\]

\[
 \frac{\partial L}{\partial\log\tau}
 =h\operatorname{tr}(A^{-1}G)-(h/s)v^\top v,
\]

\[
 \frac{\partial L}{\partial\log\sigma}
 =n-h\operatorname{tr}(A^{-1}G)
 -\frac{r^\top r-2h(W^\top r)^\top v+h^2v^\top Gv}{s}.
\]

The reference checks these scores against central differences of the independent
full covariance calculation at two step sizes. Its conditional latent moments
are also compared with direct multivariate Gaussian conditioning.

## Changed case: do not let partitions create new latent effects

Evaluate the same rows once with the global covariance and once after dividing
them into two independently marginalized blocks. The objectives differ because
the second model creates two latent vectors. More computation partitions must
not silently change a statistical model.

A simple interpretation uses a single shared random intercept. Then
\(\operatorname{Var}(\bar Y)=t+s/n\). Adding observations cannot remove the shared
uncertainty floor \(t\). Treating \(P\) partitions as independent random-intercept
groups changes that floor to \(t/P\) in a balanced example. The resulting confidence
claim would depend on how the dataset was partitioned, which is a model error.

Likewise, an unseen row may still share the same global latent vector. A new
observation ID does not automatically mean a new latent context. Predictions for
another row in the same context condition on the learned latent distribution;
a genuinely independent new context uses its prior instead. This distinction
must be declared by the model, not guessed from storage partitions.

## Numerical and inferential limits

Raw Gram matrices can lose residual information when large nearly equal terms
are subtracted. The reference rejects cancellation-limited or nonpositive
quadratics and unqualified covariance pivots. It adds no jitter and clips no
negative quadratic to zero. Even an exactly fitted residual is refused if the
raw statistics cannot certify whether zero is exact or cancellation. Centering
or a separately qualified mergeable QR/square-root reduction is the next step,
not a silent change to the probability model.

The columns of \(X,Z\) are fixed for this derivation. An arbitrary nonlinear mean
or parameter-dependent basis does not inherit these sufficient statistics.
A finite-basis Gaussian model can be exact as defined; using that basis to
approximate another Gaussian-process kernel introduces a separate approximation
error. The [Stan Gaussian-process guide](https://mc-stan.org/docs/stan-users-guide/gaussian-processes.html)
and [Riutort-Mayol et al.](https://doi.org/10.1007/s11222-022-10167-2) describe the
Gaussian marginalization and basis-approximation context. No implementation is
copied from those sources.

Known Gaussian structure is crucial. This example does not implement a general
distributed sparse Laplace method, a non-Gaussian state-space solver or arbitrary
crossed random effects. With a fixed small latent rank, increasing the number of
observations may still provide little extra information about latent covariance
hyperparameters. Exact computation does not guarantee identification.
