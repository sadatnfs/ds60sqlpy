# CUDA architecture and C++ study workflow

The 64 chapters in this branch run from GPU mental models to kernels, numerical
engineering, profiling, asynchronous pipelines, libraries and independent
projects. Open the CUDA subject in the single `/classroom` interface. Its default
reading worksheet saves your explanation, notes and progress on every supported
classroom host. GPU availability never blocks reading.

## What each learning surface establishes

| Surface | Available work | What it does not establish |
| --- | --- | --- |
| Reading worksheet | Architecture diagrams, exact arithmetic, dependency/lifetime analysis and design decisions | Device execution or hardware performance |
| CPU Python reference | Standard-library calculations with real assertions | CUDA scheduling, memory visibility, instruction timing or GPU execution |
| CUDA compilation | A toolkit accepts a source/target configuration and produces an artifact | Device availability or correct returned values |
| Actual NVIDIA run | Checked allocation, launch, completion and host validation on a named device | Universal correctness, every architecture or a speedup |
| Sanitizer/profiling | Tool-specific observations on a stated fixture and configuration | Every possible defect or a universally optimal implementation |

Apple Silicon, AMD/Intel GPU and CPU-only learners can complete reading and CPU
work. A Docker image cannot manufacture an NVIDIA GPU. Optional GPU work needs a
separately prepared supported NVIDIA Linux host or supported Windows WSL 2 setup.
Use [the classroom GPU guide](../../../docs/cuda-classroom.md) for platform and
profile details. Other GPU APIs, such as Metal/MPS or ROCm, are separate optional
learning environments and do not execute these `.cu` programs automatically.

## Run a bounded CPU reference

Every chapter links its own `references/cuda-NNN_cpu.py`. It uses the Python
standard library and no package/model downloads. In a prepared Python shell,
from the repository root:

```sh
python courses/cuda/cpp/references/cuda-020_cpu.py
```

Select **CPU model (Python)** inside the CUDA chapter to keep practice source
and results scoped to that lesson. Its starter is deliberately incomplete;
implement the model and boundary assertions before replacing its error. You can
explicitly reveal the separate reference for comparison. Assertions
check the exact small model, and the output identifies its surface in the guide.
Hypothetical hardware parameters and synthetic timing samples are labelled as
models, not measured benchmark results. Retain the worksheet as your own work;
viewing an answer should not replace your saved source or mark mastery.

## Optional single-source CUDA C++ lab

Complete `.cu` references accompany cuda-012, cuda-014, cuda-015, cuda-020,
cuda-022, cuda-023, cuda-039 and cuda-043. Separate learner harnesses have the
same IDs under `lessons/`. They intentionally report incomplete work until you
implement the bounded algorithm and checks. The reference does not substitute
CPU arithmetic when a device is absent.

If the classroom offers the optional NVIDIA CUDA C++ variant, select it only
after its runtime capability notice confirms readiness. Its one-source worker
stages the selected source as `main.cu`; the original checked-in filename is not
an executable path. The worker's reviewed compiler flags and bounded job policy
are described in the GPU guide. Your worksheet and each language variant retain
separate saved work.

For a deliberate external lab, use an owned scratch directory on a supported
NVIDIA host with a compatible CUDA toolkit, host compiler and driver already
prepared. The following Bash commands copy only this project's one lesson file
and compile it locally. Run from the repository root. This directory is learner
scratch and must not be committed with experiment logs or personal machine data.

```sh
mkdir -p .learning/cuda-cpp/cuda-020
cp courses/cuda/cpp/references/cuda-020_gpu.cu .learning/cuda-cpp/cuda-020/main.cu
cd .learning/cuda-cpp/cuda-020
nvcc -std=c++17 -O2 -lineinfo main.cu -o main
./main
```

The input `main.cu` contains host code, kernels and `main`. `-o main` names the
compiled host executable; `./main` runs it from this directory. These examples
use C++17-compatible language features. The classroom can deliberately compile
them under its supported newer standard. The manual command uses the toolkit's
default architecture target; confirm that it supports your actual device.
A production binary needs an explicitly reviewed architecture/PTX policy, not a
copied target value from an unrelated GPU.

Success prints the actual CUDA device and reports that host comparisons passed.
No-device, compilation, launch, completion and numerical failures are failures
or unavailable capability, not successful CUDA observations. The fixtures cap
sizes and repetitions; do not replace them with infinite loops or arbitrary
memory exhaustion experiments on a shared or display GPU.

For a separately prepared Compute Sanitizer workflow, run a bounded reference:

```sh
compute-sanitizer --tool memcheck --error-exitcode 99 ./main
compute-sanitizer --tool racecheck --error-exitcode 99 ./main
compute-sanitizer --tool initcheck --error-exitcode 99 ./main
compute-sanitizer --tool synccheck --error-exitcode 99 ./main
```

Each tool has a different scope and overhead. Preserve the diagnostic and exit
status. A clean run is not a speed measurement or a proof about every input.
Do not run deliberate hanging kernels, reset a shared GPU or delete classroom
volumes as an exercise. If device state needs review, the resource owner decides
how to recover it after learner source and observations are preserved.

## Advanced projects and honest scope

The chapters on cuBLAS, cuFFT, cuSPARSE, cuSOLVER, random generators, cooperative
launch, architecture-specific copy mechanisms, CUTLASS, PTX/SASS and multiple
GPUs provide concrete worked models and design practice. Their optional
specialized execution requires its named library, tool or hardware preparation.
The general CUDA C++ pad does not grant arbitrary library installation,
multi-file project builds, profiling permissions or multi-GPU qualification.

cuda-061 explains a larger CMake project as an explicit external workflow.
cuda-063 and cuda-064 ask for a numerical application and a custom ML operator
with evidence-based acceptance. They include CPU baselines and honest decisions
to keep a CPU or library implementation when a custom kernel does not help.

Sources: [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/),
[NVCC reference](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/index.html),
[Compute Sanitizer](https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html).
