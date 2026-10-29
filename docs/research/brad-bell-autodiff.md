# Brad Bell's work, automatic differentiation and distributed likelihoods

This review supports the separate [Spark likelihood package](../../packages/spark-likelihood/README.md).
The primary implementation evaluates custom PyTorch likelihoods on Spark
executors and returns bounded objective/gradient summaries. It does not require
R or the classroom server. The completed R/TMB integration remains a separately
prepared reference, rather than the main package dependency.

The research covers all 26 repositories publicly listed under Brad Bell's
account at inspection, plus upstream and publicly indexed contribution
repositories. In total, 36 repository heads were recorded and 35 root README
files were read at those immutable revisions. The remaining repository,
`test_sphinx`, had no README at the checked names. The
[versioned source index](brad-bell-source-index.json) retains the exact scope and
revisions. GitHub's contributed-repository index is a recent public index, not a
complete lifetime authorship record.

## What the repository review establishes

Brad Bell's work is relevant at several different layers. CppAD provides
algorithmic differentiation of C++ programs; `cppad_mixed` adds native
mixed-effects optimization; other repositories explore interfaces, tensor
operations, sparse derivatives, code generation, numerical comparisons and
scientific documentation. These are related capabilities, not interchangeable
packages. [CppAD](https://github.com/coin-or/CppAD),
[cppad_mixed](https://cppad-mixed.readthedocs.io/latest/)

| Project or group                                             | Evidence inspected                                                             | Consequence for this project                                                                                                    |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `coin-or/CppAD`                                              | Current upstream source, documentation and account-attributed commits          | A substantive native C++ AD option; keep derivative recording and evaluation separate in the teaching                           |
| `cppad_mixed`                                                | Public C++ API and mixed-effects theory                                        | A possible future native Laplace backend, with its own dependencies and AGPL-3.0-or-later terms                                 |
| `cppad_py`                                                   | Python and C++ object APIs, sparse derivatives and mixed-model interface       | An alternative Python-to-C++ route that does not require R; installation and version compatibility need their own qualification |
| `CppADCodeGen`                                               | Upstream documentation, Brad's fork and observed upstream commits              | Derivative code generation is a distinct preparation stage, not a reason to compile arbitrary models inside Spark tasks         |
| `sparse_ad`                                                  | Repository and linked research description                                     | Add explicit sparsity-pattern, coloring and sparse-Hessian reasoning to advanced model development                              |
| `implicit_ad`                                                | README and its support statement                                               | Teach implicit differentiation, but do not adopt this unsupported package as a default dependency                               |
| `cmpad`                                                      | Comparison algorithms and correctness checks                                   | Compare end-to-end numerical correctness and cost, including recording, compilation and communication                           |
| `ad-tensor`                                                  | Libtorch-overloading description and preliminary-release statement             | A research direction for tensor-valued AD, not an already qualified backend                                                     |
| `rustad`                                                     | Implemented features, preliminary release and unstable-API statement           | Useful concepts for future Rust AD lessons; do not treat its GPU/LLVM wish list as completed capability                         |
| `dismod_at` and `at_cascade`                                 | Model/application descriptions and documentation links                         | Study complete numerical applications and dependent fitting workflows, while preserving their domain assumptions                |
| `cppad_swig`                                                 | Interface documentation and unsupported status                                 | Historical interface design, not a new recommended production dependency                                                        |
| `mat2cpp`                                                    | Matlab/Octave-to-C++ example scope                                             | A useful bridge for explaining numerical language migration                                                                     |
| `xrst`, `omhelp`                                             | Documentation tooling descriptions                                             | Keep model code, examples, equations and generated documentation connected                                                      |
| Feedstocks and packaging forks                               | Repository metadata and recent public contribution index                       | Reproducible builds and platform compatibility are part of scientific software quality                                          |
| `Trilinos` fork                                              | Fork metadata; no account-linked commit returned by the bounded upstream query | Do not attribute the upstream project or its AD packages to Brad merely because a fork exists                                   |
| `match_csv`, `python-reference`, `test_sphinx`, `tst_github` | Inventory and available README material                                        | Peripheral numerical-interface, language or tooling references; no direct modeling-backend adoption                             |

The recent public contribution index also named `LaurentMazare/tch-rs`
and seven CppAD/conda-related repositories. That index can reflect issues or
pull requests as well as code. `tch-rs` is a Rust binding to Libtorch;
its inspected current branch expects a different Libtorch version from this
classroom's pinned Torch runtime, so it cannot simply be inserted into the
existing worker. [tch-rs](https://github.com/LaurentMazare/tch-rs)

Bounded author queries found account-attributed commits in CppAD,
`kaskr/adcomp` and upstream CppADCodeGen. The observed adcomp commit
concerned a benchmark script. Brad is also a coauthor of the TMB paper, but
these facts do not justify attributing all TMB or TMBad implementation work to
one person. [TMB paper](https://arxiv.org/abs/1509.00660)

## Can adcomp support an R-free C++ calculation?

Yes, for the AD core we actually exercised. The
[standalone native experiment](../../examples/native-ad-core/README.md)
compiles an original likelihood functor with the TMBad component from the
checksum-pinned TMB 1.9.25 source archive. Its configuration adapter supplies
standard C++ diagnostic streams and assertions. R is not installed in the test
image, and the executable links neither `libR` nor `libpython`.

The experiment compares values, gradients and Hessians with independent Gaussian
formulas at six data/parameter combinations. On native Linux ARM64, maximum
absolute error was about \(1.14\times10^{-13}\). Its
[source-bound receipt](../../examples/native-ad-core/qualification.json)
records exactly what ran.

This is not drop-in loading of an arbitrary TMB model library. The usual TMB
interface includes R headers, R data objects, template input macros, model
construction and reporting. A portable C++ functor using TMBad is a different
interface. The research example does not qualify all TMB distributions,
random-effect integration, concurrent JNI calls or a multi-node Spark connector.
[TMB interface source](https://github.com/kaskr/adcomp/blob/master/TMB/inst/include/TMB.hpp),
[TMBad function-object source](https://github.com/kaskr/adcomp/blob/master/TMB/inst/include/TMBad/TMBad.hpp)

The bundled TMB-modified CppAD headers also exposed standalone-build assumptions
during a separate exploratory attempt. That failed attempt is not evidence that
upstream CppAD cannot run independently; upstream CppAD is specifically a C++ AD
library with its own supported configuration. It is evidence that copying a
nested vendor directory without its configuration is not a complete integration.

TMBad contains forward/reverse code-generation machinery as well. Inspection of
the pinned implementation found an experimental helper using fixed temporary
filenames and an unchecked compiler-failure branch before attempting to load a
shared library. We did not use that helper for the accepted experiment. A future
code-generation backend needs owned build directories, checked compiler exits,
source/binary identities and independent numerical acceptance.
[Code-generation implementation](https://github.com/kaskr/adcomp/blob/master/TMB/inst/include/TMBad/TMBad.cpp)

## The distributed estimator's mathematical boundary

Let \(\theta\in\mathbb R^d\) be the shared parameter vector and \(I_p\) the
observations assigned to partition \(p\). For a row-additive objective,

\[
L(\theta)
=\sum_{p=1}^{P}\underbrace{\sum_{i\in I_p}w_i\ell_i(\theta)}_{L_p(\theta)}
+\frac{\lambda}{2}\lVert\theta\rVert_2^2.
\]

Each executor returns \(L_p\), \(\nabla L_p\), counts, weight totals and identity
evidence. The driver combines these summaries, adds the shared penalty once and
chooses the next parameter vector. Its numerical payload grows with \(Pd\),
rather than with the full observation table. Spark scheduling and local
differentiation have separate responsibilities.

For a complete independent group \(g\), replace the row sum with a scalar
group objective \(\ell_g(\theta;y_g)\). All observations needed by that group
must reach the same bounded evaluation unit. The current package includes an
exact Gaussian random-intercept marginal and an original Gamma-Poisson custom
example. The latter integrates a shared latent rate analytically, rather than
pretending that an AD engine automatically performs statistical integration.

Three operations must remain distinct:

1. One shared fit, obtained by summing compatible contributions at the same
   parameter vector.
2. Independent fits with a different parameter vector for each group.
3. A coupled model whose covariance or latent state spans multiple units.

Averaging independently fitted coefficients does not generally recover the
shared MLE. Splitting a coupled likelihood can change the model. Neither native
C++ nor a faster derivative engine changes those facts.

For large neural parameter sets, use an appropriate distributed training
strategy rather than collecting a separate full gradient from every Spark
partition into a small-parameter driver optimizer. The package's opt-in
TorchDistributor/Lightning examples teach rank scaling and exact observation
coverage separately from the MLE interface.

## Additional mathematics worth teaching

### Derivatives of an optimized quantity

If \(u^{\star}(\theta)\) solves
\(\nabla_u f(\theta,u^{\star})=0\), differentiating that equation gives

\[
\frac{\partial u^{\star}}{\partial\theta}
=-H_{uu}^{-1}H_{u\theta},
\]

when the required derivatives exist and \(H_{uu}\) is nonsingular. This is a
linear solve, not an instruction to form a dense inverse. It explains why an
inner optimizer's accuracy and conditioning affect an outer gradient.

For a Laplace approximation, let \(f\) be the joint negative log density,
\(u^{\star}\) an interior conditional mode, and \(q\) the latent dimension.
The Hessian in the latent coordinates must be positive definite at that mode:

\[
L_{\mathrm{Laplace}}(\theta)
=f(\theta,u^{\star})+\frac12\log\det H_{uu}(\theta,u^{\star})
-\frac q2\log(2\pi).
\]

The envelope theorem simplifies the derivative of the first term at an exact
inner optimum. It does not remove the total derivative of the log-determinant
term. Treating the fitted latent state as an arbitrary detached constant can
therefore produce the wrong outer gradient. Gaussian-only examples can hide
this issue when the Hessian does not depend on the latent state.

CppAD Mixed's explicit random/fixed likelihood, optimization and information
interfaces are particularly relevant here. Its C++ API demonstrates that
TMB-like mixed-model computation is possible without making R the only
integration route. We have researched that API, not claimed a compiled
CppAD Mixed/Spark backend. [CppAD Mixed theory](https://cppad-mixed.readthedocs.io/latest/theory.html)

### Sparse and directional derivatives

A scalar objective often benefits from reverse mode because the desired output
is one gradient. A Hessian-vector product can be computed as

\[
H(\theta)v=\nabla_\theta\left(\nabla_\theta L(\theta)^\mathsf{T}v\right),
\]

without necessarily materializing every Hessian entry. Sparse patterns and
coloring can reduce work when the model structure supports them. These ideas
deserve explicit examples before promising a dense Hessian for thousands of
parameters. [Sparse derivative research](https://arxiv.org/abs/2111.05207)

### Numerical stability is part of the model interface

A finite result can still be wrong. Review found that a naive Gamma-Poisson
formula could cancel to zero when shape and rate were both very large. The
example was rewritten with stable ratio/rising-factorial algebra and an explicit
supported-count regime. Zero- and nonzero-count Poisson-limit checks now test
the value and score, rather than merely testing that neither is NaN.

A model's source identity must also distinguish meaningful callables and
configuration. Same-file anonymous functions and changed defaults were concrete
review findings. Registration now has a stricter named-source/configuration
contract; this is compatibility evidence, not a digital signature certifying
scientific correctness.

### Benchmark the complete path

Measure derivative correctness first, then separate model preparation, tape
recording, compilation, warm evaluation, serialization, Spark scheduling and
optimizer passes. Keep dtype, threads, parameter dimension and observation
counts comparable. A fast isolated kernel does not establish a faster
end-to-end distributed fit. The comparison structure in `cmpad` is useful
for designing such experiments. [cmpad](https://cmpad.readthedocs.io/)

## Where this material belongs

| Topic                                               | Current learning route or implementation                                                                |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Additivity, shared parameters and bounded summaries | Advanced Spark `asm-002`, `asm-006`, `asm-007`; package Spark adapters                                  |
| Nonlinear custom likelihoods                        | `asm-010`; PyTorch likelihood course and package model-registration examples                            |
| Nonseparable objectives                             | `asm-011`, `asm-033`, `asm-036`                                                                         |
| Analytic, finite-difference and AD checks           | `clp-003`, `clp-016`; native and package numerical gates                                                |
| Inner/outer optimization and Laplace reasoning      | `tmb-013`, `tmb-014`, `tmb-035`                                                                         |
| Sparse matrices and derivative structure            | `tmb-015`, `tmb-036`, `tmb-041`                                                                         |
| Branches and atomic derivative contracts            | `tmb-046`, `tmb-047`                                                                                    |
| One/two-rank training and scaling                   | `asm-027`, `asm-028`, `clp-019`; package training examples                                              |
| Native C++ AD feasibility                           | `examples/native-ad-core`, with its explicit qualification limits                                       |
| Standalone modeler-facing API                       | `packages/spark-likelihood`, independent of the classroom                                               |
| Research-derived future extensions                  | Sparse/directional derivatives, implicit nested objectives and prepared native/code-generation backends |

The priorities are deliberate: a tested R-free Spark/PyTorch package first,
original numerical oracles and durable model contracts throughout, and optional
native backends only after their dependency, numerical and execution boundaries
are qualified. Experimental or unsupported upstream projects remain research
references, not hidden runtime dependencies.
