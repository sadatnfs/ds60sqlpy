# Research, attribution and implementation boundaries

Research reviewed 2026-10-29. Links below are primary project, author or package
sources. The project implements original teaching code using documented APIs;
it does not vendor source from the cited historical modeling projects.

| Source | Concrete finding used here | Course placement |
| --- | --- | --- |
| [TMB CRAN manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf) and [DESCRIPTION](https://github.com/kaskr/adcomp/blob/master/TMB/DESCRIPTION) | TMB 1.9.25, dated 2026-08-22, GPL-2. `MakeADFun`, `compile`, `sdreport`, `checkConsistency`, `map`, `FreeADFun` are distinct operations. | 1-9, 12-20 |
| [TMB methodology paper](https://arxiv.org/abs/1509.00660) | Automatic differentiation, sparse Hessians and Laplace approximation support custom latent-variable likelihoods. Integration is not the same as maximizing a joint density. | 6, 12-17 |
| [TMB sdreport source](https://github.com/kaskr/adcomp/blob/master/TMB/R/sdreport.R) | Fixed covariance uses likelihood curvature; derived quantities use delta-method machinery; latent uncertainty has conditional and parameter-sensitivity components. | 8-9, 18 |
| [TMB introduction](https://kaskr.github.io/adcomp/Introduction.html) | R constructs objective/gradient interfaces from compiled C++ templates. Some Doxygen pages identify version 1.9.11, older than our 1.9.25 target, so API claims were cross-checked with current CRAN documentation. | 1-6 |
| [TMB parallel accumulator](https://kaskr.github.io/adcomp/structparallel__accumulator.html) | Independent sums can use OpenMP; numerical and derivative parity still need actual tests. | 20 |
| [AFModel](https://github.com/sadatnfs/AFModel) and its [MIT license](https://github.com/sadatnfs/AFModel/blob/master/AFModel/LICENSE.md) | Historical R/TMB panel forecasting architecture includes trend, fixed/group effects and autoregressive choices. We inspected the model declarations and wrote a neutral synthetic decomposition, without importing source or environment metadata. | 21, 24 |
| [PyMB](https://github.com/kforeman/PyMB) and [model wrapper](https://github.com/kforeman/PyMB/blob/master/PyMB/model.py) | Historical Python/TMB bridge uses rpy2 and global NumPy conversion activation. Our bridge uses the current scoped converter API and fixed typed model boundary. | 22-23 |
| [PyMB license](https://github.com/kforeman/PyMB/blob/master/LICENSE) | Repository license file is GPL-2.0. Its README has inconsistent license wording; this course copies no PyMB implementation. | Dependency/source attribution |
| [Neal Marquez repository list](https://github.com/nmmarquez?tab=repositories), [ar.matrix](https://github.com/nmmarquez/ar.matrix), [DESCRIPTION](https://github.com/nmmarquez/ar.matrix/blob/master/DESCRIPTION) | ar.matrix 0.1.0 describes sparse autoregressive precision and Cholesky simulation; declared license GPL (>=2). Our AR1 oracle is independently derived from its mathematical recurrence. | 15, 21 |
| [rpy2 pandas documentation](https://rpy2.github.io/doc/latest/html/pandas.html) | Docs identify 3.6.6 and demonstrate local converter contexts. Conversion may copy data and requires explicit type/timezone policy. | 22-23 |
| [R nlminb reference](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/nlminb.html) | Optimizer status and stopping controls are numerical evidence, distinct from identifiability and scientific validation. | 7, 14, 24 |

## What Spark can and cannot distribute

Independent per-group fits can run in separate processes, each with a prepared
native TMB library. A common additive fixed-effect likelihood can return values
and gradients at the same driver-supplied parameter vector. Independent latent
groups also permit a sum of group-marginal Laplace terms. These are three
different estimators/execution patterns and must retain group/row counts.

A latent covariance edge across partitions breaks independent-group
factorization. Spark does not automatically differentiate through R, deserialize
native R pointers safely, or provide a distributed sparse factorization just
because a TMB call occurs inside a task. A coupled model requires a different
algorithm or a deliberately labeled approximation. See chapters 16-17 and the
separate advanced Spark/TMB project for actual distributed tests.

## Framework and license limits

Both CppAD and TMBad are supported TMB frameworks. The owned project qualifies
CppAD first. `intern=TRUE` and some internal Laplace/Hessian facilities have
TMBad-specific requirements; they are explained, not silently claimed tested.
OpenMP is intra-process and is not evidence of Spark or multi-node execution.

Course prose, fixtures and models are original repository source. Installed TMB
and RcppEigen have their own GPL-related licenses, notices and source-availability
requirements. Preserve full licenses in any optional runtime distribution and
review its actual composition before publication. No dependency license is
replaced by this repository's top-level license. The dependency lock records
source URLs and measured SHA256 digests; it does not contain vendor source.
