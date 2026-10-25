# GPU computing, CUDA and accelerated data workflows

Open **GPU computing: CUDA, Python, machine learning and Spark** in the unified
`/classroom`. The path has 128 chapters and flexible language/framework variants.
There is no daily deadline and no requirement to own an NVIDIA GPU to read,
save reasoning or run the bounded CPU models.

## Choose a route

Start with cuda-001 through cuda-008 for the common hardware, software, memory,
numerical and performance foundations. Then choose:

- **CUDA C++:** cuda-009 through cuda-064, including compilation, ownership,
  kernels, synchronization, numerical libraries, profiling and advanced projects.
- **Python and ML:** cuda-065 through cuda-112, including CuPy, kernel concepts,
  interoperability, PyTorch, TensorFlow, attention, fine-tuning and deployment.
- **GPU Spark:** cuda-113 through cuda-128, connecting the existing Scala/Spark
  route to the RAPIDS Accelerator, also documented as the cuDF plugin for
  Apache Spark. Learn supported query acceleration, CPU fallback boundaries,
  plans, transfers, scheduling, memory, shuffle, skew and qualification.

Follow each chapter's direct prerequisites. Python users do not need to finish
all C++ chapters before the first tensor lesson. Spark users can enter after
the shared GPU foundation and the relevant existing Spark preparation.

## What the classroom actually runs

The default reading workspace saves a worksheet and notes. **CPU model**
variants run small mathematical or semantic references in Python Core. Selected
framework and Spark variants use the ordinary CPU workers and retain that
evidence label. These calculations do not simulate GPU timing or prove that a
CUDA kernel is correct.

Selected units also provide complete, bounded NVIDIA GPU examples. Their
optional workers require explicit device selection and pass an actual
allocate/compute/synchronize/readback probe before the Run button becomes ready.
See [CUDA platform setup](../../docs/cuda-classroom.md). macOS learners use the
CPU route locally; Metal, ROCm and other GPU backends are separate software and
hardware choices, not CUDA emulation supplied by Docker.

Multi-file extensions, long training, profiler tools, GPU Spark clusters and
multi-GPU projects have explicit external preparation instructions. The single
pad does not silently create infrastructure, download models or execute a
multi-file project. A saved classroom draft is different from a model-training
checkpoint, and neither preserves a live GPU context through a container stop.

## Study and evidence

Every guide includes explanations, worked examples, distinct practice tasks,
expected observations and separate explanations/reference sources. Record what
was read, calculated on a CPU, compiled, executed on a GPU or measured on actual
hardware. Compare supported input contracts and numerical tolerances before
comparing performance. A library baseline is a useful engineering choice even
when a handwritten kernel does not beat it.

The local fixtures are original, small and offline. External libraries and
hardware-specific features are linked to their primary documentation, with
release and platform limits explained in the corresponding guide.

## Maintain the subject

The durable authoring sources live in `authoring/`. Regenerate their owned
content first, then assemble the complete track with:

```sh
python courses/cuda/authoring/cpp_content.py
python courses/cuda/authoring/python_generate.py
python courses/cuda/authoring/build_catalog.py
python scripts/check_modules.py
```

Inspect each generator's `--help` and authoring README for checks. Preserve
stable IDs, CPU/GPU evidence distinctions and separate variant pads. Format
generated executable sources through the shared formatter, then refresh readers.
Never invent a GPU execution receipt from compilation or CPU checks.
