# CUDA study guide

This guide holds the operating rules that every chapter of **GPU computing: CUDA, Python,
machine learning and Spark** shares. Each chapter links here instead of repeating them, so the
chapter pages can spend their words on their own mechanism, worked cases and exercises. Read it
once before your first chapter and return to a section when a chapter points to it.

## Pacing and routes

The order supports learning at your own pace; a chapter is not a deadline. Allow several
sessions when a hardware experiment is new. Follow each chapter's direct prerequisites rather
than the global numbering: Python and Spark learners do not need every C++ chapter first. The
[track README](README.md) describes the three routes.

Reading and CPU reasoning stay available when NVIDIA hardware is absent. Advanced hardware
features (cooperative launch, clusters, specialized instructions, multi-GPU links) need their
own capability checks and are never prerequisites for opening a chapter.

## How to study a chapter

1. Read the mechanism and key terms, then trace worked example 1 by hand before running
   anything.
2. Use the saved reading worksheet in `/classroom`. The reading pad stores predictions and
   reasoning; it does not execute CUDA, GPU or cluster commands.
3. For the bounded calculation, select the **CPU model (Python)** variant. In the C++ route its
   answer-free starter supplies the literal fixtures and the task contract; in the Python and
   Spark routes it is an editable copy of the chapter's worked program.
4. In a prepared Python environment you can also run the chapter's separate CPU reference from
   the repository root with `python courses/cuda/<route>/references/<chapter>_cpu.py`. Its
   assertions check the stated numerical result or model invariant.
5. Before editing a program, predict its output. After editing, compare the observation with the
   exact contract that changed, and keep the original case as a regression check.
6. Work the six exercises in order, then compare with the separate explanations.

The [CUDA C++ study workflow](cpp/README.md), [Python route notes](python/README.md) and
[Spark route notes](spark/README.md) cover route-specific commands.

## Evidence labels and acceptance

Keep these observations separate, because each establishes something different:

- a reading or hand calculation;
- a CPU model or semantic oracle run;
- a successful compilation or an imported package;
- an actual NVIDIA device execution with validated results;
- a measured duration on named hardware.

A CPU model checks only the named arithmetic, layout, dependency or capability decision. It does
not model GPU scheduling, caches, instruction timing or device memory visibility, and its console
text is never a CUDA execution receipt.

Acceptance rules for every model and reference:

- Integers, shapes and ordering must match exactly.
- Floating-point differences are accepted only where an assertion states an explicit tolerance.
- A printed duration, or any value labeled model, fixture or trace, is model output, not a
  measured GPU benchmark.
- If you change dtype, layout, ordering, batch size or backend, update the acceptance contract
  instead of silently reusing the old observation.

Keep a small evidence table with columns **claim**, **input**, **expected observation**,
**actual observation** and **limit**. An unperformed GPU or cluster experiment stays pending even
when the CPU model is correct.

## Platforms and hardware

The worksheet and CPU models run in the ordinary Linux Docker classroom on macOS, Linux and
Windows using WSL 2. They need no NVIDIA GPU, and their results are labeled CPU models rather
than simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly
prepared GPU runtime. See [CUDA platform setup](../../docs/cuda-classroom.md). An Apple GPU does
not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware
and other vendor backends are separate accelerator routes with their own package and operation
qualification; they are not CUDA evidence. The Linux Docker classroom does not expose native Mac
MPS automatically.

## Safety and records

- Opening a chapter never downloads packages, models or data.
- Do not attach an engine socket, a host Docker socket, ambient cluster credentials, an ambient
  kubeconfig or an arbitrary remote endpoint to a lesson worker.
- Do not install drivers, reset devices or run external jobs to reproduce an exercise.
- Record the actual backend, data shape and dtype, source revision, versions and pending checks.
- A saved completion marker records learning progress, not hardware certification or expert
  mastery.

## Optional native CUDA laboratories

Selected C++ chapters ship a complete GPU reference `.cu` file and a separate GPU learner source.
Both are standalone, use bounded fixtures, check runtime calls and validate results on the host.

