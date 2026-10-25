# Learn CUDA with or without an NVIDIA GPU

The CUDA subject has one shared classroom route for GPU architecture, CUDA C++,
Python, PyTorch, TensorFlow and GPU data engineering with Spark. Reading,
mathematical models and bounded CPU implementations are useful on every ordinary
classroom host. Optional NVIDIA profiles add a different execution surface when
compatible hardware is deliberately prepared.

Start with `./classroom` or resume your existing project. Choose **CUDA** from
`/classroom`, open the chapter, and select its reading or **CPU model (Python)**
variant. Each variant keeps its own source and results under the lesson. Reading
notes and progress remain in the same classroom. A saved result does not rerun
code when you revisit it.

## Choose the right platform route

| Host environment | Ordinary classroom learning | Optional GPU route and boundary |
| --- | --- | --- |
| macOS on Apple Silicon | Reading, CPU models and ordinary CPU ML workers | These Linux CUDA workers do not run on Apple GPUs. A separately prepared native PyTorch MPS environment is an external comparison route, not CUDA or Docker GPU qualification. |
| macOS on Intel | Reading, CPU models and supported ordinary Docker profiles | No local CUDA support is promised by this product. Use a separately owned supported NVIDIA machine for actual CUDA experiments. |
| Windows with WSL 2, no supported NVIDIA GPU | Reading, CPU models and ordinary Linux-container profiles | Keep the CPU route. WSL and Docker do not provide missing hardware. |
| Windows with WSL 2 and a supported NVIDIA GPU | All ordinary learning surfaces | Use a supported Windows NVIDIA driver and a Docker engine whose WSL 2 GPU integration actually works. Run classroom commands from the Ubuntu/WSL terminal. |
| Linux x86-64 with a supported NVIDIA GPU | All ordinary learning surfaces | Prepare the host driver and NVIDIA Container Toolkit integration, then explicitly select a GPU and optional profile. |
| Linux with AMD/Intel GPU or CPU only | Reading, CPU models and ordinary profiles | ROCm, oneAPI and other backends have different runtime contracts. They do not automatically execute CUDA `.cu` files or qualify these NVIDIA workers. |
| Linux ARM64 with NVIDIA hardware | Reading and supported ordinary profiles | The optional images in this release target `linux/amd64`. ARM GPU targets require their own images, dependency locks and actual qualification; they are not implicitly supported. |

