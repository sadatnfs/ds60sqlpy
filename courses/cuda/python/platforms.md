# Choose an execution route honestly

| Host or backend | What this course supports by default | What needs separate preparation |
| --- | --- | --- |
| Linux, any CPU | Reading, standard-library CPU models and prepared CPU framework/Spark workers | NVIDIA GPU worker plus compatible driver/device runtime for CUDA |
| Windows with WSL 2 | The same Linux Docker classroom and saved progress | Supported NVIDIA Windows driver and WSL GPU exposure for CUDA |
| macOS, including Apple Silicon | The same CPU Docker classroom, diagrams, references and worksheets | A separately owned NVIDIA Linux host for CUDA; native MPS is a different backend |
| Supported AMD GPU host | CPU classroom and backend-neutral theory | Release-matched ROCm/framework environment; CUDA kernels are not automatically portable |
| Other accelerator backends | CPU classroom and numerical reference route | Vendor-supported framework/package and operation qualification |

CUDA is NVIDIA's programming platform. Installing a compiler or a Docker image
on non-NVIDIA hardware does not create a CUDA device. Some frameworks support
other backends, but package, operator, dtype and performance behavior differ.
PyTorch's ROCm build intentionally reuses much of the `torch.cuda` API namespace;
that spelling alone does not prove NVIDIA execution. Our explicitly named CUDA
variants reject a ROCm build rather than mislabel it.

PyTorch MPS is a native macOS backend using Apple's Metal ecosystem. A Linux
container on a Mac does not inherit that native API merely because the host has
an Apple GPU. TensorFlow's platform GPU options and third-party plugins have
their own support and maintenance status. Do not present a DirectML or Metal
plugin as a universal replacement for a current supported CUDA installation.
Check the current primary installation documentation before choosing an optional
backend, and retain the CPU route whenever hardware is unavailable.

For NVIDIA WSL, follow the host-driver and container-runtime documentation.
Do not independently replace the supplied host GPU driver with a Linux display
driver inside WSL. Container userspace libraries and the host driver are separate
layers. Verify visibility, a small allocation, a completed kernel and readback
before treating a runtime as ready. Driver versions, image architecture and
compute capability must be recorded, not guessed from a package import.

A remote GPU option means an explicitly owned, separately prepared machine or
service. This release does not let lesson metadata choose arbitrary remote
endpoints or carry credentials. Use a deliberate external terminal workflow and
bring back a sanitized evidence report. Keep classroom progress and source
separate from remote model artifacts and cluster credentials.

## Evidence labels

1. **Reading:** a written explanation or trace.
2. **CPU reference:** a mathematical or semantic oracle executed on CPU.
3. **Compilation:** source accepted for a declared target, without runtime proof.
4. **GPU correctness:** real-device execution and accepted output for stated cases.
5. **GPU performance:** synchronized measurements with workload and environment.
6. **Distributed acceptance:** actual owned multi-device/host execution, failure
   behavior and recovery, qualified separately from single-device correctness.

A saved result should retain its actual category. A CPU reference can be fully
correct and useful while GPU evidence remains pending. A successful single-GPU
kernel does not prove distributed training, GPU Spark, another driver, another
architecture or a beginner's installation on a different operating system.

Primary references: [PyTorch HIP semantics](https://docs.pytorch.org/docs/2.9/notes/hip.html),
[PyTorch MPS](https://docs.pytorch.org/docs/2.9/notes/mps.html),
[TensorFlow installation](https://www.tensorflow.org/install/pip),
[CUDA on WSL](https://docs.nvidia.com/cuda/wsl-user-guide/index.html),
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).
