# Original C++ model-authoring API probes

These five small source files independently implement the patterns taught in
chapters 41-48. They are separate from the frozen nine-model likelihood project.
They use documented TMB interfaces and copy no third-party implementation code.

`check.R` copies the five allowlisted sources into an explicitly selected owned
scratch directory, compiles them serially under TMB1.9.25/CppAD and compares their
values, gradients and selected Hessian results with independent dense formulas.
Run only in an already prepared native Linux TMB environment with a compiler:

```bash
Rscript --vanilla check.R "$PWD" /tmp/tmb-cpp-api-owned-build
```

Preparation and execution are not an ordinary R-pad operation. Keep the scratch
directory disposable and separate from learner state. Source presence does not
establish a compiler pass. The track qualification ledger records whether this
exact source was actually executed on an architecture. No TMBad, GPU, specialized
SuiteSparse or large-scale performance claim follows from these tiny probes.

## Run from Docker on Linux, macOS or Windows through WSL 2

After building the owned TMB image described by the main project, start from the
repository root and create a separate local build-output directory:

```bash
mkdir -p .classroom-projects/tmb-cpp-api
docker run --rm --network none --cpus 1 --memory 3g --entrypoint Rscript \
  -v "$PWD/courses/tmb-modeling/projects/tmb-cpp-api:/project:ro" \
  -v "$PWD/.classroom-projects/tmb-cpp-api:/build" \
  -w /project ds60-tmb-local:lesson --vanilla check.R /project /build
```

This local folder stores compiled artifacts separately from lesson progress.
The command compiles five known source files and runs their numerical checks;
it does not access a registry, engine socket or existing learner volume. Do not
reuse an unrelated directory as the output mount. Native ARM64 execution has
passed; another architecture requires its own build and receipt.