- The learner source reports an incomplete implementation until you add the chapter's algorithm
  and assertions. It must never return a fake GPU success on a CPU machine.
- The reference contains an explicit no-device failure, launch and completion checks, and
  returned-value validation.
- Source review and CPU reference checks do not qualify a `.cu` file on your hardware. Keep
  compilation, actual device execution and sanitizer evidence as separate records.
- If the classroom offers the optional CUDA C++ variant, its capability notice must confirm real
  runtime readiness first. The [CUDA C++ study workflow](cpp/README.md) gives the exact compile
  and run paths.
- Diagnosis exercises are reasoning tasks: never deliberately launch a hanging kernel or reset a
  shared GPU to reproduce one.

## Python GPU and framework labs

The **CuPy on NVIDIA CUDA** variants run the real operation in the separately prepared
`cuda-python` profile. They refuse a missing device instead of switching to CPU. Keep inputs
bounded as supplied, inspect the device, synchronize, and compare with the CPU reference. A
successful syntax check on a Mac is not GPU qualification.

Framework chapters offer **PyTorch on CPU**, **TensorFlow on CPU** and separate NVIDIA CUDA
versions. CPU versions force CPU placement; CUDA versions require the named GPU profile and never
fall back silently. Each program uses a tiny deterministic objective, bounded tensors and local
synthetic data, so no model hub or dataset download is triggered. Choose either lane first, then
compare the other with identical mathematical inputs; shape, mode and optimizer rules are checked
per framework. A framework pass establishes only that variant and environment.

Checkpoint demonstrations are in memory. They teach which state must be saved; they do not export
a durable model artifact or preserve an in-flight device context. Custom operators, distributed
training and engine building remain separately prepared external workflows.

## Spark parity and GPU Spark

The **Scala Spark on CPU** and **PySpark on CPU** variants run the same bounded query in the
ordinary `spark-local-scala` and `spark-local-python` workers. Both use explicit schemas, local
fixtures, at most two local threads, a disabled GPU SQL setting and a session stop in a finally
block, and both assert the same expected result. These are CPU Spark observations, not GPU plugin
qualification.

GPU Spark is a separate owned external workflow. Keep the GPU plugin disabled or absent for a
CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a
different condition from having no compatible GPU. For an external GPU comparison, keep the same
relational expressions and expected result, but use a separately reviewed launcher and the
plugin's compatibility matrix rather than turning classroom source into a cluster connection.

## Exercises, hints and solutions

Exercises move from guided reconstruction of the worked examples to changing an input, diagnosing
a defect, testing a boundary and transferring the idea. For each one, keep the calculation,
output, diagram or failure policy you produce so another reader can compare it with the worked
cases. Record which evidence surface supports your answer (reading, CPU reference or actual
NVIDIA execution) and what it does not establish.

Use one hint at a time. If a hint is not enough, reread the mechanism and the bounded CPU
assertion. Open the separate solution only after a recorded attempt or a deliberate reveal. A
complete explanation names its inputs, the unchanged mathematical contract, the changed boundary
or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline
even after a GPU path becomes available.

## Retrieval and review

A correct tiny example is not a general implementation. After each chapter, explain the first
worked example without its code, state one assumption the second example changes, and explain an
unexpected result before trying random configuration changes. When a failure appears, preserve
the original input and the stage where behavior diverged, and compare with the CPU model before
changing hardware configuration.

## Documentation and sources

Use the documentation that matches your prepared toolkit, driver, framework or plugin release
before any optional hardware execution. Each chapter lists primary references that describe
interfaces and supported boundaries; its synthetic examples and CPU models are original teaching
material. Python, framework and Spark chapters cite the one route reference closest to their
topic; the complete route lists follow.

Array chapters:

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Kernel chapters:

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)
- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Interoperability chapters:

- [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html)
- [CuPy interoperability](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)

Framework chapters:

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

GPU Spark chapters:

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

## Asking an AI tutor

Each chapter ends with a tutor prompt. Ask for one progressive hint at a time, keep the separate
solution closed until you request comparison, and treat CPU models and synthetic timings as model
evidence. The tutor should not install drivers, download packages, run external jobs, reset
devices or change saved work without your instruction.
