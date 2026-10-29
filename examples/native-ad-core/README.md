# Standalone C++ automatic differentiation from TMBad

This is a bounded research example, separate from the primary Spark/PyTorch
modeling package. It evaluates an original C++ Gaussian likelihood functor using
the TMBad component distributed with TMB 1.9.25. It does not initialize R or load
an R model object.

## Prepare and run

Prepare the ordinary C++ image through the classroom, then build this example:

```bash
./classroom build --profile cpp20
docker build --progress=plain -t ds60-native-ad:research examples/native-ad-core
docker run --rm --network none --read-only --cap-drop ALL ds60-native-ad:research
```

The default build uses the C++ image named in the Dockerfile. A compatible
already-prepared image can be selected with `--build-arg BASE_IMAGE=IMAGE`.
The build downloads a checksum-pinned source archive from CRAN, retains its
archive and license, extracts the TMBad implementation and pinned Eigen headers, and compiles the
original test program. Execution makes no downloads and requires no writable
host mount.

Linux containers provide the same preparation route on Linux, macOS and
Windows with WSL 2. See `qualification.json` for the architecture actually
executed. Do not infer a second architecture or a remote Spark deployment from
that receipt.

## What is checked

For data \(y_1,\ldots,y_n\), mean \(\mu\) and parameter
\(s=\log\sigma\), the normalized negative log likelihood is

\[
L(\mu,s)=n\left(s+\frac12\log(2\pi)\right)
+\frac12e^{-2s}\sum_i(y_i-\mu)^2.
\]

The program differentiates this expression with TMBad, then compares its value,
gradient and Hessian with independently written formulas. It uses two datasets
and three parameter settings, including points away from the optimum. The
program prints success only after all six cases pass.

`tmbad_probe.cpp` uses TMBad's C++ function object directly. Its small
configuration adapter maps diagnostic output to standard C++ streams and keeps
assertions enabled. The full TMB R interface is not involved. The image build
also checks that R is absent and that the executable links neither `libR`
nor `libpython`.

## What this establishes

The AD core can evaluate this C++ functor without an R runtime. This is useful
evidence for a future native worker or JVM/native adapter. The experiment does
not provide drop-in execution of arbitrary TMB templates: their data macros,
R object construction, random-effect integration and reporting still need
appropriate adapters or implementations.

The included program is single-process and serial. It does not qualify JNI
thread safety, distributed model fitting, sparse latent-variable inference,
GPU execution or performance. The library's experimental code-generation
helper is not used. In particular, this example does not compile learner source
during a Spark task.

For the maintained distributed estimator, use the
[separate Spark likelihood package](../../packages/spark-likelihood/README.md).
Its primary backend uses PyTorch derivatives inside Spark tasks.

## Source and licenses

The mathematical example and preparation script in this directory are original
and MIT-licensed, as specified in `LICENSE`. The downloaded TMBad dependency
retains TMB's GPL-2 terms; the complete pinned source archive, package description
and license are retained, along with the Eigen source and license notices, under `/opt/native-ad/vendor` in the built image.
The primary Python package does not depend on this optional experiment.

Primary references:
[TMB source](https://github.com/kaskr/adcomp),
[TMBad function-object API](https://github.com/kaskr/adcomp/blob/master/TMB/inst/include/TMBad/TMBad.hpp),
and the [native-modeling research report](../../docs/research/brad-bell-autodiff.md).
