# JAX: numerical functions to independent scientific work

This subject contains a complete CPU learning route with 31 executable units and three reading units for optional accelerator, distributed and kernel work. It covers array contracts, functional state, random keys, pytrees, differentiation, compilation, vectorization, training, scientific computation and measured resource tradeoffs. Its capstones require independently explained numerical evidence; a lesson count or reference run does not establish expertise.

Use the **JAX** subject in the shared `/classroom` interface. Runnable units use the separately prepared `jax-cpu` profile with JAX/JAXLIB 0.12.0.1 and NumPy. Read the [classroom instructions](../../docs/one-command-classroom.md) and [runtime contracts](../../docs/modules-runtime.md) for preparation and execution boundaries. The ordinary route uses Linux containers, including on macOS and Windows through WSL 2. No host JAX installation, model download or external account is required for the CPU course.

No previous JAX knowledge is assumed. Learners should be able to trace a Python function and a small array calculation. The opening units review those contracts. Existing preparation includes `python-05`, `python-10`, `python-13`, `python-16`, `python-numpy-01`, `python-numpy-02` and `python-33`; use the classroom catalog to revisit those units as needed. The [statistics book](../statistics-ml/README.md), [PyTorch route](../deep-learning-pytorch/README.md) and [TensorFlow route](../deep-learning-tensorflow/README.md) provide related mathematical and framework explanations.

| Units | Capability developed |
| --- | --- |
| [001](guides/jax-001.md) through [006](guides/jax-006.md) | Numerical contracts, axes, dtypes, explicit state, typed random keys and pytrees |
| [007](guides/jax-007.md) through [012](guides/jax-012.md) | Scalar gradients, JVP/VJP, curvature, JIT, structured control flow and vectorization |
| [013](guides/jax-013.md) through [018](guides/jax-018.md) | Stable masked losses, optimizers, neural training, dropout, continuation and debugging |
| [019](guides/jax-019.md) through [024](guides/jax-024.md) | Linear solves, simulation error, Monte Carlo sensitivity, custom derivatives, implicit differentiation and compiler-stage inspection |
| [025](guides/jax-025.md) through [029](guides/jax-029.md) | Completed-work timing, recomputation/donation, one-device placement, collective mathematics and attention/LoRA porting |
| [030](guides/jax-030.md) and [031](guides/jax-031.md) | A checked numerical component and a reproducible training comparison |
| [032](guides/jax-032.md) through [034](guides/jax-034.md) | Optional GPU/TPU, multi-host and custom-kernel qualification contracts |

Each executable guide contains two complete worked programs and six distinct practice tasks with expected observations and progressive hints. The separate learner scaffold leaves the tasks unimplemented. The executable reference checks the worked and practice cases; the explanatory reference connects each result to its mathematical or state contract. Work through the prediction and derivation before comparing your own attempt with a reference.

The examples deliberately enable X64 at program startup for their small numerical checks. This differs from JAX's usual 32-bit default and is stated in every runnable guide. Precision, tolerance and the actual dtype are part of the evidence, not interchangeable labels.

Every Run starts a fresh Python process. Parameters, keys and in-memory compiled functions do not survive it. Warm-call timing is measured within a single program. Temporary checkpoint files demonstrate a bounded local round trip and are removed after the Run; arbitrary model files and profiler traces are not exported through the ordinary source pad. A durable checkpoint, interactive trace or multi-file project needs an explicitly prepared artifact workflow.

The one-device and named-mapped-axis examples execute real CPU calculations. They do not establish physical multi-device communication, accelerator scaling or multi-host recovery. Optional systems chapters are reading-only. Actual GPU, TPU, distributed and custom-kernel claims require their separately prepared resources and qualified execution. The [CUDA route](../cuda/README.md) supplies related architecture and device-methodology material without becoming a prerequisite for CPU JAX work.

[Authoring ownership](authoring/README.md) describes durable sources and subject-only generation. Runtime integration, shared readers and release checks have separate owners.