Docker Desktop documents NVIDIA container GPU access on Windows through its WSL
2 backend. Its other accelerator products do not imply that arbitrary CUDA
containers run on Mac. See [Docker GPU support](https://docs.docker.com/desktop/features/gpu/).
For native Apple GPU experimentation, see [PyTorch's MPS backend](https://docs.pytorch.org/docs/stable/notes/mps.html).

The ordinary `--all` selection deliberately excludes the four NVIDIA profiles.
A new learner never needs to download CUDA images to read this subject or run
its CPU models. Optional GPU preparation can be large and takes additional disk,
RAM and device memory; start with one profile and the small provided fixtures.

## Prepare hardware before choosing a GPU profile

On a supported Linux NVIDIA host, follow the distribution-specific
[NVIDIA Container Toolkit installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).
The host needs a working compatible driver and a container runtime configured
to expose the chosen device. Installing a Python package inside an image is not
a substitute for those steps. Verify the exact local engine you intend to use.
Do not switch a classroom to an unrelated remote Docker context to repair a
local failure; the launcher deliberately keeps personal volumes on its local
engine.

On Windows, install the appropriate Windows NVIDIA driver and update WSL 2 as
described in [NVIDIA's WSL guide](https://docs.nvidia.com/cuda/wsl-user-guide/index.html).
The Windows driver supplies the WSL driver interface. Do not install a separate
Linux NVIDIA display/kernel driver inside WSL to replace it. Docker Desktop's
WSL integration is a documented route. Other engines need their own supported
GPU integration and actual device test; ordinary Linux-container compatibility
does not itself establish GPU passthrough.

From the host or WSL terminal appropriate to that setup, inspect the device and
engine before starting a lesson profile:

```sh
nvidia-smi
docker info
docker compose version
```

`nvidia-smi` is a management observation. Its displayed CUDA version is not the
version of every framework or compiler in the image, and it is not a numerical
kernel test. The classroom performs a separate small computation before marking
an optional GPU worker ready.

Choose one device index or UUID that you own or have permission to use. The
examples below use device index `0`. A GPU shared with other work can have
resource contention; a container memory limit does not cap all GPU allocations
or make arbitrary learner kernels a hostile-code sandbox.

## Start one optional profile

Run from the repository root after host preparation. This selects Python Core
for CPU comparisons plus the optional C++ GPU worker, retaining the chosen
project's named learning volumes:

```sh
./classroom --profile cuda-cpp --gpu-device 0 --project ds60-classroom
```

For CuPy-based Python kernels and array work:

```sh
./classroom --profile cuda-python --gpu-device 0 --project ds60-classroom
```

For paired CPU/GPU PyTorch work:

```sh
./classroom --profile llm-torch-cpu --profile pytorch-cuda --gpu-device 0 --project ds60-classroom
```

For paired CPU/GPU TensorFlow work:

```sh
./classroom --profile tensorflow-cpu --profile tensorflow-cuda --gpu-device 0 --project ds60-classroom
```

An explicit profile selection replaces the saved selection, rather than adding
an invisible global preference. Already running unselected workers are not
stopped automatically. Include every profile you intend to resume together.
To retain the full ordinary set and add a CUDA worker, put `--all` before the
additional profile:

```sh
./classroom --all --profile cuda-cpp --gpu-device 0 --project ds60-classroom
```

The selected GPU is saved with this project's launcher settings. Normal starts
reuse existing images and containers. The familiar stop/resume behavior applies:

```sh
./classroom stop --project ds60-classroom
./classroom resume --project ds60-classroom
./classroom status --project ds60-classroom
```

`resume` does not build or pull. Use the ordinary start command to prepare a
missing selected image. Use `--rebuild` deliberately to apply changed code or
configuration. If you change which physical GPU the project should use, make
that change deliberately and review the resulting configuration rather than
expecting an unchanged stopped container to acquire another device.

Use the same `--project` on every command to keep the same volumes and progress.
The `.classroom/<project>/` directory stores launcher preferences; learner code,
notes and history are in named Docker volumes. Retain those volumes when cleaning
images. See [the main startup guide](one-command-classroom.md) for backups and
normal recovery.

## Use an owned NVIDIA machine from a CPU-only laptop

A Mac or other CPU-only learner can use a separately owned NVIDIA Linux machine
without changing the laptop's ordinary classroom. This is an explicit external
workflow. The GPU machine needs its own repository checkout, supported engine,
driver, disk space and qualification. Its progress volumes live on that machine,
so they are separate from the laptop's local learning state.

On the GPU machine, choose a free fixed loopback browser port and start the
selected profile. The example uses 8787; use the same chosen number throughout.

```sh
./classroom --profile cuda-cpp --gpu-device 0 --port 8787 --project ds60-gpu-study --no-browser
```

From the laptop, create an SSH tunnel to that machine using your normal trusted
SSH account. Replace the two uppercase names with your actual SSH user and host;
do not paste private keys or credentials into repository files.

```sh
ssh -N -L 127.0.0.1:8787:127.0.0.1:8787 YOUR_USER@YOUR_GPU_HOST
```

Keep that terminal open and visit `http://127.0.0.1:8787/classroom` locally.
Matching the forwarded and server port preserves the classroom's exact
Host/Origin checks. The application remains bound to the GPU host's loopback
interface; do not publish it on a public interface or weaken request checks to
make tunnelling work. If the local port is already used, choose a free fixed
port on both sides and configure that deliberately before starting.

Stop or resume the GPU classroom on the GPU machine with its same
`--project ds60-gpu-study`. Closing the SSH tunnel only closes browser access;
it does not stop remote containers or transfer their volumes. Back up/export
from the machine that owns the relevant state. This workflow is a user-managed
SSH connection, not automatic cloud provisioning, a remote Docker context or a
claim that the laptop executed CUDA.

## What the four profiles actually run

| Profile | Source staged by the worker | Prepared capability |
| --- | --- | --- |
| `cuda-cpp` | `main.cu` | A fixed NVCC compile command, followed by the resulting executable |
| `cuda-python` | `main.py` | CuPy with its pinned CUDA dependency profile |
| `pytorch-cuda` | `main.py` | Pinned PyTorch and CuPy, explicit CUDA tensors and synchronization |
| `tensorflow-cuda` | `main.py` | Pinned TensorFlow with its CUDA dependencies and explicit GPU placement |

The current CUDA C++ adapter compiles one source as C++20 with `-O1`, line
information and `compute_75`/`sm_75` device code plus PTX. That baseline does not
claim support for pre-7.5 devices or every architecture-specific instruction.
PTX compatibility also depends on the driver. Specialized tensor-core, cluster,
TMA, cooperative launch and multi-GPU exercises need their own feature checks.
The chapter's external single-source example can use C++17-compatible syntax;
its toolkit default target is a separate manual configuration.

The C++/CuPy/PyTorch profiles use the pinned CUDA 12.8.1 development base.
The TensorFlow profile uses a separately pinned CUDA 12.9.1 development base,
aligned with its locked CUDA 12.9 runtime dependency. Inspect the exact image
digests in `compose.modules.yaml` and the mirror configuration when qualifying
a release. Python libraries
are pinned with hashes under `docker/workers/gpu/`. A framework's CUDA runtime
components can differ from the base compiler toolkit, so choose driver support
from the complete profile, not only the image's `nvcc` version. Do not replace
one lock with an unbounded package install inside a running worker. NVIDIA's
[compatibility documentation](https://docs.nvidia.com/deploy/cuda-compatibility/)
explains the additional driver/runtime constraints.

The worker owns compiler arguments and command selection. Learner metadata
cannot supply arbitrary argv, remote endpoints or driver installation commands.
Jobs have fixed selectable total deadlines, bounded output, bounded scratch
storage, private work directories and the existing local trusted-code execution
boundary. These limits do not guarantee recovery from every device hang.
The standard C++ pad is single-source. CMake projects, custom framework extension
builds, arbitrary external libraries, profiler access and distributed jobs need
an explicitly prepared external workflow.

## Readiness and failure behavior

At startup each optional worker performs a small real computation:

- CUDA C++ allocates device storage, launches a kernel, checks completion,
  copies the result back and checks the value.
- CuPy verifies device visibility, performs an array reduction, synchronizes and
  reads back the result.
- PyTorch requires a CUDA build and available device, creates a CUDA tensor,
  synchronizes and checks both CUDA placement and returned value.
- TensorFlow requires a CUDA build and physical GPU, disables soft placement,
  executes on the GPU and checks placement plus returned value.

A missing device, incompatible runtime, failed allocation, failed kernel or
wrong result keeps the worker unavailable. Installing packages, compiling a file
or discovering a device alone does not mark it ready. The ordinary CPU profiles
continue to hide CUDA devices and are not changed into implicit GPU workers.

An ordinary compiler error returns its diagnostic and lets the learner repair
the source. A runtime timeout, cancellation, resource-limit interruption, signal exit or
recognized serious device fault
marks the optional GPU worker as needing owner review and prevents another job
from being submitted to that worker. Its finished receipt remains readable.
Stopping a child process does not prove the device is healthy. The worker never
resets a GPU. Preserve the learner source and diagnostic, inspect the host/device
through its owner's approved procedure, and only then restart the affected
worker or project so its real startup probe runs again. Do not delete learning
volumes or reset unrelated devices as a repair step.

## PyTorch, TensorFlow and Spark are related but distinct

PyTorch and TensorFlow can both run supported tensor operations and ML workloads
on NVIDIA GPUs. The CUDA curriculum connects their tensor placement, gradients,
training loops, precision, profiling and custom-operator contracts to the C++
mechanisms. CPU variants are legitimate implementations and comparisons; their
results are never labelled CUDA execution. TensorFlow's current installation
guide directs modern Windows GPU users to WSL 2 rather than native Windows.
See [TensorFlow installation](https://www.tensorflow.org/install/pip).

RAPIDS is an ecosystem of GPU data-science tools. The **RAPIDS Accelerator for
Apache Spark**, now documented as the cuDF plugin for Apache Spark, accelerates supported parts of Spark SQL/DataFrame execution;
it does not automatically convert every Spark stage, Scala function or Python
UDF into CUDA. A mixed plan can fall back to CPU for unsupported operations.
The dedicated Spark/GPU chapters teach plan inspection, compatibility, resource
assignment, columnar data, partitioning, transfer/spill costs, correctness and
end-to-end benchmarking. Use the plugin's [official documentation](https://docs.nvidia.com/spark-rapids/).

The ordinary Spark workers are CPU baselines. A CUDA Python worker is not a
GPU Spark cluster. Plugin/Scala/Spark/CUDA version compatibility, GPU discovery,
executor resources and actual accelerated-plan evidence require a separately
prepared owned Spark environment. These distributed and multi-GPU labs remain
explicit external workflows; the classroom never receives a Docker socket or
ambient cluster credentials to create them silently.

## Evidence before a GPU release claim

CPU source tests and content checks can validate lesson registration, saved-pad
identity, deterministic CPU models, fixed command selection, readiness failure
handling and quarantine behavior. They cannot qualify actual NVIDIA execution.
On a supported test machine, retain the following distinct observations before
claiming the relevant optional profile works on that configuration:

1. Successful image build for its declared architecture and locked dependencies.
2. Actual worker startup probe and device/runtime identity.
3. Representative reference execution, including awkward sizes and invalid input.
4. Compile or syntax failure with an actionable diagnostic and no false success.
5. Controlled cancellation/timeout behavior, with owner review before reuse.
6. Saved source/results surviving stop/resume and container replacement without
   replaying a historical result.
7. Browser guide, mathematics, syntax highlighting, variant switching and output
   visibility at desktop and narrow widths.
8. Separate sanitizer or profiler evidence for claims that depend on those tools.

The examples are bounded teaching fixtures, not a promise that arbitrary code
cannot affect a shared GPU. No documentation scan, passing CPU test suite or
single reference run proves that every workload, OS, GPU or driver is bug free.
